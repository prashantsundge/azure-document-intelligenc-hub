import argparse
import json
from pathlib import Path

from app.services.language_service import LanguageService


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Enrich Document Intelligence output with Azure AI Language."
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--confirm-cloud-analysis", action="store_true")
    args = parser.parse_args()

    if not args.confirm_cloud_analysis:
        parser.error("Add --confirm-cloud-analysis before sending text to Azure.")

    document = json.loads(args.input.read_text(encoding="utf-8"))
    source_text = document.get("content", "")

    if not source_text.strip():
        raise SystemExit("Input JSON does not contain document content.")

    document["language_enrichment"] = LanguageService().analyze_text(source_text)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2), encoding="utf-8")

    enrichment = document["language_enrichment"]
    print(f"Enrichment complete. Saved result to: {args.output}")
    print(f"Language: {enrichment['detected_language']}")
    print(f"Key phrases: {len(enrichment['key_phrases'])}")
    print(f"Entities: {len(enrichment['entities'])}")
    print(f"PII entities: {len(enrichment['pii_entities'])}")


if __name__ == "__main__":
    main()