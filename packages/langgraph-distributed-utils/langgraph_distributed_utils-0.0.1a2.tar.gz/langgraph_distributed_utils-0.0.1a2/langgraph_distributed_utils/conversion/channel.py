from collections.abc import Mapping

from langgraph._internal._typing import MISSING
from langgraph.channels.base import BaseChannel, EmptyChannelError
from langgraph.graph.state import Pregel
from langgraph.managed.base import ManagedValue, ManagedValueMapping, is_managed_value

from langgraph_distributed_utils.conversion.value import (
    value_from_proto,
    value_to_proto,
)
from langgraph_distributed_utils.proto import types_pb2


def channel_to_proto(name: str, channel: BaseChannel) -> types_pb2.Channel:
    try:
        get_result = channel.get()
    except EmptyChannelError:
        get_result = MISSING

    return types_pb2.Channel(
        get_result=value_to_proto(name, get_result),
        is_available_result=channel.is_available(),
        checkpoint_result=value_to_proto(name, channel.checkpoint()),
    )


def channels_to_proto(
    channels: Mapping[str, BaseChannel | type[ManagedValue]],
) -> types_pb2.Channels:
    pb = {}
    for name, channel in channels.items():
        if isinstance(channel, BaseChannel):
            pb[name] = channel_to_proto(name, channel)
    return types_pb2.Channels(channels=pb)


def channels_from_proto(
    channels_pb: dict[str, types_pb2.Channel],
    graph: Pregel,
) -> tuple[dict[str, BaseChannel], ManagedValueMapping]:
    channels = {}
    managed = {}
    for k, v in graph.channels.items():
        if isinstance(v, BaseChannel):
            assert k in channels_pb
            channels[k] = revive_channel(v, channels_pb[k])
        elif is_managed_value(v):  # managed values
            managed[k] = v
        else:
            raise NotImplementedError(f"Unrecognized channel value: {type(v)} | {v}")

    return channels, managed


def revive_channel(channel: BaseChannel, channel_pb: types_pb2.Channel) -> BaseChannel:
    val_pb = channel_pb.checkpoint_result
    val = value_from_proto(val_pb)

    return channel.copy().from_checkpoint(val)
