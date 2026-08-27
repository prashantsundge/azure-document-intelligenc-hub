
# Azure Document Intelligence Hub

A public, production-style document assistant built with Azure AI services. It extracts information from synthetic business documents, enriches the extracted text, performs hybrid keyword and vector search, and answers questions with grounded citations.

> This project uses only synthetic sample data. Do not upload company, customer, employee, or personal documents.

## Business problem

Organizations store policies, invoices, and operational documents in formats that are difficult to search and analyze. This project demonstrates an Azure-based solution that:

- Extracts document structure, tables, and invoice fields.
- Detects language, key phrases, entities, and PII.
- Redacts PII before searchable content is stored.
- Supports hybrid keyword and vector search.
- Produces grounded RAG answers with document citations.
- Screens user prompts and generated answers with Azure AI Content Safety.
- Runs locally with Docker and is prepared for GitHub CI/CD.

## Architecture

```mermaid
flowchart TB
    User[Public React UI] -->|HTTPS / REST| API[FastAPI API]

    API --> Blob[Azure Blob Storage]
    API --> DI[Azure AI Document Intelligence]
    API --> Language[Azure AI Language]
    API --> Search[Azure AI Search]
    API --> OpenAI[Azure OpenAI]
    API --> Safety[Azure AI Content Safety]

    DI --> Processed[Processed JSON artifacts]
    Language --> Processed
    Processed --> Search

    OpenAI --> Embeddings[text-embedding-3-small]
    OpenAI --> Chat[gpt-4.1-mini]

    Search --> RAG[Hybrid retrieval context]
    RAG --> Chat
    Safety --> API