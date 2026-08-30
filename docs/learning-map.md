

```md
# Azure AI learning map

This document maps implemented features to Azure AI engineering concepts.

| Azure AI concept | Evidence in this repository | Demonstrated outcome |
|---|---|---|
| Document Intelligence Layout | `backend/scripts/analyze_document.py` | Extracted text, paragraphs, tables, and page structure |
| Document Intelligence Invoice | `backend/scripts/analyze_document.py` | Invoice ID, vendor, total, payment terms, and confidence values |
| Extraction quality review | `backend/app/services/document_intelligence.py` | Fields below the review threshold are flagged in the UI |
| Azure AI Language | `backend/app/services/language_service.py` | Language detection, entities, key phrases, and PII detection |
| PII-aware indexing | `backend/scripts/enrich_document.py` | Searchable content is prepared after privacy enrichment |
| Azure Blob Storage | `backend/app/services/blob_storage.py` | Synthetic source documents uploaded to a private Blob container |
| Managed identity | `infra/storage.bicep`, `infra/api.bicep` | Container Apps access Blob Storage without shared keys |
| Azure AI Search | `backend/app/services/azure_search.py` | Keyword and vector search over document chunks |
| Chunking | `backend/app/services/azure_search.py` | Large extracted documents become retrieval-sized chunks |
| Azure OpenAI embeddings | `backend/app/services/openai_service.py` | `text-embedding-3-small` produces vector representations |
| Grounded RAG | `backend/app/services/catalog.py` | Answers use retrieved context and return citations |
| Hallucination resistance | `backend/app/services/openai_service.py` | Unsupported questions return a safe fallback response |
| RAG evaluation | `backend/scripts/evaluate_rag.py` | Repeatable grounded-answer evaluation cases |
| Azure AI Content Safety | `backend/app/services/content_safety.py` | Unsafe prompts and answers are screened |
| Responsible AI | API behavior and RAG prompts | No real company data, citations, grounding, safe fallback |
| Docker | `backend/Dockerfile`, `frontend/Dockerfile` | Reproducible API and frontend containers |
| Local cloud emulation | `docker-compose.yml` | Azurite supports local Blob Storage development |
| Infrastructure as Code | `infra/*.bicep` | Repeatable Azure infrastructure deployments |
| Key Vault | `infra/keyvault.bicep`, `infra/api.bicep` | Runtime secrets are retrieved through Key Vault references |
| Observability | `backend/app/telemetry.py` | Application Insights captures API telemetry |
| Container Apps | `infra/api.bicep`, `infra/frontend.bicep` | Public API and frontend deployments |
| GitHub Actions CI | `.github/workflows/ci.yml` | Linting, tests, and container builds |
| GitHub Actions CD | `.github/workflows/deploy.yml` | OIDC deployment to Azure Container Apps |
| OIDC federation | `infra/github-oidc.bicep` | GitHub deploys without an Azure client secret |
| Least privilege | `infra/github-oidc.bicep` | Deployment identity is scoped to ACR and two Container Apps |

## Validation evidence

- `ruff check app tests`
- `pytest`
- Docker Compose health check
- Document Intelligence Layout and Invoice output JSON
- Azure AI Language enriched output JSON
- Azure AI Search query results
- Grounded RAG answer with citations
- Content Safety integration
- Azure Blob upload using Microsoft Entra RBAC
- GitHub Actions CI pass
- GitHub OIDC deployment pass
- Public API health endpoint
```

After creating it, reply `done`.