import base64
import copy
from collections.abc import Sequence
from typing import Any, cast

from google.protobuf.json_format import MessageToDict
from langchain_core.messages import AIMessageChunk, BaseMessage
from langchain_core.messages.utils import convert_to_messages
from langgraph.checkpoint.base import CheckpointMetadata
from langgraph.types import PregelTask, StateSnapshot, StreamMode

from langgraph_distributed_utils import serde
from langgraph_distributed_utils.conversion.config import config_from_proto
from langgraph_distributed_utils.conversion.value import value_from_proto
from langgraph_distributed_utils.proto import runtime_pb2, types_pb2

VAL_KEYS = {"method", "value"}


def deser_vals(chunk: dict[str, Any]):
    return _deser_vals(copy.deepcopy(chunk))


def _deser_vals(current_chunk: Any):
    if isinstance(current_chunk, list):
        return [_deser_vals(v) for v in current_chunk]
    if not isinstance(current_chunk, dict):
        return current_chunk
    if set(current_chunk.keys()) == VAL_KEYS:
        return serde.get_serializer().loads_typed(
            (current_chunk["method"], base64.b64decode(current_chunk["value"]))
        )
    for k, v in current_chunk.items():
        if isinstance(v, dict | Sequence):
            current_chunk[k] = _deser_vals(v)
    return current_chunk


def state_snapshot_from_proto(state_pb: types_pb2.StateSnapshot) -> StateSnapshot:
    return StateSnapshot(
        values=deser_vals(MessageToDict(state_pb.values)),
        next=tuple(state_pb.next),
        config=config_from_proto(state_pb.config),
        metadata=CheckpointMetadata(**MessageToDict(state_pb.metadata)),
        created_at=state_pb.created_at,
        parent_config=config_from_proto(state_pb.parent_config),
        tasks=tuple([pregel_task_from_proto(task_pb) for task_pb in state_pb.tasks]),
        interrupts=tuple(
            [value_from_proto(i_pb.value) for i_pb in state_pb.interrupts]
        ),
    )


def pregel_task_from_proto(task_pb: types_pb2.PregelTask) -> PregelTask:
    return PregelTask(
        id=task_pb.id,
        name=task_pb.name,
        path=tuple(task_pb.path),
        error=value_from_proto(task_pb.error) if task_pb.error is not None else None,
        interrupts=tuple([value_from_proto(i_pb.value) for i_pb in task_pb.interrupts])
        if task_pb.interrupts
        else tuple(),
        state=MessageToDict(task_pb.state) if task_pb.state else None,
        result=MessageToDict(task_pb.result) if task_pb.result else None,
    )


def decode_state_history_response(response: runtime_pb2.GetStateHistoryResponse):
    if not response:
        return

    return [state_snapshot_from_proto(state_pb) for state_pb in response.history]


def decode_state_response(response: runtime_pb2.GetStateResponse):
    if not response:
        return

    return state_snapshot_from_proto(response.state)


def decode_response(response: runtime_pb2.OutputChunk, stream_mode: StreamMode):
    which = response.WhichOneof("message")
    if which == "error":
        raise ValueError(response.error)
    if which == "chunk":
        return decode_chunk(response.chunk, stream_mode)
    if which == "chunk_list":
        return [
            decode_chunk(chunk.chunk, stream_mode)
            for chunk in response.chunk_list.chunks
        ]

    raise ValueError("No stream response")


def decode_chunk(chunk: types_pb2.StreamChunk, stream_mode: StreamMode):
    d = cast(dict[str, Any], deser_vals(MessageToDict(chunk)))
    stream_mode = stream_mode or ()
    mode = d.get("mode")
    ns = d.get("ns")
    # Handle messages mode specifically - we don't always send the stream mode in the chunk
    # Because if user only has 1 mode, we exclude it since it is implied
    if mode == "messages" or (mode is None and "messages" in stream_mode):
        return (ns, extract_message_chunk(d["payload"]))

    # Handle custom mode primitive extraction
    payload = d.get("payload")

    # For custom mode, unwrap primitives from "data" wrapper
    if mode == "custom" or (mode is None and "custom" in stream_mode):
        if isinstance(payload, dict) and len(payload) == 1 and "data" in payload:
            payload = payload["data"]

    # Regular logic for all modes
    if ns:
        if mode:
            return (ns, mode, payload)
        return (ns, payload)
    if mode:
        return (mode, payload)

    return payload


def extract_message_chunk(
    payload: dict[str, Any],
) -> tuple[BaseMessage, dict[str, Any]]:
    """Extract (BaseMessage, metadata) tuple from messages mode payload"""

    # Extract writes from payload and deserialize the message data
    message_data = payload.get("message", {}).get("message", {})
    metadata = payload.get("metadata", {})
    message_type = message_data.get("type", "ai")
    if message_type.endswith("Chunk"):
        message_id = message_data.get("id")
        content = message_data.get("content", "")
        additional_kwargs = message_data.get("additional_kwargs", {})
        usage_metadata = message_data.get("usage_metadata", None)
        tool_calls = message_data.get("tool_calls", [])
        name = message_data.get("name")
        tool_call_chunks = message_data.get("tool_call_chunks", [])
        response_metadata = message_data.get("response_metadata", {})
        if message_type == "AIMessageChunk":
            message = AIMessageChunk(
                content=content,
                id=message_id,
                additional_kwargs=additional_kwargs,
                tool_calls=tool_calls,
                name=name,
                usage_metadata=usage_metadata,
                tool_call_chunks=tool_call_chunks,
                response_metadata=response_metadata,
            )
            return (message, metadata)
        else:
            raise ValueError(f"Unknown message type: {message_type}")

    else:
        return convert_to_messages([message_data])[0], metadata
