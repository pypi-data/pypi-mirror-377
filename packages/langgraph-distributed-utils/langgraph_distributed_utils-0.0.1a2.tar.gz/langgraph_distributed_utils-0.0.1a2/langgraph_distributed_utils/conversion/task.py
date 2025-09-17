from collections import deque
from collections.abc import Sequence
from collections.abc import Sequence as SequenceType
from dataclasses import is_dataclass
from functools import partial
from typing import Any

from langchain_core.runnables.config import RunnableConfig
from langgraph._internal._config import patch_config
from langgraph._internal._constants import (
    CACHE_NS_WRITES,
    CONF,
    CONFIG_KEY_CHECKPOINT_NS,
    CONFIG_KEY_READ,
    CONFIG_KEY_RESUME_MAP,
    CONFIG_KEY_RUNTIME,
    CONFIG_KEY_SCRATCHPAD,
    CONFIG_KEY_SEND,
    PULL,
    PUSH,
)
from langgraph._internal._scratchpad import PregelScratchpad
from langgraph.checkpoint.base import PendingWrite
from langgraph.pregel import Pregel
from langgraph.pregel._algo import (
    PregelTaskWrites,
    _proc_input,
    _scratchpad,
    local_read,
)
from langgraph.pregel._call import identifier
from langgraph.pregel._read import PregelNode
from langgraph.runtime import DEFAULT_RUNTIME, Runtime
from langgraph.store.base import BaseStore
from langgraph.types import CacheKey, PregelExecutableTask
from pydantic import BaseModel
from xxhash import xxh3_128_hexdigest

from langgraph_distributed_utils.conversion.channel import channels_from_proto
from langgraph_distributed_utils.conversion.checkpoint import pending_writes_from_proto
from langgraph_distributed_utils.conversion.config import config_from_proto
from langgraph_distributed_utils.conversion.value import (
    value_from_proto,
    value_to_proto,
)
from langgraph_distributed_utils.proto import types_pb2


def task_writes_from_proto(
    tasks_proto: SequenceType[types_pb2.Task],
) -> SequenceType[PregelTaskWrites]:
    return [
        PregelTaskWrites(
            tuple(t.task_path),
            t.name,
            [(w.channel, value_from_proto(w.value)) for w in t.writes],
            t.triggers,
        )
        for t in tasks_proto
    ]


def task_writes_to_proto(
    writes: Sequence[tuple[str, Any]],
) -> SequenceType[types_pb2.Write]:
    writes_proto = []
    for channel, val in writes:
        val_pb = value_to_proto(channel, val)
        channel_write = types_pb2.Write(channel=channel, value=val_pb)
        writes_proto.append(channel_write)
    return writes_proto


def pregel_executable_task_from_proto(
    task_proto: types_pb2.Task,
    step: int,
    stop: int,
    channels_proto: types_pb2.Channels,
    graph: Pregel,
    proc: PregelNode,
    *,
    store: BaseStore | None = None,
    config: RunnableConfig | None = None,
    custom_stream_writer=None,
) -> PregelExecutableTask:
    try:
        if config is None:
            config = config_from_proto(task_proto.config)
        configurable = config.get(CONF, {})

        scratchpad = scratchpad_from_proto(config, step, stop, task_proto=task_proto)
        channels, managed = channels_from_proto(
            channels_proto.channels,
            graph,
        )
        if task_proto.task_path[0] == PULL:
            val = _proc_input(
                proc,
                managed,
                channels,
                for_execution=True,
                scratchpad=scratchpad,
                input_cache=None,
            )
        elif task_proto.task_path[0] == PUSH:
            val = value_from_proto(task_proto.input["PUSH_INPUT"])

        writes = deque()
        runtime = ensure_runtime(
            configurable, store, graph, custom_stream_writer=custom_stream_writer
        )

        # Generate cache key if cache policy exists
        cache_policy = getattr(proc, "cache_policy", None)
        cache_key = None
        if cache_policy:
            args_key = cache_policy.key_func(
                *([val] if not isinstance(val, list | tuple) else val),
            )
            cache_key = CacheKey(
                (CACHE_NS_WRITES, identifier(proc.node) or "__dynamic__"),
                xxh3_128_hexdigest(
                    args_key.encode() if isinstance(args_key, str) else args_key,
                ),
                cache_policy.ttl,
            )

        task = PregelExecutableTask(
            name=task_proto.name,
            input=val,
            proc=proc.node,
            writes=writes,
            config=patch_config(
                config,
                configurable={
                    CONFIG_KEY_SEND: writes.extend,
                    CONFIG_KEY_READ: partial(
                        local_read,
                        scratchpad,
                        channels,
                        managed,
                        PregelTaskWrites(
                            tuple(task_proto.task_path)[:3],
                            task_proto.name,
                            writes,
                            task_proto.triggers,
                        ),
                    ),
                    CONFIG_KEY_RUNTIME: runtime,
                    CONFIG_KEY_SCRATCHPAD: scratchpad,
                },
            ),
            triggers=task_proto.triggers,
            id=task_proto.id,
            path=task_proto.task_path,
            retry_policy=proc.retry_policy or [],  # TODO support
            cache_key=cache_key,  # TODO support
            writers=proc.flat_writers,
            subgraphs=proc.subgraphs,
        )
    except Exception as e:
        raise e

    return task


def scratchpad_from_proto(
    config: RunnableConfig,
    step: int,
    stop: int,
    task_proto: types_pb2.Task | None = None,
) -> PregelScratchpad:
    # TODO: We shouldn't be accepting null tasks here actually
    configurable = config.setdefault(CONF, {})
    task_checkpoint_ns: str = configurable.get(CONFIG_KEY_CHECKPOINT_NS) or ""
    if task_proto is not None:
        task_id = task_proto.id
        pending_writes: list[PendingWrite] = (
            (pending_writes_from_proto(task_proto.pending_writes) or [])
            if (
                hasattr(task_proto, "pending_writes")
                and len(task_proto.pending_writes) > 0
            )
            else []
        )
    else:
        task_id = ""
        pending_writes = []

    scratchpad = _scratchpad(
        configurable.get(CONFIG_KEY_SCRATCHPAD),
        pending_writes,
        task_id,
        xxh3_128_hexdigest(task_checkpoint_ns.encode()),
        configurable.get(CONFIG_KEY_RESUME_MAP),
        step,
        stop,
    )

    return scratchpad


def ensure_runtime(
    configurable: dict[str, Any],
    store: BaseStore | None,
    graph: Pregel,
    custom_stream_writer=None,
) -> Runtime:
    runtime = configurable.get(CONFIG_KEY_RUNTIME)

    # Prepare runtime overrides
    overrides = {"store": store}
    if custom_stream_writer is not None:
        overrides["stream_writer"] = custom_stream_writer

    if runtime is None:
        return DEFAULT_RUNTIME.override(**overrides)
    if isinstance(runtime, Runtime):
        return runtime.override(**overrides)
    if isinstance(runtime, dict):
        context = _coerce_context(graph, runtime.get("context"))
        return Runtime(
            **(
                runtime
                | {"store": store, "context": context}
                | (
                    {"stream_writer": custom_stream_writer}
                    if custom_stream_writer
                    else {}
                )
            )
        )
    raise ValueError("Invalid runtime")


def _coerce_context(graph: Pregel, context: Any) -> Any:
    if context is None:
        return None

    context_schema = graph.context_schema
    if context_schema is None:
        return context

    schema_is_class = issubclass(context_schema, BaseModel) or is_dataclass(
        context_schema,
    )
    if isinstance(context, dict) and schema_is_class:
        return context_schema(**_filter_context_by_schema(context, graph))

    return context


_CACHE = {}


def _filter_context_by_schema(context: dict[str, Any], graph: Pregel) -> dict[str, Any]:
    if graph not in _CACHE:
        _CACHE[graph] = graph.get_context_jsonschema()
        if len(_CACHE) > 500:
            _CACHE.popitem()
    json_schema = _CACHE[graph]
    if not json_schema or not context:
        return context

    # Extract valid properties from the schema
    properties = json_schema.get("properties", {})
    if not properties:
        return context

    # Filter context to only include parameters defined in the schema
    filtered_context = {}
    for key, value in context.items():
        if key in properties:
            filtered_context[key] = value

    return filtered_context
