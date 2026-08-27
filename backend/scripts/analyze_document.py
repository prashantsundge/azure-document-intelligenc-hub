import argparse
import json
from pathlib import Path

from azure.core.exceptions import HttpResponseError

from app.services.document_intelligence import DocumentIntelligenceService


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze a synthetic document using Azure Document Intelligence."
    )
    parser.add_argument("--file", type=Path, required=True)
    parser.add_argument(
        "--model",
        choices=["prebuilt-layout", "prebuilt-invoice"],
        default="prebuilt-layout",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/document-analysis.json"),
    )
    parser.add_argument("--confirm-cloud-analysis", action="store_true")
    args = parser.parse_args()

    if not args.confirm_cloud_analysis:
        parser.error("Add --confirm-cloud-analysis before sending a file to Azure.")

    try:
        result = DocumentIntelligenceService().analyze_file(args.file, args.model)
    except HttpResponseError as error:
        raise SystemExit(f"Azure analysis failed: {error.message}") from error

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"Analysis complete. Saved result to: {args.output}")
    print(f"Pages: {result['page_count']}")
    print(f"Tables: {len(result['tables'])}")


if __name__ == "__main__":
    main()