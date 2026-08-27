import argparse
import json
from pathlib import Path

from app.services.catalog import answer_question

EVALUATION_FILE = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "evaluation"
    / "rag_cases.json"
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate grounded RAG answers against a small public test dataset."
    )

    parser.add_argument(
        "--confirm-cloud-analysis",
        action="store_true",
        help="Confirms Azure OpenAI, Azure AI Search, and Content Safety usage.",
    )

    args = parser.parse_args()

    if not args.confirm_cloud_analysis:
        parser.error(
            "Add --confirm-cloud-analysis to run cloud-backed RAG evaluation."
        )

    cases = json.loads(EVALUATION_FILE.read_text(encoding="utf-8"))

    passed = 0

    for case in cases:
        answer, grounded, citations = answer_question(case["question"])
        answer_lower = answer.lower()

        missing_terms = [
            term
            for term in case["expected_terms"]
            if term.lower() not in answer_lower
        ]

        citation_document_ids = {
            citation.document_id
            for citation in citations
        }

        has_expected_citation = (
            case["expected_document_id"] in citation_document_ids
        )

        case_passed = (
            grounded
            and not missing_terms
            and has_expected_citation
        )

        status = "PASS" if case_passed else "FAIL"

        print(f"\n[{status}] {case['id']}")
        print(f"Question: {case['question']}")
        print(f"Answer: {answer}")
        print(
            "Citations: "
            + ", ".join(sorted(citation_document_ids))
        )

        if missing_terms:
            print(f"Missing expected terms: {', '.join(missing_terms)}")

        if not has_expected_citation:
            print(
                "Missing expected citation: "
                f"{case['expected_document_id']}"
            )

        if case_passed:
            passed += 1

    total = len(cases)

    print(f"\nEvaluation summary: {passed}/{total} cases passed.")

    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()