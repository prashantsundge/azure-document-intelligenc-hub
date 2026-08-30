import time
from collections.abc import Callable

from azure.core.exceptions import AzureError
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAIError

from app.config import get_settings
from app.models import (
    AskRequest,
    AskResponse,
    DocumentDetail,
    DocumentSummary,
    HealthResponse,
    MetricsSummary,
    SearchResponse,
)
from app.services.catalog import (
    answer_question,
    get_document,
    list_documents,
    search_documents,
)
from app.services.content_safety import UnsafeContentError
from app.telemetry import configure_telemetry

# Must run before the FastAPI application instance is created below.
configure_telemetry()

settings = get_settings()

app = FastAPI(
    title="Azure Document Intelligence Hub API",
    version="0.1.0",
    description="Portfolio API for a grounded document intelligence assistant.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

metrics = {
    "requests": 0,
    "blocked_requests": 0,
    "total_latency_ms": 0.0,
}


@app.middleware("http")
async def track_request(request: Request, call_next: Callable):
    started_at = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - started_at) * 1000

    metrics["requests"] += 1
    metrics["total_latency_ms"] += elapsed_ms
    response.headers["X-Correlation-ID"] = request.headers.get(
        "X-Correlation-ID", "local-development"
    )
    return response


@app.get("/api/v1/health", response_model=HealthResponse, tags=["Operations"])
async def health() -> HealthResponse:
    return HealthResponse(status="healthy", environment=settings.app_env)


@app.get("/api/v1/documents", response_model=list[DocumentSummary], tags=["Documents"])
async def documents() -> list[DocumentSummary]:
    return list_documents()


@app.get(
    "/api/v1/documents/{document_id}",
    response_model=DocumentDetail,
    tags=["Documents"],
)
async def document_detail(document_id: str) -> DocumentDetail:
    document = get_document(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    return document


@app.get("/api/v1/search", response_model=SearchResponse, tags=["Search"])
async def search(query: str) -> SearchResponse:
    clean_query = query.strip()

    if len(clean_query) < 3:
        raise HTTPException(status_code=422, detail="Search query must contain at least 3 characters.")

    try:
        results = search_documents(clean_query)
    except (AzureError, RuntimeError) as error:
        raise HTTPException(
            status_code=503,
            detail="Azure AI Search is temporarily unavailable.",
        ) from error

    return SearchResponse(query=clean_query, total=len(results), results=results)


@app.post("/api/v1/ask", response_model=AskResponse, tags=["Grounded chat"])
async def ask(payload: AskRequest) -> AskResponse:
    question = payload.question.strip()

    if any(term in question.lower() for term in ["kill", "explosive", "self harm"]):
        metrics["blocked_requests"] += 1
        raise HTTPException(
            status_code=400,
            detail="The question was blocked by the local safety demonstration rule.",
        )

    try:
        answer, grounded, citations = answer_question(question)
    except UnsafeContentError as error:
        metrics["blocked_requests"] += 1
        raise HTTPException(status_code=400, detail=str(error)) from error
    except (AzureError, OpenAIError, RuntimeError) as error:
        raise HTTPException(
            status_code=503,
            detail="An Azure AI dependency is temporarily unavailable.",
        ) from error
    return AskResponse(answer=answer, grounded=grounded, citations=citations)


@app.get("/api/v1/metrics/summary", response_model=MetricsSummary, tags=["Operations"])
async def metrics_summary() -> MetricsSummary:
    request_count = metrics["requests"]
    average_latency = metrics["total_latency_ms"] / request_count if request_count else 0

    return MetricsSummary(
        requests=request_count,
        blocked_requests=metrics["blocked_requests"],
        average_latency_ms=round(average_latency, 2),
    )