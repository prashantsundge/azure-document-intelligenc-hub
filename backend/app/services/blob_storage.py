from pathlib import Path
from uuid import uuid4

from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobServiceClient, ContentSettings

from app.config import get_settings


class BlobStorageService:
    def __init__(self) -> None:
        settings = get_settings()

        if not settings.azure_storage_connection_string:
            raise RuntimeError(
                "AZURE_STORAGE_CONNECTION_STRING is not configured. "
                "Add it to backend/.env before using Blob Storage."
            )

        self.container_name = settings.azure_storage_container_name
        self.service_client = BlobServiceClient.from_connection_string(
            settings.azure_storage_connection_string
        )
        self.container_client = self.service_client.get_container_client(self.container_name)

    def ensure_container_exists(self) -> None:
        try:
            self.container_client.create_container()
        except ResourceExistsError:
            pass

    def upload_file(self, source_file: Path, document_id: str) -> str:
        if not source_file.is_file():
            raise FileNotFoundError(f"Source file was not found: {source_file}")

        self.ensure_container_exists()

        blob_name = f"raw/{document_id}/{uuid4()}-{source_file.name}"
        content_type = (
            "application/pdf"
            if source_file.suffix.lower() == ".pdf"
            else "text/plain"
            if source_file.suffix.lower() == ".txt"
            else "application/octet-stream"
        )

        with source_file.open("rb") as file_handle:
            self.container_client.upload_blob(
                name=blob_name,
                data=file_handle,
                overwrite=False,
                content_settings=ContentSettings(content_type=content_type),
                metadata={
                    "document_id": document_id,
                    "ingestion_status": "uploaded",
                },
            )

        return blob_name

    def can_connect(self) -> bool:
        self.ensure_container_exists()
        return True