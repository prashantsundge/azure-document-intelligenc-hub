import argparse

from app.services.azure_search import AzureSearchService
from app.services.openai_service import AzureOpenAIService


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True)
    args = parser.parse_args()
    query_vector = AzureOpenAIService().create_embedding(args.query)
    
    results = AzureSearchService().search(
        query=args.query,
        query_vector=query_vector,
    )

    print(f"Results: {len(results)}")
    for result in results:
        print(f"\nTitle: {result['title']}")
        print(f"Score: {result['score']}")
        print(f"Excerpt: {result['content'][:250]}")


if __name__ == "__main__":
    main()