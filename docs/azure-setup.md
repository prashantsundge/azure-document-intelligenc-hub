Create this file:

`docs/azure-setup.md`

```md
# Azure setup

This guide describes the Azure resources used by Azure Document Intelligence Hub.

> Never commit API keys, connection strings, `.env` files, or Azure credentials.

## Prerequisites

- Azure subscription
- Azure CLI
- Bicep CLI: `az bicep install`
- Docker Desktop
- GitHub repository
- Python 3.12 and Node.js LTS

## Resource group

### Azure portal

1. Open **Resource groups**.
2. Select **Create**.
3. Use a unique name, such as `rg-document-intelligence-hub-dev`.
4. Select a region close to your Azure AI resources.

### Azure CLI

```powershell
az group create `
  --name rg-document-intelligence-hub-dev `
  --location eastus
```

## Foundation infrastructure

The foundation deployment creates:

- Azure Container Registry
- Log Analytics workspace
- Application Insights
- Azure Container Apps environment
- User-assigned managed identity for the application

Validate and deploy:

```powershell
az deployment group validate `
  --resource-group rg-document-intelligence-hub-dev `
  --template-file infra/main.bicep `
  --parameters infra/dev.bicepparam

az deployment group create `
  --name document-intelligence-hub-foundation-dev `
  --resource-group rg-document-intelligence-hub-dev `
  --template-file infra/main.bicep `
  --parameters infra/dev.bicepparam
```

## Azure AI resources

Create these resources through the Azure portal:

1. **Azure AI Document Intelligence**
   - Use the `prebuilt-layout` and `prebuilt-invoice` models.

2. **Azure AI Language**
   - Used for language detection, entities, key phrases, and PII detection.

3. **Azure AI Search**
   - Used for keyword and vector retrieval.

4. **Azure OpenAI**
   - Deploy:
     - `gpt-4.1-mini` for grounded answers.
     - `text-embedding-3-small` for vector embeddings.

5. **Azure AI Content Safety**
   - Used to screen prompts and generated answers.

Store service endpoints, deployment names, and keys only in local `.env` during development. Move production keys to Key Vault before deployment.

## Azure Key Vault

Key Vault stores the API keys for Azure AI Search, Azure OpenAI, Content Safety, and Application Insights.

```powershell
az deployment group create `
  --name document-intelligence-hub-keyvault-dev `
  --resource-group rg-document-intelligence-hub-dev `
  --template-file infra/keyvault.bicep `
  --parameters `
    "operatorObjectId=<your-microsoft-entra-object-id>" `
    "containerIdentityPrincipalId=<container-app-managed-identity-principal-id>"
```

The Container App identity receives **Key Vault Secrets User**. Your developer identity receives **Key Vault Secrets Officer**.

## Private Azure Blob Storage

Blob Storage holds only synthetic or openly licensed source documents.

```powershell
az deployment group create `
  --name document-intelligence-hub-storage-dev `
  --resource-group rg-document-intelligence-hub-dev `
  --template-file infra/storage.bicep `
  --parameters `
    "operatorObjectId=<your-microsoft-entra-object-id>" `
    "containerIdentityPrincipalId=<container-app-managed-identity-principal-id>"
```

Security settings:

- Private `documents` container
- Public blob access disabled
- Shared-key access disabled
- HTTPS required
- Storage Blob Data Contributor granted through Azure RBAC

## Container Apps

The API and frontend are deployed independently.

```powershell
az deployment group create `
  --name document-intelligence-hub-api-dev `
  --resource-group rg-document-intelligence-hub-dev `
  --template-file infra/api.bicep `
  --parameters <environment-specific-values>

az deployment group create `
  --name document-intelligence-hub-frontend-dev `
  --resource-group rg-document-intelligence-hub-dev `
  --template-file infra/frontend.bicep `
  --parameters <environment-specific-values>
```

Use Key Vault references for secrets. Do not pass production API keys directly to Bicep or GitHub Actions.

## GitHub OIDC deployment

`infra/github-oidc.bicep` creates a dedicated GitHub deployment identity.

It has:

- `AcrPush` on the Azure Container Registry
- `Contributor` scoped only to the API Container App
- `Contributor` scoped only to the frontend Container App
- No Key Vault, Blob Storage, or AI service permissions

GitHub environment secrets required by `.github/workflows/deploy.yml`:

```text
AZURE_CLIENT_ID
AZURE_TENANT_ID
AZURE_SUBSCRIPTION_ID
```

The GitHub Actions workflow authenticates using OIDC. It does not use an Azure client secret.

## Verification

```powershell
Invoke-RestMethod `
  "https://ca-docintel-api-dev.blackwave-0f15539d.eastus.azurecontainerapps.io/api/v1/health"
```

Open the public frontend:

```text
https://ca-docintel-web-dev.blackwave-0f15539d.eastus.azurecontainerapps.io
```
```
