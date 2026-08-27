import argparse
from pathlib import Path

from app.services.blob_storage import BlobStorageService


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Upload a local synthetic document to Azure Blob Storage or Azurite."
    )
    parser.add_argument("--file", type=Path, required=True, help="Path to the document.")
    parser.add_argument("--document-id", required=True, help="Stable document identifier.")
    parser.add_argument(
        "--confirm-write",
        action="store_true",
        help="Required confirmation before writing to storage.",
    )
    args = parser.parse_args()

    if not args.confirm_write:
        parser.error("Add --confirm-write to upload a document.")

    blob_name = BlobStorageService().upload_file(
        source_file=args.file,
        document_id=args.document_id,
    )

    print(f"Upload successful. Blob name: {blob_name}")


if __name__ == "__main__":
    main()