from langgraph.types import Durability

from langgraph_distributed_utils.proto import runtime_pb2, types_pb2


def runopts_to_proto(
    stream_mode,
    output_keys,
    interrupt_before,
    interrupt_after,
    durability: Durability | None,
    debug: bool | None,
    subgraphs: bool | None,
) -> runtime_pb2.RunOpts:
    # Prepare kwargs for construction
    kwargs = {}

    if durability is not None:
        kwargs["durability"] = durability

    if debug is not None:
        kwargs["debug"] = debug

    if subgraphs is not None:
        kwargs["subgraphs"] = subgraphs

    if output_keys is not None:
        string_or_slice_pb = None
        if isinstance(output_keys, str):
            string_or_slice_pb = types_pb2.StringOrSlice(
                is_string=True, values=[output_keys]
            )
        elif isinstance(output_keys, list):
            string_or_slice_pb = types_pb2.StringOrSlice(
                is_string=False, values=output_keys
            )

        if string_or_slice_pb is not None:
            kwargs["output_keys"] = string_or_slice_pb

    # Create the RunOpts with initial values
    run_opts = runtime_pb2.RunOpts(**kwargs)

    # Handle repeated fields after construction
    if stream_mode is not None:
        if isinstance(stream_mode, str):
            run_opts.stream_mode.append(stream_mode)
        elif isinstance(stream_mode, list):
            run_opts.stream_mode.extend(stream_mode)

    if interrupt_before is not None:
        run_opts.interrupt_before.extend(interrupt_before)

    if interrupt_after is not None:
        run_opts.interrupt_after.extend(interrupt_after)

    return run_opts
