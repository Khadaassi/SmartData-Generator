from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class _GraphState(TypedDict):
    message: str


def _greet(state: _GraphState) -> _GraphState:
    return {"message": f"Hello, {state['message']}!"}


def test_langgraph_compiles_and_runs():
    graph = StateGraph(_GraphState)
    graph.add_node("greet", _greet)
    graph.add_edge(START, "greet")
    graph.add_edge("greet", END)

    compiled = graph.compile()
    result = compiled.invoke({"message": "SmartData Generator"})

    assert result["message"] == "Hello, SmartData Generator!"
