import re
import time
from operator import add
from typing import Annotated, Any, Literal

from langchain_core.messages import HumanMessage
from langgraph.constants import END, START
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.managed import IsLastStep
from langgraph.types import Command, Send, interrupt
from typing_extensions import TypedDict


class AnyStr(str):
    def __init__(self, prefix: str | re.Pattern = "") -> None:
        super().__init__()
        self.prefix = prefix

    def __eq__(self, other: object) -> bool:
        return isinstance(other, str) and (
            other.startswith(self.prefix)
            if isinstance(self.prefix, str)
            else self.prefix.match(other)
        )

    def __hash__(self) -> int:
        return hash((str(self), self.prefix))


def _AnyIdHumanMessage(content: str = "", **kwargs: Any) -> HumanMessage:
    """Create a human message with an any id field."""
    message = HumanMessage(content=content, **kwargs)
    message.id = AnyStr()
    return message


# Build the graph
def create_example_graph():
    """Create an example graph."""

    # Define the state
    class State(TypedDict):
        messages: Annotated[list[str], add]
        count: int

    # Define nodes
    def agent(state: State) -> dict:
        """Simple agent that processes messages."""
        messages = state.get("messages", [])
        count = state.get("count", 0)

        # Add a response
        new_message = f"Agent processed {len(messages)} messages (count: {count})"

        return {"messages": [new_message], "count": count + 1}

    def tool(state: State) -> dict:
        """Simple tool that modifies state."""
        count = state.get("count", 0)

        return {"messages": [f"Tool executed with count: {count}"], "count": count * 2}

    def should_continue(state: State) -> str:
        """Decide whether to continue to tool or end."""
        count = state.get("count", 0)

        if count < 5:
            return "tool"
        else:
            return "end"

    workflow = StateGraph(State)

    # Add nodes
    workflow.add_node("agent", agent)
    workflow.add_node("tool", tool)

    # Add edges
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges(
        "agent", should_continue, {"tool": "tool", "end": END}
    )
    workflow.add_edge("tool", "agent")

    # Compile with memory
    graph = workflow.compile(name="example")

    return graph


def create_simple_graph():
    """Create a simple linear graph."""

    class SimpleState(TypedDict):
        value: int
        result: str

    def double(state: SimpleState) -> dict:
        """Double the value."""
        value = state.get("value", 1)
        return {"value": value * 2}

    def stringify(state: SimpleState) -> dict:
        """Convert to string."""
        value = state.get("value", 0)
        return Command(
            update={"result": f"The value is: {value}"},
            goto=END if state.get("value", 0) > 10 else "double",
        )

    workflow = StateGraph(SimpleState)
    workflow.add_node("double", double)
    workflow.add_node("stringify", stringify)

    workflow.set_entry_point("double")
    workflow.add_edge("double", "stringify")

    return workflow.compile(name="simple")


def create_single_node_graph():
    """Create a graph with one node"""

    class State(TypedDict):
        value: int
        is_last_step: IsLastStep

    def double(state: State) -> dict:
        """Double the value."""
        value = state.get("value", 0)
        return {"value": value * 2}

    graph = StateGraph(State)
    graph.add_node("double", double)

    graph.set_entry_point("double")

    return graph.compile(name="single_node")


def create_send_graph():
    class Node:
        def __init__(self, name: str):
            self.name = name
            self.__name__ = name

        def __call__(self, state):
            return [self.name]

    def send_for_fun(state):
        return [Send("2", state), Send("2", state)]

    def route_to_three(state) -> Literal["3"]:
        return "3"

    builder = StateGraph(Annotated[list, add])
    builder.add_node(Node("1"))
    builder.add_node(Node("2"))
    builder.add_node(Node("3"))
    builder.add_edge(START, "1")
    builder.add_conditional_edges("1", send_for_fun)
    builder.add_conditional_edges("2", route_to_three)
    graph = builder.compile(name="send")

    return graph


def create_concurrent_sends_graph():
    class Node:
        def __init__(self, name: str):
            self.name = name
            self.__name__ = name

        def __call__(self, state):
            return (
                [self.name]
                if isinstance(state, list)
                else ["|".join((self.name, str(state)))]
            )

    def send_for_fun(state):
        return [Send("2", 1), Send("2", 2), "3.1"]

    def send_for_profit(state):
        return [Send("2", 3), Send("2", 4)]

    def route_to_three(state) -> Literal["3"]:
        return "3"

    builder = StateGraph(Annotated[list, add])
    builder.add_node(Node("1"))
    builder.add_node(Node("1.1"))
    builder.add_node(Node("2"))
    builder.add_node(Node("3"))
    builder.add_node(Node("3.1"))
    builder.add_edge(START, "1")
    builder.add_edge(START, "1.1")
    builder.add_conditional_edges("1", send_for_fun)
    builder.add_conditional_edges("1.1", send_for_profit)
    builder.add_conditional_edges("2", route_to_three)
    graph = builder.compile(name="concurrent_send")

    return graph


def create_send_command_graph():
    class Node:
        def __init__(self, name: str):
            self.name = name
            self.__name__ = name

        def __call__(self, state):
            update = (
                [self.name]
                if isinstance(state, list)
                else ["|".join((self.name, str(state)))]
            )
            if isinstance(state, Command):
                return [state, Command(update=update)]
            else:
                return update

    def send_for_fun(state):
        return [
            Send("2", Command(goto=Send("2", 3))),
            Send("2", Command(goto=Send("2", 4))),
            "3.1",
        ]

    def route_to_three(state) -> Literal["3"]:
        return "3"

    builder = StateGraph(Annotated[list, add])
    builder.add_node(Node("1"))
    builder.add_node(Node("2"))
    builder.add_node(Node("3"))
    builder.add_node(Node("3.1"))
    builder.add_edge(START, "1")
    builder.add_conditional_edges("1", send_for_fun)
    builder.add_conditional_edges("2", route_to_three)
    return builder.compile(name="send_command")


def create_custom_output_graph():
    class State(TypedDict):
        hello: str
        bye: str
        messages: Annotated[list[str], add_messages]

    class Output(TypedDict):
        messages: list[str]

    class StateForA(TypedDict):
        hello: str
        messages: Annotated[list[str], add_messages]

    def node_a(state: StateForA) -> State:
        assert state == {
            "hello": "there",
            "messages": [_AnyIdHumanMessage(content="hello")],
        }

    class StateForB(TypedDict):
        bye: str
        now: int

    def node_b(state: StateForB):
        assert state == {
            "bye": "world",
        }
        return {
            "now": 123,
            "hello": "again",
        }

    class StateForC(TypedDict):
        hello: str
        now: int

    def node_c(state: StateForC) -> StateForC:
        assert state == {
            "hello": "again",
            "now": 123,
        }

    builder = StateGraph(State, output_schema=Output)
    builder.add_node("a", node_a)
    builder.add_node("b", node_b)
    builder.add_node("c", node_c)
    builder.add_edge(START, "a")
    builder.add_edge("a", "b")
    builder.add_edge("b", "c")
    return builder.compile(name="custom_output")


def create_in_one_fan_out_state_graph_waiting_edge():
    def sorted_add(x: list[str], y: list[str] | list[tuple[str, str]]) -> list[str]:
        if isinstance(y[0], tuple):
            for rem, _ in y:
                x.remove(rem)
            y = [t[1] for t in y]
        return sorted(add(x, y))

    class State(TypedDict, total=False):
        query: str
        answer: str
        docs: Annotated[list[str], sorted_add]

    workflow = StateGraph(State)

    @workflow.add_node
    def rewrite_query(data: State) -> State:
        return {"query": f"query: {data['query']}"}

    def analyzer_one(data: State) -> State:
        return {"query": f"analyzed: {data['query']}"}

    def retriever_one(data: State) -> State:
        return {"docs": ["doc1", "doc2"]}

    def retriever_two(data: State) -> State:
        time.sleep(0.1)  # to ensure stream order
        return {"docs": ["doc3", "doc4"]}

    def qa(data: State) -> State:
        return {"answer": ",".join(data["docs"])}

    workflow.add_node(analyzer_one)
    workflow.add_node(retriever_one)
    workflow.add_node(retriever_two)
    workflow.add_node(qa)

    workflow.set_entry_point("rewrite_query")
    workflow.add_edge("rewrite_query", "analyzer_one")
    workflow.add_edge("analyzer_one", "retriever_one")
    workflow.add_edge("rewrite_query", "retriever_two")
    workflow.add_edge(["retriever_one", "retriever_two"], "qa")
    workflow.set_finish_point("qa")

    return workflow.compile(name="in_one_fan_out")


def create_run_from_checkpoint_id_retains_previous_writes():
    class MyState(TypedDict):
        myval: Annotated[int, add]
        otherval: bool

    class Anode:
        def __init__(self):
            self.switch = False

        def __call__(self, state: MyState):
            self.switch = not self.switch
            return {"myval": 2 if self.switch else 1, "otherval": self.switch}

    builder = StateGraph(MyState)
    thenode = Anode()  # Fun.
    builder.add_node("node_one", thenode)
    builder.add_node("node_two", thenode)
    builder.add_edge(START, "node_one")

    def _getedge(src: str):
        swap = "node_one" if src == "node_two" else "node_two"

        def _edge(st: MyState) -> str:
            if st["myval"] > 3:
                return END
            if st["otherval"]:
                return swap
            return src

        return _edge

    builder.add_conditional_edges("node_one", _getedge("node_one"))
    builder.add_conditional_edges("node_two", _getedge("node_two"))
    return builder.compile(name="run_from_checkpoint_id")


def create_simple_multi_edge():
    class State(TypedDict):
        my_key: Annotated[str, add]

    def up(state: State):
        pass

    def side(state: State):
        pass

    def other(state: State):
        return {"my_key": "_more"}

    def down(state: State):
        pass

    graph = StateGraph(State)

    graph.add_node("up", up)
    graph.add_node("side", side)
    graph.add_node("other", other)
    graph.add_node("down", down)

    graph.set_entry_point("up")
    graph.add_edge("up", "side")
    graph.add_edge("up", "other")
    graph.add_edge(["up", "side"], "down")
    graph.set_finish_point("down")

    return graph.compile(name="simple_multi_edge")


def create_interrupt_graph():
    class State(TypedDict):
        steps: Annotated[list[str], add]

    def interruptible_node(state: State):
        first = interrupt("First interrupt")
        second = interrupt("Second interrupt")
        return {"steps": [first, second]}

    builder = StateGraph(State)
    builder.add_node("node", interruptible_node)
    builder.add_edge(START, "node")

    app = builder.compile(name="interrupt_graph")

    return app


def create_concurrent_failure_graph():
    """Graph that starts several nodes concurrently where one raises an error.

    Used to validate runtime coordination when a worker fails while others are running.
    """

    class State(TypedDict):
        out: Annotated[list[str], add]

    def will_fail(state: State):
        # Small delay to ensure overlap with other workers
        time.sleep(0.05)
        raise Exception("boom: expected test failure")

    def slow_ok(name: str):
        def _fn(state: State):
            time.sleep(0.2)
            return {"out": [name]}

        _fn.__name__ = name
        return _fn

    g = StateGraph(State)

    # Add several slow nodes and one failing node to encourage concurrency
    g.add_node("fail", will_fail)
    g.add_node("slow1", slow_ok("slow1"))
    g.add_node("slow2", slow_ok("slow2"))
    g.add_node("slow3", slow_ok("slow3"))

    g.add_edge(START, "fail")
    g.add_edge(START, "slow1")
    g.add_edge(START, "slow2")
    g.add_edge(START, "slow3")

    return g.compile(name="concurrent_failure")


GRAPHS = {
    "example": create_example_graph(),
    "simple": create_simple_graph(),
    "single_node": create_single_node_graph(),
    "send": create_send_graph(),
    "send_command": create_send_command_graph(),
    "custom_output": create_custom_output_graph(),
    "in_one_fan_out": create_in_one_fan_out_state_graph_waiting_edge(),
    "run_from_checkpoint_id": create_run_from_checkpoint_id_retains_previous_writes(),
    "simple_multi_edge": create_simple_multi_edge(),
    "interrupt_graph": create_interrupt_graph(),
    "concurrent_failure_graph": create_concurrent_failure_graph(),
}
