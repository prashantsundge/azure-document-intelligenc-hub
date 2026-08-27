import argparse

from app.services.catalog import answer_question


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--question", required=True)
    parser.add_argument("--confirm-cloud-analysis", action="store_true")
    args = parser.parse_args()

    if not args.confirm_cloud_analysis:
        parser.error("Add --confirm-cloud-analysis before calling the chat model.")

    answer, grounded, citations = answer_question(args.question)

    print(f"\nGrounded: {grounded}")
    print(f"\nAnswer:\n{answer}")
    print("\nCitations:")

    for citation in citations:
        print(f"- {citation.document_title}, page {citation.page_number}")


if __name__ == "__main__":
    main()