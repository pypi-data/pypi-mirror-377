import logging
from collections.abc import Sequence
from contextvars import ContextVar
from typing import Any

import grpc
import orjson
from langchain_core.runnables import RunnableConfig
from langgraph._internal._config import ensure_config
from langgraph.errors import (
    EmptyInputError,
    GraphBubbleUp,
    GraphInterrupt,
    GraphRecursionError,
    ParentCommand,
)
from langgraph.pregel import Pregel
from langgraph.runtime import get_runtime
from langgraph.types import All, Command, Durability, Interrupt, StreamMode
from langgraph.typing import ContextT, InputT
from pydantic import ValidationError

from langgraph_distributed_utils import serde
from langgraph_distributed_utils.conversion.config import (
    config_to_proto,
    context_to_proto,
)
from langgraph_distributed_utils.conversion.orchestrator_response import decode_response
from langgraph_distributed_utils.conversion.runopts import runopts_to_proto
from langgraph_distributed_utils.conversion.value import value_to_proto
from langgraph_distributed_utils.proto import runtime_pb2
from langgraph_distributed_utils.proto.runtime_pb2 import OutputChunk
from langgraph_distributed_utils.proto.runtime_pb2_grpc import LangGraphRuntimeStub

var_child_runnable_config: ContextVar[RunnableConfig | None] = ContextVar(
    "child_runnable_config", default=None
)


def patch_pregel(runtime_client: LangGraphRuntimeStub, logger: logging.Logger):
    async def patched_ainvoke(pregel_self, input, config=None, **kwargs):
        return await _ainvoke_wrapper(
            runtime_client, logger, pregel_self, input, config, **kwargs
        )

    def patched_invoke(pregel_self, input, config=None, **kwargs):
        return _invoke_wrapper(
            runtime_client, logger, pregel_self, input, config, **kwargs
        )

    Pregel.ainvoke = patched_ainvoke  # type: ignore[invalid-assignment]
    Pregel.invoke = patched_invoke  # type: ignore[invalid-assignment]


async def _ainvoke_wrapper(
    runtime_client: LangGraphRuntimeStub,
    logger: logging.Logger,
    pregel_self: Pregel,  # This is the actual Pregel instance
    input: InputT | Command | None,
    config: RunnableConfig | None = None,
    *,
    context: ContextT | None = None,
    stream_mode: StreamMode = "values",
    print_mode: StreamMode | Sequence[StreamMode] = (),
    output_keys: str | Sequence[str] | None = None,
    interrupt_before: All | Sequence[str] | None = None,
    interrupt_after: All | Sequence[str] | None = None,
    durability: Durability | None = None,
    subgraphs: bool | None = None,
    debug: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any] | Any:
    """Wrapper that handles the actual invoke logic."""

    # subgraph names coerced when initializing executor
    graph_name = pregel_self.name

    logger.info(f"SUBGRAPH AINVOKE ENCOUNTERED: {graph_name}")

    # TODO: Hacky way of retrieving runtime from runnable context
    if not context:
        try:
            runtime = get_runtime()
            if runtime.context:
                context = runtime.context
        except Exception as e:
            logger.error(f"failed to retrive parent runtime for subgraph: {e}")

    if parent_config := var_child_runnable_config.get({}):
        config = ensure_config(config, parent_config)

    try:
        # create request
        invoke_request = runtime_pb2.InvokeRequest(
            graph_name=graph_name,
            input=value_to_proto(None, input),
            config=config_to_proto(config),
            context=context_to_proto(context),
            run_opts=runopts_to_proto(
                stream_mode,
                output_keys,
                interrupt_before,
                interrupt_after,
                durability,
                debug,
                subgraphs,
            ),
        )

        # get response - if this blocks, you might need to make it async
        try:
            # Option 1: If runtime_client.Invoke is synchronous and might block:
            import asyncio

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, runtime_client.Invoke, invoke_request
            )

            if response.WhichOneof("message") == "error":
                error = response.error.error

                if error.WhichOneof("error_type") == "graph_interrupt":
                    graph_interrupt = error.graph_interrupt

                    interrupts = []

                    for interrupt in graph_interrupt.interrupts:
                        interrupts.append(
                            Interrupt(
                                value=serde.get_serializer().loads_typed(
                                    (
                                        interrupt.value.base_value.method,
                                        interrupt.value.base_value.value,
                                    )
                                ),
                                id=interrupt.id,
                            )
                        )

                    raise GraphInterrupt(interrupts)

                else:
                    raise ValueError(
                        f"Unknown subgraph error from orchestrator: {error!s}"
                    )

        except grpc.RpcError as e:
            raise parse_error(e)

        # decode response
        return decode_response(response, stream_mode)

    except Exception as e:
        if isinstance(e, grpc.RpcError):
            logger.error(f"gRPC client/runtime error: {e!s}")
        raise e


def _invoke_wrapper(
    runtime_client: LangGraphRuntimeStub,
    logger: logging.Logger,
    pregel_self: Pregel,  # This is the actual Pregel instance
    input: InputT | Command | None,
    config: RunnableConfig | None = None,
    *,
    context: ContextT | None = None,
    stream_mode: StreamMode = "values",
    print_mode: StreamMode | Sequence[StreamMode] = (),
    output_keys: str | Sequence[str] | None = None,
    interrupt_before: All | Sequence[str] | None = None,
    interrupt_after: All | Sequence[str] | None = None,
    durability: Durability | None = None,
    subgraphs: bool | None = None,
    debug: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any] | Any:
    """Wrapper that handles the actual invoke logic."""

    # subgraph names coerced when initializing executor
    graph_name = pregel_self.name

    logger.info(f"SUBGRAPH INVOKE ENCOUNTERED: {graph_name}")

    # TODO: Hacky way of retrieving runtime from runnable context
    if not context:
        try:
            runtime = get_runtime()
            if runtime.context:
                context = runtime.context
        except Exception as e:
            logger.error(f"failed to retrive parent runtime for subgraph: {e}")

    # need to get config of parent because wont be available in orchestrator
    if parent_config := var_child_runnable_config.get({}):
        config = ensure_config(config, parent_config)

    try:
        # create request
        invoke_request = runtime_pb2.InvokeRequest(
            graph_name=graph_name,
            input=value_to_proto(None, input),
            config=config_to_proto(config),
            context=context_to_proto(context),
            run_opts=runopts_to_proto(
                stream_mode,
                output_keys,
                interrupt_before,
                interrupt_after,
                durability,
                debug,
                subgraphs,
            ),
        )

        try:
            response: OutputChunk = runtime_client.Invoke(invoke_request)

            if response.WhichOneof("message") == "error":
                error = response.error.error

                if error.WhichOneof("error_type") == "graph_interrupt":
                    graph_interrupt = error.graph_interrupt

                    interrupts = []

                    for interrupt in graph_interrupt.interrupts:
                        interrupts.append(
                            Interrupt(
                                value=serde.get_serializer().loads_typed(
                                    (
                                        interrupt.value.base_value.method,
                                        interrupt.value.base_value.value,
                                    )
                                ),
                                id=interrupt.id,
                            )
                        )

                    raise GraphInterrupt(interrupts)

                else:
                    raise ValueError(
                        f"Unknown subgraph error from orchestrator: {error!s}"
                    )

        except grpc.RpcError as e:
            # Unified error parsing: prefer JSON envelope; fallback heuristics inside parser.
            raise parse_error(e)

        # decode response
        return decode_response(response, stream_mode)

    except Exception as e:
        if isinstance(e, grpc.RpcError):
            logger.error(f"gRPC client/runtime error: {e!s}")
        raise e


_ERROR_MAP = {
    # Canonical codes
    "GRAPH_RECURSION": GraphRecursionError,
    "GRAPH_BUBBLE_UP": GraphBubbleUp,
    "GRAPH_INTERRUPT": GraphInterrupt,
    "EMPTY_INPUT": EmptyInputError,
    "VALUE_ERROR": ValueError,
    "REMOTE_ERROR": Exception,
    "EXECUTOR_ERROR": Exception,
    "INVALID_UPDATE": ValueError,
    "EXECUTE_TASK": Exception,
    "RUNTIME_ERROR": RuntimeError,
    # Backward/compat names
    "GraphRecursionError": GraphRecursionError,
    "GraphBubbleUp": GraphBubbleUp,
    "GraphInterrupt": GraphInterrupt,
    "ParentCommand": ParentCommand,
    "ValueError": ValueError,
    "EmptyInputError": EmptyInputError,
}


def parse_error(e: grpc.RpcError) -> Exception:
    if (
        (details := getattr(e, "details", None))
        and callable(details)
        and (det := details())
        and isinstance(det, str)
    ):
        return parse_error_detail(det)
    return e


def parse_error_detail(detail: str) -> Exception:
    # First try JSON envelope
    try:
        details = orjson.loads(detail)
        code = details.get("code") or details.get("error")
        exc_type = _ERROR_MAP.get(code) or Exception
        message = details.get("message") or ""
        return exc_type(message)
    except orjson.JSONDecodeError:
        pass

    # Fallback: legacy heuristics for certain server-side validation errors
    lowered = detail.lower()
    if "recursion limit exceeded" in lowered:
        return GraphRecursionError()
    if "invalid context format" in lowered:
        return TypeError("invalid context format")
    if "invalid pydantic context format" in lowered:
        # Attempt to extract trailing JSON error data if present: ": { ... }"
        try:
            import json as _json

            if ": {" in detail:
                json_part = "{" + detail.split(": {", 1)[1]
                error_data = _json.loads(json_part)
                return ValidationError.from_exception_data(
                    error_data.get("title", "ValidationError"),
                    error_data.get("errors", []),
                )
        except Exception:
            # fall through to generic Exception
            pass
    return Exception(detail)


__all__ = [
    "parse_error",
    "patch_pregel",
]
