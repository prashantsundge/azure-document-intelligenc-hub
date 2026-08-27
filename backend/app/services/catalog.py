import json
from pathlib import Path
from typing import Any

from app.models import (
    AnalysisField,
    Citation,
    DocumentDetail,
    DocumentSummary,
    PiiEntity,
    QualityIssue,
    QualityReport,
    SearchResult,
)
from app.services.azure_search import AzureSearchService
from app.services.content_safety import ContentSafetyService
from app.services.openai_service import AzureOpenAIService

DATA_DIRECTORY = Path(__file__).resolve().parents[2] / "data" / "processed"

REMOTE_WORK_POLICY = DocumentDetail(
    id="remote-work-policy",
    title="Northstar Remote Work Policy",
    document_type="Policy",
    language="en",
    description="Synthetic policy describing remote work eligibility and equipment support.",
    tags=["policy", "remote work", "equipment"],
    extracted_text=(
        "Northstar employees may work remotely up to three days per week with manager "
        "approval. The company provides one laptop, one monitor, and a security key. "
        "Employees must complete annual information-security training."
    ),
    key_phrases=["remote work", "manager approval", "security training"],
    entities=["Northstar", "three days per week"],
    image_descriptions=["Illustration of an employee working from home."],
    tables=[
        [
            ["Benefit", "Eligibility"],
            ["Remote work", "Up to three days each week"],
            ["Equipment", "Laptop, monitor, security key"],
        ]
    ],
)


def load_json(filename: str) -> dict[str, Any]:
    return json.loads((DATA_DIRECTORY / filename).read_text(encoding="utf-8"))


def load_invoice_document() -> DocumentDetail | None:
    layout_file = DATA_DIRECTORY / "sample-invoice-layout.json"
    fields_file = DATA_DIRECTORY / "sample-invoice-fields.json"
    enriched_file = DATA_DIRECTORY / "sample-invoice-enriched.json"

    if not layout_file.exists() or not fields_file.exists() or not enriched_file.exists():
        return None

    layout = load_json("sample-invoice-layout.json")
    invoice = load_json("sample-invoice-fields.json")
    enriched = load_json("sample-invoice-enriched.json")

    enrichment = enriched.get("language_enrichment", {})
    extracted_document = invoice.get("documents", [{}])[0]
    fields = extracted_document.get("fields", {})

    analysis_fields = [
        AnalysisField(
            name=name,
            content=value.get("content"),
            value_type=value.get("value_type", "unknown"),
            confidence=value.get("confidence"),
        )
        for name, value in fields.items()
    ]

    quality_data = invoice.get("quality", {})
    quality = QualityReport(
        status=quality_data.get("status", "needs_review"),
        minimum_confidence=quality_data.get("minimum_confidence", 0.80),
        issues=[
            QualityIssue(
                field=issue["field"],
                reason=issue["reason"],
                message=issue["message"],
                confidence=issue.get("confidence"),
            )
            for issue in quality_data.get("issues", [])
        ],
    )

    return DocumentDetail(
        id="sample-invoice",
        title="Northstar Sample Services Invoice",
        document_type="Invoice",
        language=enrichment.get("detected_language", "en"),
        description=(
            "Synthetic invoice analyzed with Azure Document Intelligence "
            "and Azure AI Language."
        ),
        tags=[
            "invoice",
            "finance",
            "document intelligence",
            "language enrichment",
            quality.status,
        ],
        extracted_text=enrichment.get("safe_content", layout.get("content", "")),
        key_phrases=enrichment.get("key_phrases", []),
        entities=[
            f"{entity['text']} ({entity['category']})"
            for entity in enrichment.get("entities", [])
        ],
        pii_entities=[
            PiiEntity(
                text=entity["text"],
                category=entity["category"],
                confidence=entity["confidence"],
            )
            for entity in enrichment.get("pii_entities", [])
        ],
        image_descriptions=[],
        tables=layout.get("tables", []),
        analysis_fields=analysis_fields,
        quality=quality,
    )


def all_documents() -> list[DocumentDetail]:
    documents = [REMOTE_WORK_POLICY]
    invoice = load_invoice_document()

    if invoice:
        documents.append(invoice)

    return documents


def list_documents() -> list[DocumentSummary]:
    return [
        DocumentSummary(
            id=document.id,
            title=document.title,
            document_type=document.document_type,
            language=document.language,
            description=document.description,
            tags=document.tags,
        )
        for document in all_documents()
    ]


def get_document(document_id: str) -> DocumentDetail | None:
    return next(
        (document for document in all_documents() if document.id == document_id),
        None,
    )


def _hybrid_search(query: str) -> list[dict[str, Any]]:
    query_vector = AzureOpenAIService().create_embedding(query)

    return AzureSearchService().search(
        query=query,
        query_vector=query_vector,
    )


def search_documents(query: str) -> list[SearchResult]:
    search_results = _hybrid_search(query)
    results: list[SearchResult] = []

    for search_result in search_results:
        document = get_document(search_result["document_id"])

        if document is None:
            continue

        results.append(
            SearchResult(
                document=DocumentSummary(
                    id=document.id,
                    title=document.title,
                    document_type=document.document_type,
                    language=document.language,
                    description=document.description,
                    tags=document.tags,
                ),
                score=search_result["score"],
                excerpt=search_result["content"][:220],
                page_number=search_result["page_number"],
            )
        )

    return results


def answer_question(question: str) -> tuple[str, bool, list[Citation]]:
    safety_service = ContentSafetyService()
    safety_service.require_safe(question, "question")

    search_results = _hybrid_search(question)

    if not search_results:
        return "I could not find an answer in the supplied public documents.", False, []

    citations = [
        Citation(
            document_id=result["document_id"],
            document_title=result["title"],
            page_number=result["page_number"],
            excerpt=result["content"][:220],
        )
        for result in search_results
    ]

    context = "\n\n".join(
        (
            f"[Document: {result['title']} | Page: {result['page_number']}]\n"
            f"{result['content']}"
        )
        for result in search_results
    )

    answer = AzureOpenAIService().create_grounded_answer(question, context)
    safety_service.require_safe(answer, "generated answer")

    return answer, True, citations