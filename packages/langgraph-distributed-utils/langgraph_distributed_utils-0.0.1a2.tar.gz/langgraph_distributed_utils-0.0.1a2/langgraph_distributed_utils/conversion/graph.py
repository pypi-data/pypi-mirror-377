from collections.abc import Sequence
from typing import Any

from google.protobuf.struct_pb2 import Struct
from langgraph.cache.memory import InMemoryCache
from langgraph.graph.state import Pregel, PregelNode

from langgraph_distributed_utils.conversion.channel import channels_to_proto
from langgraph_distributed_utils.conversion.config import config_to_proto
from langgraph_distributed_utils.proto import graph_pb2, types_pb2


def nodes_to_proto(nodes: dict[str, PregelNode]) -> list[graph_pb2.NodeDefinition]:
    return [node_to_proto(k, v) for k, v in nodes.items()]


def node_to_proto(name: str, node: PregelNode) -> graph_pb2.NodeDefinition:
    if isinstance(node.channels, str):
        channels = [node.channels]
    elif isinstance(node.channels, list):
        channels = node.channels
    elif isinstance(node.channels, dict):
        channels = [k for k, _ in node.channels.items()]
    else:
        channels = []
    # TODO cache policy
    return graph_pb2.NodeDefinition(
        metadata=Struct(fields=node.metadata or {}),
        name=name,
        triggers=node.triggers,
        tags=node.tags or [],
        channels=channels,
    )


def trigger_to_nodes_map_to_proto(
    trigger_to_nodes: dict[str, Sequence[str]] | Any,  # Allow Mapping type from graph
) -> dict[str, graph_pb2.TriggerMapping]:
    trigger_map = {}
    for trigger, nodes in trigger_to_nodes.items():
        if isinstance(nodes, dict) and "nodes" in nodes:
            trigger_map[trigger] = graph_pb2.TriggerMapping(nodes=nodes["nodes"])
        elif isinstance(nodes, list):
            trigger_map[trigger] = graph_pb2.TriggerMapping(nodes=nodes)
        else:
            trigger_map[trigger] = graph_pb2.TriggerMapping(nodes=[])
    return trigger_map


def string_or_slice_field_to_proto(
    val: str | Sequence[str] | None,
) -> types_pb2.StringOrSlice | None:
    if val is None:
        return None
    if isinstance(val, str):
        return types_pb2.StringOrSlice(values=[val], is_string=True)
    if isinstance(val, list):
        return types_pb2.StringOrSlice(values=val, is_string=False)
    raise NotImplementedError(f"Cannot extract field value {val} as string or slice")


def cache_type_to_proto(cache: Any) -> str:
    """Extract cache type from a cache object."""
    if cache is None:
        return "unsupported"
    if isinstance(cache, InMemoryCache):
        return "inMemory"
    return "unsupported"


def graph_to_proto(graph: Pregel, name: str | None = None) -> graph_pb2.GraphDefinition:
    """Extract graph information from a compiled LangGraph graph.

    Returns a protobuf message that contains all relevant orchestration information about the graph
    """
    # Handle input_channels and output_channels oneof
    graph_def = graph_pb2.GraphDefinition(
        name=name or str(graph.name),
        channels=channels_to_proto(graph.channels),
        interrupt_before_nodes=list(graph.interrupt_before_nodes),
        interrupt_after_nodes=list(graph.interrupt_after_nodes),
        stream_mode=(
            [graph.stream_mode]
            if isinstance(graph.stream_mode, str)
            else graph.stream_mode
        ),
        stream_eager=bool(graph.stream_eager),
        stream_channels=string_or_slice_field_to_proto(graph.stream_channels),
        step_timeout=float(graph.step_timeout) if graph.step_timeout else 0.0,
        debug=bool(graph.debug),
        # TODO retry policy
        cache=graph_pb2.Cache(
            cache_type=cache_type_to_proto(getattr(graph, "cache", None)),
        ),
        config=config_to_proto(graph.config) if graph.config else None,
        nodes=nodes_to_proto(graph.nodes),
        trigger_to_nodes=trigger_to_nodes_map_to_proto(graph.trigger_to_nodes),
        stream_channels_asis=string_or_slice_field_to_proto(graph.stream_channels_asis),
        input_channels=string_or_slice_field_to_proto(graph.input_channels),
        output_channels=string_or_slice_field_to_proto(graph.output_channels),
    )

    return graph_def
