from typing import Any

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    HnswParameters,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
)
from azure.search.documents.models import VectorizedQuery

from app.config import get_settings


def chunk_text(text: str, chunk_size: int = 180, overlap: int = 30) -> list[str]:
    words = text.split()

    if not words:
        return []

    chunks: list[str] = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)

        if end >= len(words):
            break

        start = end - overlap

    return chunks


class AzureSearchService:
    def __init__(self) -> None:
        settings = get_settings()

        if not settings.azure_search_endpoint or not settings.azure_search_admin_key:
            raise RuntimeError(
                "AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_ADMIN_KEY must be configured."
            )

        if not settings.azure_search_index_name:
            raise RuntimeError("AZURE_SEARCH_INDEX_NAME must be configured.")

        credential = AzureKeyCredential(settings.azure_search_admin_key)

        self.index_name = settings.azure_search_index_name
        self.index_client = SearchIndexClient(
            endpoint=settings.azure_search_endpoint,
            credential=credential,
        )
        self.search_client = SearchClient(
            endpoint=settings.azure_search_endpoint,
            index_name=self.index_name,
            credential=credential,
        )

    def create_or_update_index(self) -> None:
        fields = [
            SimpleField(
                name="id",
                type=SearchFieldDataType.String,
                key=True,
                filterable=True,
            ),
            SimpleField(
                name="document_id",
                type=SearchFieldDataType.String,
                filterable=True,
            ),
            SimpleField(
                name="page_number",
                type=SearchFieldDataType.Int32,
                filterable=True,
            ),
            SearchableField(
                name="title",
                type=SearchFieldDataType.String,
                searchable=True,
            ),
            SearchableField(
                name="content",
                type=SearchFieldDataType.String,
                searchable=True,
            ),
            SearchField(
                name="tags",
                type=SearchFieldDataType.Collection(SearchFieldDataType.String),
                searchable=True,
                filterable=True,
            ),
            SearchField(
                name="content_vector",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=1536,
                vector_search_profile_name="content-vector-profile",
            ),
        ]

        vector_search = VectorSearch(
            algorithms=[
                HnswAlgorithmConfiguration(
                    name="content-hnsw",
                    parameters=HnswParameters(metric="cosine"),
                )
            ],
            profiles=[
                VectorSearchProfile(
                    name="content-vector-profile",
                    algorithm_configuration_name="content-hnsw",
                )
            ],
        )

        index = SearchIndex(
            name=self.index_name,
            fields=fields,
            vector_search=vector_search,
        )

        self.index_client.create_or_update_index(index)

    def upload_chunks(self, chunks: list[dict[str, Any]]) -> None:
        if not chunks:
            return

        result = self.search_client.merge_or_upload_documents(documents=chunks)

        failed = [item for item in result if not item.succeeded]
        if failed:
            failed_keys = ", ".join(item.key for item in failed)
            raise RuntimeError(f"Failed to upload search documents: {failed_keys}")

    def search(
        self,
        query: str,
        query_vector: list[float],
        top: int = 5,
    ) -> list[dict[str, Any]]:
        vector_query = VectorizedQuery(
            vector=query_vector,
            k_nearest_neighbors=top,
            fields="content_vector",
        )

        results = self.search_client.search(
            search_text=query,
            vector_queries=[vector_query],
            select=[
                "id",
                "document_id",
                "page_number",
                "title",
                "content",
                "tags",
            ],
            top=top,
        )

        return [
            {
                "id": item["id"],
                "document_id": item["document_id"],
                "page_number": item["page_number"],
                "title": item["title"],
                "content": item["content"],
                "tags": item.get("tags", []),
                "score": item["@search.score"],
            }
            for item in results
        ]