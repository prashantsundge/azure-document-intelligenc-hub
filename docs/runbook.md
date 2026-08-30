

```md
# Operations runbook

## Health check

```powershell
$ApiUrl = "https://ca-docintel-api-dev.blackwave-0f15539d.eastus.azurecontainerapps.io"

Invoke-RestMethod "$ApiUrl/api/v1/health"
```

Expected response: `healthy`.

## Check the deployed Container App revision

```powershell
az containerapp show `
  --name ca-docintel-api-dev `
  --resource-group rg-document-intelligence-hub-dev `
  --query "{latestRevision:properties.latestRevisionName,provisioningState:properties.provisioningState}" `
  --output json
```

## Read Container App logs

Use system logs when a revision does not start:

```powershell
az containerapp logs show `
  --name ca-docintel-api-dev `
  --resource-group rg-document-intelligence-hub-dev `
  --type system `
  --tail 50
```

Use console logs when the application starts but a request fails:

```powershell
az containerapp logs show `
  --name ca-docintel-api-dev `
  --resource-group rg-document-intelligence-hub-dev `
  --type console `
  --tail 50
```

## Verify Application Insights telemetry

```powershell
az monitor app-insights query `
  --app appi-docintel-dev-awjtcgryz5xpw `
  --resource-group rg-document-intelligence-hub-dev `
  --offset 1h `
  --analytics-query "requests | where name contains '/api/v1/' | project timestamp, name, resultCode, duration, success | top 20 by timestamp desc" `
  --output table
```

## Common failures

| Symptom | Likely cause | Check |
|---|---|---|
| API fails to start | Missing Key Vault permission or invalid secret reference | Container App system logs and Key Vault role assignments |
| RAG answer fails | Azure OpenAI deployment, endpoint, or key issue | `AZURE_OPENAI_*` configuration and API console logs |
| Search returns no results | Index has not been created or populated | Run `python -m scripts.index_documents --confirm-write` locally |
| Blob upload is denied | RBAC propagation delay or wrong identity | Wait a few minutes; verify Storage Blob Data Contributor |
| GitHub deployment fails at login | OIDC subject does not match federated credential | Compare GitHub log subject claim with `infra/github-oidc.bicep` |
| GitHub deployment fails to push image | Missing AcrPush role | Verify the GitHub deployment identity role at ACR scope |

## Roll back an API revision

First list revisions:

```powershell
az containerapp revision list `
  --name ca-docintel-api-dev `
  --resource-group rg-document-intelligence-hub-dev `
  --output table
```

Then reactivate a known healthy revision:

```powershell
az containerapp revision activate `
  --name ca-docintel-api-dev `
  --resource-group rg-document-intelligence-hub-dev `
  --revision <healthy-revision-name>
```

Verify health after rollback.

## Cost controls

- Use only synthetic sample documents.
- Keep Container Apps at minimum replicas `0` where configured.
- Use small development SKUs.
- Avoid unnecessary model calls during testing.
- Delete unused ACR images periodically.
- Create a budget alert in Azure Cost Management for this resource group.

## Teardown

> This permanently deletes every resource in the demo resource group, including Key Vault, Container Apps, storage, search indexes, logs, and AI resources created there.

```powershell
az group delete `
  --name rg-document-intelligence-hub-dev `
  --yes `
  --no-wait
```

Confirm deletion status:

```powershell
az group exists `
  --name rg-document-intelligence-hub-dev
```
