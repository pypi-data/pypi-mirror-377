import traceback

from langgraph.errors import GraphBubbleUp, GraphInterrupt
from langgraph.types import Interrupt

from langgraph_distributed_utils import serde
from langgraph_distributed_utils.conversion.value import value_to_proto
from langgraph_distributed_utils.proto import types_pb2


def exception_to_proto(exc: Exception) -> types_pb2.ExecutorError:
    executor_error_pb = None
    if isinstance(exc, GraphInterrupt):
        if exc.args[0]:
            interrupts = [interrupt_to_proto(interrupt) for interrupt in exc.args[0]]
            meth, ser = serde.get_serializer().dumps_typed(
                exc.args[0] if len(exc.args[0]) != 1 else exc.args[0][0]
            )
            interrupts_serialized = types_pb2.SerializedValue(method=meth, value=ser)

            graph_interrupt_pb = types_pb2.GraphInterrupt(
                interrupts=interrupts,
                interrupts_serialized=interrupts_serialized,  # brittle fix
            )
        else:
            graph_interrupt_pb = types_pb2.GraphInterrupt()
        executor_error_pb = types_pb2.ExecutorError(graph_interrupt=graph_interrupt_pb)
    elif isinstance(exc, GraphBubbleUp):
        bubbleup_pb = types_pb2.GraphBubbleUp()
        executor_error_pb = types_pb2.ExecutorError(graph_bubble_up=bubbleup_pb)
    else:
        meth, ser = serde.get_serializer().dumps_typed(exc)
        error_serialized = types_pb2.SerializedValue(method=meth, value=ser)
        exc_type = type(exc)

        base_error_pb = types_pb2.BaseError(
            error_type=getattr(exc_type, "__name__", str(exc_type)),
            error_message=str(exc),
            error_serialized=error_serialized,
        )
        executor_error_pb = types_pb2.ExecutorError(base_error=base_error_pb)
        executor_error_pb.traceback = traceback.format_exc()

    return executor_error_pb


def interrupt_to_proto(interrupt: Interrupt) -> types_pb2.Interrupt:
    return types_pb2.Interrupt(
        value=value_to_proto(None, interrupt.value),
        id=interrupt.id,
    )
