### 1. Update `README.md`

Add this section near the end of the root `README.md`:

```md
## Documentation

- [Architecture](docs/architecture.md)
- [Azure setup](docs/azure-setup.md)
- [Operations runbook](docs/runbook.md)
- [Azure AI learning map](docs/learning-map.md)
- [Contributing](CONTRIBUTING.md)

## Safety and privacy

This project uses only synthetic or openly licensed sample documents. Do not upload company documents, personal data, API keys, or connection strings.

## Roadmap

Project 1 focuses on document intelligence, language, search/RAG, responsible AI, secure deployment, and observability.

Future projects will focus on speech/custom vision and agentic AI workflows.
```

### 2. Create the LinkedIn announcement

Create:

`docs/linkedin-announcement.md`

```md
# LinkedIn announcement draft

I have completed and deployed my Azure AI portfolio project: **Azure Document Intelligence Hub**.

It is a public, read-only document assistant built with React, FastAPI, Docker, and Azure Container Apps. The project processes only synthetic sample documents and demonstrates an end-to-end Azure AI workflow:

- Azure AI Document Intelligence for layout and invoice extraction
- Azure AI Language for entities, key phrases, language detection, and PII-aware enrichment
- Azure AI Search hybrid keyword and vector retrieval
- Azure OpenAI for embeddings and grounded RAG answers with citations
- Azure AI Content Safety for prompt and answer screening
- Azure Blob Storage with managed identity and private access
- Azure Key Vault, Application Insights, Docker, Bicep, and GitHub Actions CI/CD
- GitHub OIDC deployment with no Azure client secret

I focused on production-style engineering practices: private storage, Key Vault references, least-privilege RBAC, structured evaluation, health checks, observability, infrastructure as code, and reproducible container deployments.

Live demo:
https://ca-docintel-web-dev.blackwave-0f15539d.eastus.azurecontainerapps.io

Source code:
https://github.com/prashantsundge/azure-document-intelligenc-hub

#Azure #AzureAI #DocumentIntelligence #RAG #AzureOpenAI #AzureAISearch #FastAPI #Docker #DevOps #GitHubActions #AIEngineering
```

After both files are created, reply `done`.