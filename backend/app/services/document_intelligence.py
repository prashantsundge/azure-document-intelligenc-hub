from pathlib import Path
from typing import Any

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import (
    AnalyzeDocumentRequest,
    DocumentContentFormat,
)
from azure.core.credentials import AzureKeyCredential

from app.config import get_settings

MIN_FIELD_CONFIDENCE = 0.80

def build_quality_report(documents: list[dict[str, Any]]) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []

    for document in documents:
        for field_name, field in document["fields"].items():
            confidence = field["confidence"]
            content = field["content"]

            if content is None:
                issues.append(
                    {
                        "field": field_name,
                        "reason": "missing_content",
                        "message": f"{field_name} did not contain an extracted value.",
                    }
                )
            elif confidence is None or confidence < MIN_FIELD_CONFIDENCE:
                issues.append(
                    {
                        "field": field_name,
                        "reason": "low_confidence",
                        "confidence": confidence,
                        "message": (
                            f"{field_name} has confidence {confidence}, "
                            f"below the {MIN_FIELD_CONFIDENCE} review threshold."
                        ),
                    }
                )

    return {
        "status": "needs_review" if issues else "accepted",
        "minimum_confidence": MIN_FIELD_CONFIDENCE,
        "issues": issues,
    }


class DocumentIntelligenceService:
    def __init__(self) -> None:
        settings = get_settings()

        if not settings.document_intelligence_endpoint or not settings.document_intelligence_key:
            raise RuntimeError(
                "DOCUMENT_INTELLIGENCE_ENDPOINT and DOCUMENT_INTELLIGENCE_KEY "
                "must be configured in .env."
            )

        self.client = DocumentIntelligenceClient(
            endpoint=settings.document_intelligence_endpoint,
            credential=AzureKeyCredential(settings.document_intelligence_key),
        )

    def analyze_file(self, source_file: Path, model_id: str) -> dict[str, Any]:
        if not source_file.is_file():
            raise FileNotFoundError(f"File not found: {source_file}")

        with source_file.open("rb") as file_handle:
            poller = self.client.begin_analyze_document(
                model_id,
                AnalyzeDocumentRequest(bytes_source=file_handle.read()),
                output_content_format=DocumentContentFormat.MARKDOWN,
            )

        result = poller.result()

        tables: list[list[list[str]]] = []
        for table in result.tables or []:
            matrix = [["" for _ in range(table.column_count)] for _ in range(table.row_count)]

            for cell in table.cells:
                matrix[cell.row_index][cell.column_index] = cell.content or ""

            tables.append(matrix)
        extracted_documents = []
        for document in result.documents or []:
            fields = {}

            for field_name, field in (document.fields or {}).items():
                fields[field_name] = {
                    "content": field.content,
                    "value_type": str(field.type),
                    "confidence": field.confidence,
                }

            extracted_documents.append(
                {
                    "document_type": document.doc_type,
                    "confidence": document.confidence,
                    "fields": fields,
                }
            )
        quality = build_quality_report(extracted_documents)

        return {
            "model_id": model_id,
            "content": result.content or "",
            "page_count": len(result.pages or []),
            "tables": tables,
            "quality": quality,
            "documents": extracted_documents,
            "paragraphs": [
                {
                    "content": paragraph.content or "",
                    "role": str(paragraph.role) if paragraph.role else None,
                }
                for paragraph in (result.paragraphs or [])
            ],
        }