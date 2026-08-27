import argparse

from app.services.azure_search import AzureSearchService, chunk_text
from app.services.catalog import all_documents
from app.services.openai_service import AzureOpenAIService


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create an Azure AI Search index and upload safe document chunks."
    )

    parser.add_argument(
        "--confirm-write",
        action="store_true",
        help="Confirms that Azure AI Search data may be created or updated.",
    )

    parser.add_argument(
        "--confirm-cloud-analysis",
        action="store_true",
        help="Confirms that Azure OpenAI embeddings may be generated.",
    )

    args = parser.parse_args()

    if not args.confirm_write:
        parser.error(
            "Add --confirm-write before creating or changing Azure AI Search data."
        )

    if not args.confirm_cloud_analysis:
        parser.error(
            "Add --confirm-cloud-analysis to confirm Azure OpenAI embedding usage."
        )

    search_service = AzureSearchService()
    embedding_service = AzureOpenAIService()

    print("Creating or updating Azure AI Search index...")
    search_service.create_or_update_index()

    chunks: list[dict] = []

    for document in all_documents():
        print(f"Creating embeddings for: {document.title}")

        text_chunks = chunk_text(document.extracted_text)

        for chunk_number, text in enumerate(text_chunks, start=1):
            embedding = embedding_service.create_embedding(text)

            chunks.append(
                {
                    "id": f"{document.id}-{chunk_number}",
                    "document_id": document.id,
                    "page_number": 1,
                    "title": document.title,
                    "content": text,
                    "tags": document.tags,
                    "content_vector": embedding,
                }
            )

    print(f"Uploading {len(chunks)} chunks to Azure AI Search...")
    search_service.upload_chunks(chunks)

    print(f"Index ready: {search_service.index_name}")
    print(f"Uploaded {len(chunks)} hybrid-search chunks successfully.")


if __name__ == "__main__":
    main()