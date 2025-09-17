from typing import Any, cast
from uuid import UUID

from google.protobuf.json_format import MessageToDict
from langchain_core.runnables import RunnableConfig
from langgraph._internal._config import _is_not_empty
from langgraph._internal._constants import (
    CONF,
    CONFIG_KEY_CHECKPOINT_ID,
    CONFIG_KEY_CHECKPOINT_MAP,
    CONFIG_KEY_CHECKPOINT_NS,
    CONFIG_KEY_DURABILITY,
    CONFIG_KEY_READ,
    CONFIG_KEY_RESUME_MAP,
    CONFIG_KEY_RESUMING,
    CONFIG_KEY_RUNTIME,
    CONFIG_KEY_SCRATCHPAD,
    CONFIG_KEY_SEND,
    CONFIG_KEY_TASK_ID,
    CONFIG_KEY_THREAD_ID,
)
from langgraph.runtime import Runtime

from langgraph_distributed_utils.conversion.value import (
    value_from_proto,
    value_to_proto,
)
from langgraph_distributed_utils.proto import types_pb2


def config_from_proto(config_proto: types_pb2.RunnableConfig) -> RunnableConfig | None:
    if not config_proto:
        return None

    config = {}

    # Handle tags
    if config_proto.HasField("tags"):
        config["tags"] = list(config_proto.tags.item)

    # Handle metadata
    if config_proto.HasField("metadata"):
        config["metadata"] = MessageToDict(config_proto.metadata)

    # Handle run_name
    if config_proto.HasField("run_name"):
        config["run_name"] = config_proto.run_name

    # Handle max_concurrency
    if config_proto.HasField("max_concurrency"):
        config["max_concurrency"] = config_proto.max_concurrency

    # Handle recursion_limit
    if config_proto.HasField("recursion_limit"):
        config["recursion_limit"] = config_proto.recursion_limit

    # Handle run_id
    if config_proto.HasField("run_id"):
        config["run_id"] = cast(UUID, config_proto.run_id)

    # Handle configurable
    if config_proto.HasField("configurable"):
        config[CONF] = configurable_from_proto(config_proto.configurable)

    return config


def configurable_from_proto(
    configurable_proto: types_pb2.Configurable,
) -> dict[str, Any]:
    configurable = {}

    # Handle resuming
    if configurable_proto.HasField("resuming"):
        configurable[CONFIG_KEY_RESUMING] = configurable_proto.resuming

    # Handle task_id
    if configurable_proto.HasField("task_id"):
        configurable[CONFIG_KEY_TASK_ID] = configurable_proto.task_id

    # Handle thread_id
    if configurable_proto.HasField("thread_id"):
        configurable[CONFIG_KEY_THREAD_ID] = configurable_proto.thread_id

    # Handle checkpoint_id
    if configurable_proto.HasField("checkpoint_id"):
        configurable[CONFIG_KEY_CHECKPOINT_ID] = configurable_proto.checkpoint_id

    # Handle checkpoint_ns
    if configurable_proto.HasField("checkpoint_ns"):
        configurable[CONFIG_KEY_CHECKPOINT_NS] = configurable_proto.checkpoint_ns

    # Handle durability
    if configurable_proto.HasField("durability"):
        configurable[CONFIG_KEY_DURABILITY] = configurable_proto.durability

    # Handle runtime
    # TODO need context schema to create runtime here. Handle to ensure_runtime for now, but only called during executetasks
    if configurable_proto.HasField("runtime"):
        runtime_proto = configurable_proto.runtime
        configurable[CONFIG_KEY_RUNTIME] = {
            "context": MessageToDict(runtime_proto.context.item)
            if runtime_proto.HasField("context")
            else None,
            "previous": value_from_proto(runtime_proto.previous)
            if runtime_proto.HasField("previous")
            else None,
        }

    # Handle checkpoint_map - unpack the map
    if configurable_proto.HasField("checkpoint_map"):
        configurable[CONFIG_KEY_CHECKPOINT_MAP] = dict(
            configurable_proto.checkpoint_map.item
        )

    # Handle resume_map - unpack the map
    if configurable_proto.HasField("resume_map"):
        resume_map_proto = dict(configurable_proto.resume_map.item)
        configurable[CONFIG_KEY_RESUME_MAP] = {
            k: value_from_proto(v) for k, v in resume_map_proto.items()
        }

    # Handle extra - iterate through and put keys/values as is
    if configurable_proto.HasField("extra"):
        extra_map = MessageToDict(configurable_proto.extra)
        configurable.update(extra_map)

    return configurable


def _is_present_and_not_empty(config: RunnableConfig, key: Any) -> bool:
    return key in config and _is_not_empty(config[key])


def config_to_proto(config: RunnableConfig) -> types_pb2.RunnableConfig | None:
    # Prepare kwargs for construction
    if not config:
        return None
    kwargs = {}

    if _is_present_and_not_empty(config, "run_name"):
        kwargs["run_name"] = config["run_name"]

    if _is_present_and_not_empty(config, "run_id"):
        kwargs["run_id"] = str(config["run_id"]) if config["run_id"] else ""

    if _is_present_and_not_empty(config, "max_concurrency"):
        kwargs["max_concurrency"] = int(config["max_concurrency"])

    if _is_present_and_not_empty(config, "recursion_limit"):
        kwargs["recursion_limit"] = config["recursion_limit"]

    # Create the config with initial values
    pb_config = types_pb2.RunnableConfig(**kwargs)

    # Handle collections after construction
    if _is_present_and_not_empty(config, "tags"):
        if isinstance(config["tags"], list):
            pb_config.tags.item.extend(config["tags"])
        elif isinstance(config["tags"], str):
            pb_config.tags.item.append(config["tags"])

    if _is_present_and_not_empty(config, "metadata"):
        pb_config.metadata.update(config["metadata"])

    if _is_present_and_not_empty(config, "configurable"):
        pb_config.configurable.CopyFrom(configurable_to_proto(config["configurable"]))

    return pb_config


RESTRICTED_RESERVED_CONFIGURABLE_KEYS = {
    CONFIG_KEY_SEND,
    CONFIG_KEY_READ,
    CONFIG_KEY_SCRATCHPAD,
}


def configurable_to_proto(configurable: dict[str, Any]) -> types_pb2.Configurable:
    pb_configurable = types_pb2.Configurable()
    extra = {}

    for key, value in configurable.items():
        if key == CONFIG_KEY_RESUMING:
            pb_configurable.resuming = bool(value)
        elif key == CONFIG_KEY_TASK_ID:
            pb_configurable.task_id = str(value)
        elif key == CONFIG_KEY_THREAD_ID:
            pb_configurable.thread_id = str(value)
        elif key == CONFIG_KEY_CHECKPOINT_MAP:
            pb_configurable.checkpoint_map.item.update(cast(dict[str, str], value))
        elif key == CONFIG_KEY_CHECKPOINT_ID:
            pb_configurable.checkpoint_id = str(value)
        elif key == CONFIG_KEY_CHECKPOINT_NS:
            pb_configurable.checkpoint_ns = str(value)
        elif key == CONFIG_KEY_RESUME_MAP:
            resume_map = cast(dict[str, Any], value)
            for k, v in resume_map.items():
                value_proto = value_to_proto(None, v)
                pb_configurable.resume_map.item[k].CopyFrom(value_proto)
        elif key == CONFIG_KEY_RUNTIME:
            pb_configurable.runtime.CopyFrom(runtime_to_proto(value))
        elif key == CONFIG_KEY_DURABILITY:
            pb_configurable.durability = str(value)
        elif key not in RESTRICTED_RESERVED_CONFIGURABLE_KEYS:
            extra[key] = value

    if extra:
        pb_configurable.extra.update(extra)

    return pb_configurable


def runtime_to_proto(runtime: Runtime) -> types_pb2.Runtime:
    proto = types_pb2.Runtime()

    if runtime.previous:
        proto.previous.CopyFrom(value_to_proto(None, runtime.previous))
    if runtime.context:
        proto.context.CopyFrom(context_to_proto(runtime.context))
    return proto


def context_to_proto(context: dict[str, Any] | Any) -> types_pb2.Context | None:
    if context is None:
        return None

    # Convert dataclass or other objects to dict if needed
    if hasattr(context, "__dict__") and not hasattr(context, "items"):
        # Convert dataclass to dict
        context_dict = context.__dict__
    elif hasattr(context, "items"):
        # Already a dict-like object
        context_dict = context
    else:
        # Try to convert to dict using vars()
        context_dict = vars(context) if hasattr(context, "__dict__") else {}

    return types_pb2.Context(item=context_dict)
