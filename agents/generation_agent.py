from functools import lru_cache
from typing import Literal, TypedDict
from uuid import uuid4

from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field, create_model

from domain.generation import GenerationError, GenerationRequest, GenerationResult
from domain.schema import build_entity_model
from infrastructure.llm import get_llm
from infrastructure.logging import get_logger
from prompts.generation import build_generation_prompt
from rag.vectorstore import SearchResult, search

logger = get_logger(__name__)


class GenerationState(TypedDict):
    run_id: str
    request: GenerationRequest
    context: list[SearchResult]
    items: list[dict]
    errors: list[GenerationError]
    status: str


def _retrieve_context(state: GenerationState) -> GenerationState:
    request = state["request"]
    run_id = state["run_id"]
    query = request.context_query or request.entity.name

    logger.info("[%s] recherche RAG entity=%s project_id=%s", run_id, request.entity.name, request.project_id)
    try:
        state["context"] = search(query, project_id=request.project_id, k=5, entity=request.entity.name)
    except Exception as exc:  # noqa: BLE001 — frontière fournisseur (Chroma/Ollama) : toute erreur devient un GenerationError non bloquant
        logger.warning("[%s] RAG indisponible : %s", run_id, exc)
        state["errors"].append(
            GenerationError(
                code="rag_unavailable",
                message=str(exc),
                stage="rag",
                blocking=False,
            )
        )
        state["context"] = []

    return state


def _generate_data(state: GenerationState) -> GenerationState:
    request = state["request"]
    run_id = state["run_id"]

    entity_model = build_entity_model(request.entity)
    batch_model = create_model(
        f"{request.entity.name}Batch",
        __base__=BaseModel,
        items=(list[entity_model], Field(description=f"Liste de {request.count} objets {request.entity.name}.")),
    )

    prompt = build_generation_prompt(request, state["context"])

    logger.info("[%s] génération LLM entity=%s count=%d", run_id, request.entity.name, request.count)
    try:
        structured_llm = get_llm().with_structured_output(batch_model)
        result = structured_llm.invoke(prompt)
    except Exception as exc:  # noqa: BLE001 — frontière fournisseur (Groq) : toute erreur devient un GenerationError bloquant
        logger.error("[%s] échec de la génération : %s", run_id, exc)
        state["errors"].append(
            GenerationError(
                code="llm_generation_failed",
                message=str(exc),
                stage="generation",
                blocking=True,
            )
        )
        state["status"] = "FAILED"
        return state

    items = [item.model_dump() for item in result.items]
    state["items"] = items

    if len(items) != request.count:
        state["errors"].append(
            GenerationError(
                code="incomplete_generation",
                message=f"{len(items)}/{request.count} objets générés.",
                stage="generation",
                blocking=False,
            )
        )

    state["status"] = "SUCCESS"
    return state


def _route_after_generation(state: GenerationState) -> Literal["finalize", "handle_error"]:
    return "handle_error" if state["status"] == "FAILED" else "finalize"


def _finalize(state: GenerationState) -> GenerationState:
    logger.info("[%s] génération terminée avec succès : %d objets", state["run_id"], len(state["items"]))
    return state


def _handle_error(state: GenerationState) -> GenerationState:
    blocking_errors = [error for error in state["errors"] if error.blocking]
    logger.error("[%s] génération en échec : %d erreur(s) bloquante(s)", state["run_id"], len(blocking_errors))
    return state


@lru_cache
def get_generation_graph():
    graph = StateGraph(GenerationState)
    graph.add_node("retrieve_context", _retrieve_context)
    graph.add_node("generate_data", _generate_data)
    graph.add_node("finalize", _finalize)
    graph.add_node("handle_error", _handle_error)

    graph.add_edge(START, "retrieve_context")
    graph.add_edge("retrieve_context", "generate_data")
    graph.add_conditional_edges(
        "generate_data",
        _route_after_generation,
        {"finalize": "finalize", "handle_error": "handle_error"},
    )
    graph.add_edge("finalize", END)
    graph.add_edge("handle_error", END)

    return graph.compile()


def run_generation(request: GenerationRequest) -> GenerationResult:
    run_id = uuid4().hex
    logger.info(
        "[%s] génération démarrée entity=%s project_id=%s count=%d",
        run_id,
        request.entity.name,
        request.project_id,
        request.count,
    )

    initial_state: GenerationState = {
        "run_id": run_id,
        "request": request,
        "context": [],
        "items": [],
        "errors": [],
        "status": "PENDING",
    }

    final_state: GenerationState = get_generation_graph().invoke(initial_state)

    return GenerationResult(
        run_id=run_id,
        status=final_state["status"],
        entity=request.entity.name,
        items=final_state["items"],
        rules_used=[result.text for result in final_state["context"]],
        errors=final_state["errors"],
    )
