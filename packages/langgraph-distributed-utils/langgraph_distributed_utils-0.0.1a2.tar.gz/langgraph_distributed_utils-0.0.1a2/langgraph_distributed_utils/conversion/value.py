from typing import Any, cast

from langgraph._internal._constants import (
    TASKS,
)
from langgraph._internal._typing import MISSING
from langgraph.types import Command, Send

from langgraph_distributed_utils import serde
from langgraph_distributed_utils.proto import types_pb2


def value_from_proto(value: types_pb2.Value) -> Any:
    value_kind = value.WhichOneof("message")
    if value_kind == "base_value":
        return serde.get_serializer().loads_typed(
            (value.base_value.method, value.base_value.value)
        )
    if value_kind == "sends":
        sends = []
        for send in value.sends.sends:
            node = send.node
            arg = value_from_proto(send.arg)
            sends.append(Send(node, arg))
        return sends
    if value_kind == "missing":
        return MISSING
    if value_kind == "command":
        graph, update, resume, goto = None, None, None, ()
        if value.command.graph is not None:
            graph = value.command.graph
        if value.command.update is not None:
            if (
                isinstance(value.command.update, dict)
                and len(value.command.update) == 1
                and "__root__" in value.command.update
            ):
                update = value_from_proto(value.command.update["__root__"])
            else:
                update = {
                    k: value_from_proto(v) for k, v in value.command.update.items()
                }
        if value.command.resume:
            which = value.command.resume.WhichOneof("message")
            if which == "value":
                resume = value_from_proto(value.command.resume.value)
            else:
                resume_map = {
                    k: value_from_proto(v)
                    for k, v in value.command.resume.values.values.items()
                }
                resume = resume_map
        if value.command.gotos:
            gotos = []
            for g in value.command.gotos:
                which = g.WhichOneof("message")
                if which == "node_name":
                    gotos.append(g.node_name.name)
                else:
                    gotos.append(Send(g.send.node, value_from_proto(g.send.arg)))
            if len(gotos) == 1:
                gotos = gotos[0]
            goto = gotos
        return Command(graph=graph, update=update, resume=resume, goto=goto)
    raise NotImplementedError(f"Unrecognized value kind: {value_kind}")


def value_to_proto(channel_name: str | None, value: Any) -> types_pb2.Value:
    if channel_name == TASKS and value != MISSING:
        if not isinstance(value, list):
            if not isinstance(value, Send):
                raise ValueError(
                    "Task must be a Send object objects."
                    f" Got type={type(value)} value={value}",
                )
            value = [value]
        else:
            for v in value:
                if not isinstance(v, Send):
                    raise ValueError(
                        "Task must be a list of Send objects."
                        f" Got types={[type(v) for v in value]} values={value}",
                    )
        return sends_to_proto(value)
    if value == MISSING:
        return missing_to_proto()
    if isinstance(value, Command):
        return command_to_proto(value)
    return base_value_to_proto(value)


def send_to_proto(send: Send) -> types_pb2.Send:
    return types_pb2.Send(
        node=send.node,
        arg=value_to_proto(TASKS if isinstance(send.arg, Send) else None, send.arg),
    )


def sends_to_proto(sends: list[Send]) -> types_pb2.Value:
    if not sends:
        return missing_to_proto()
    pb = []
    for send in sends:
        pb.append(send_to_proto(send))

    return types_pb2.Value(sends=types_pb2.Sends(sends=pb))


def command_to_proto(cmd: Command) -> types_pb2.Value:
    cmd_pb = types_pb2.Command()
    if cmd.graph:
        if not cmd.graph == Command.PARENT:
            raise ValueError("command graph must be null or parent")
        cmd_pb.graph = cmd.graph
    if cmd.update:
        if isinstance(cmd.update, dict):
            for k, v in cmd.update.items():
                cmd_pb.update[k].CopyFrom(value_to_proto(None, v))
        else:
            cmd_pb.update.update({"__root__": value_to_proto(None, cmd.update)})
    if cmd.resume:
        if isinstance(cmd.resume, dict):
            cmd_pb.resume.CopyFrom(resume_map_to_proto(cmd.resume))
        else:
            resume_val = types_pb2.Resume(value=value_to_proto(None, cmd.resume))
            cmd_pb.resume.CopyFrom(resume_val)
    if cmd.goto:
        gotos = []
        goto = cmd.goto
        if isinstance(goto, list):
            for g in goto:
                gotos.append(goto_to_proto(g))
        else:
            gotos.append(goto_to_proto(cast(Send | str, goto)))
        cmd_pb.gotos.extend(gotos)

    return types_pb2.Value(command=cmd_pb)


def resume_map_to_proto(resume: dict[str, Any] | Any) -> types_pb2.Resume:
    vals = {k: value_to_proto(None, v) for k, v in resume.items()}
    return types_pb2.Resume(values=types_pb2.InterruptValues(values=vals))


def goto_to_proto(goto: Send | str) -> types_pb2.Goto:
    if isinstance(goto, Send):
        return types_pb2.Goto(send=send_to_proto(goto))
    if isinstance(goto, str):
        return types_pb2.Goto(node_name=types_pb2.NodeName(name=goto))
    raise ValueError("goto must be send or node name")


def missing_to_proto() -> types_pb2.Value:
    pb = types_pb2.Value()
    pb.missing.SetInParent()
    return pb


def base_value_to_proto(value: Any) -> types_pb2.Value:
    meth, ser_val = serde.get_serializer().dumps_typed(value)
    serialize_value_proto = types_pb2.SerializedValue(method=meth, value=bytes(ser_val))

    return types_pb2.Value(base_value=serialize_value_proto)
