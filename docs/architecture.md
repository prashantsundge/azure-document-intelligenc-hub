# Architecture

## Purpose

Azure Document Intelligence Hub is a public, read-only document assistant for synthetic policies and invoices. It demonstrates extraction, enrichment, hybrid search, grounded RAG, responsible AI controls, container deployment, observability, and secure Azure access patterns.

## Live services

- Public application: https://ca-docintel-web-dev.blackwave-0f15539d.eastus.azurecontainerapps.io
- API documentation: https://ca-docintel-api-dev.blackwave-0f15539d.eastus.azurecontainerapps.io/docs
- API health endpoint: https://ca-docintel-api-dev.blackwave-0f15539d.eastus.azurecontainerapps.io/api/v1/health

## Component diagram

```text
Browser
  |
  | HTTPS
  v
React frontend — Azure Container Apps
  |
  | HTTPS /api/v1
  v
FastAPI backend — Azure Container Apps
  |
  +--> Azure AI Search
  |      Hybrid keyword and vector retrieval
  |
  +--> Azure OpenAI
  |      text-embedding-3-small + gpt-4.1-mini
  |
  +--> Azure AI Content Safety
  |      Prompt and answer screening
  |
  +--> Azure AI Document Intelligence
  |      Layout and invoice extraction
  |
  +--> Azure AI Language
  |      Language, entities, key phrases, PII detection
  |
  +--> Azure Blob Storage
  |      Private synthetic source documents
  |
  +--> Application Insights
         Requests, failures, latency, dependencies and logs

GitHub Actions
  |
  | OIDC federation, no client secret
  v
Azure Container Registry
  |
  v
Azure Container Apps