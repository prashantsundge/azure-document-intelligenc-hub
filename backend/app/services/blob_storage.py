"""Azure Blob Storage upload service."""

import mimetypes
from pathlib import Path
from uuid import uuid4

from azure.core.exceptions import ResourceExistsError
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, ContentSettings

from app.config import get_settings


class BlobStorageService:
    """Uploads curated public documents to Azure Blob Storage."""

    def __init__(self) -> None:
        settings = get_settings()

        self.container_name = settings.azure_storage_container_name

        if settings.azure_storage_use_managed_identity:
            if not settings.azure_storage_account_url:
                raise RuntimeError(
                    "AZURE_STORAGE_ACCOUNT_URL is required when "
                    "AZURE_STORAGE_USE_MANAGED_IDENTITY is enabled."
                )

            self.service_client = BlobServiceClient(
                account_url=settings.azure_storage_account_url,
                credential=DefaultAzureCredential(),
            )
        elif settings.azure_storage_connection_string:
            self.service_client = BlobServiceClient.from_connection_string(
                settings.azure_storage_connection_string
            )
        else:
            raise RuntimeError(
                "Configure AZURE_STORAGE_CONNECTION_STRING for Azurite/local development "
                "or enable AZURE_STORAGE_USE_MANAGED_IDENTITY for Azure."
            )

        self.container_client = self.service_client.get_container_client(
            self.container_name
        )

    def ensure_container_exists(self) -> None:
        """Create the container when using local Azurite for the first time."""
        try:
            self.container_client.create_container()
        except ResourceExistsError:
            pass

    def upload_file(self, source_file: str, document_id: str) -> str:
        """Upload a synthetic or openly licensed source document."""
        source_path = Path(source_file)

        if not source_path.is_file():
            raise FileNotFoundError(f"Source file does not exist: {source_path}")

        self.ensure_container_exists()

        blob_name = f"raw/{document_id}/{uuid4()}-{source_path.name}"
        content_type, _ = mimetypes.guess_type(source_path.name)

        with source_path.open("rb") as file_handle:
            self.container_client.upload_blob(
                name=blob_name,
                data=file_handle,
                overwrite=False,
                content_settings=ContentSettings(
                    content_type=content_type or "application/octet-stream"
                ),
            )

        return blob_name