from collections.abc import Sequence as SequenceType
from typing import Literal, cast

from langgraph.checkpoint.base import (
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
    PendingWrite,
)

from langgraph_distributed_utils.conversion.config import config_from_proto
from langgraph_distributed_utils.conversion.value import (
    value_from_proto,
    value_to_proto,
)
from langgraph_distributed_utils.proto import types_pb2


def checkpoint_from_proto(request_checkpoint: types_pb2.Checkpoint) -> Checkpoint:
    channel_versions = dict(request_checkpoint.channel_versions)
    versions_seen = {
        k: dict(v.channel_versions) for k, v in request_checkpoint.versions_seen.items()
    }

    channel_values = {}
    if request_checkpoint.channel_values:
        channel_values = {
            k: value_from_proto(v) for k, v in request_checkpoint.channel_values.items()
        }

    return Checkpoint(
        v=request_checkpoint.v,
        id=request_checkpoint.id,
        channel_versions=channel_versions,
        channel_values=channel_values,
        versions_seen=versions_seen,
        ts=request_checkpoint.ts,
    )


def checkpoint_to_proto(checkpoint: Checkpoint) -> types_pb2.Checkpoint:
    checkpoint_proto = types_pb2.Checkpoint()
    checkpoint_proto.channel_versions.update(checkpoint["channel_versions"])
    for node, versions_dict in checkpoint["versions_seen"].items():
        checkpoint_proto.versions_seen[node].channel_versions.update(versions_dict)

    return checkpoint_proto


def checkpoint_tuple_from_proto(
    checkpoint_tuple_pb: types_pb2.CheckpointTuple,
) -> CheckpointTuple | None:
    if not checkpoint_tuple_pb:
        return None

    return CheckpointTuple(
        config=config_from_proto(checkpoint_tuple_pb.config),
        checkpoint=checkpoint_from_proto(checkpoint_tuple_pb.checkpoint),
        metadata=checkpoint_metadata_from_proto(checkpoint_tuple_pb.metadata),
        parent_config=config_from_proto(checkpoint_tuple_pb.parent_config),
        pending_writes=pending_writes_from_proto(checkpoint_tuple_pb.pending_writes),
    )


def checkpoint_metadata_from_proto(
    metadata_pb: types_pb2.CheckpointMetadata,
) -> CheckpointMetadata | None:
    if not metadata_pb:
        return None

    return CheckpointMetadata(
        source=cast(Literal["input", "loop", "update", "fork"], metadata_pb.source),
        step=metadata_pb.step,
        parents=cast(dict[str, str], metadata_pb.parents),
    )


def pending_writes_from_proto(
    pb: SequenceType[types_pb2.PendingWrite],
) -> list[PendingWrite] | None:
    if not pb:
        return None

    return [(pw.task_id, pw.channel, value_from_proto(pw.value)) for pw in pb]


def pending_writes_to_proto(
    pb: SequenceType[types_pb2.PendingWrite],
) -> list[PendingWrite] | None:
    if not pb:
        return None

    return [(pw.task_id, pw.channel, value_to_proto(None, pw.value)) for pw in pb]
