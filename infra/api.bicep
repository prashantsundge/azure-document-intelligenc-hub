@description('Azure region for the Container App.')
param location string = resourceGroup().location

@description('Container Apps environment resource ID.')
param managedEnvironmentId string

@description('User-assigned managed identity resource ID.')
param managedIdentityId string

@description('Azure Container Registry login server.')
param containerRegistryLoginServer string

@description('Full API image name, including tag.')
param apiImage string

@description('Azure Key Vault URI, ending with a forward slash.')
param keyVaultUri string

@description('Allowed public frontend origin for browser CORS requests.')
param frontendOrigin string

@description('Azure AI Search endpoint.')
param azureSearchEndpoint string

@description('Azure AI Search index name.')
param azureSearchIndexName string

@description('Azure OpenAI endpoint.')
param azureOpenAiEndpoint string

@description('Azure OpenAI chat deployment name.')
param azureOpenAiChatDeployment string

@description('Azure OpenAI embedding deployment name.')
param azureOpenAiEmbeddingDeployment string

@description('Azure AI Content Safety endpoint.')
param contentSafetyEndpoint string

var apiContainerAppName = 'ca-docintel-api-dev'

resource api 'Microsoft.App/containerApps@2025-02-02-preview' = {
  name: apiContainerAppName
  location: location
  tags: {
    project: 'document-intelligence-hub'
    environment: 'dev'
    owner: 'prashant'
    costCenter: 'azure-learning'
    managedBy: 'bicep'
  }
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityId}': {}
    }
  }
  properties: {
    environmentId: managedEnvironmentId
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 8000
        transport: 'http'
        allowInsecure: false
        corsPolicy: {
          allowCredentials: false
          allowedHeaders: [
            '*'
          ]
          allowedMethods: [
            'GET'
            'POST'
            'OPTIONS'
          ]
          allowedOrigins: [
            frontendOrigin
          ]
          maxAge: 86400
        }
        traffic: [
          {
            latestRevision: true
            weight: 100
          }
        ]
      }
      registries: [
        {
          server: containerRegistryLoginServer
          identity: managedIdentityId
        }
      ]
      secrets: [
        {
          name: 'search-admin-key'
          keyVaultUrl: '${keyVaultUri}secrets/azure-search-admin-key'
          identity: managedIdentityId
        }
        {
          name: 'openai-api-key'
          keyVaultUrl: '${keyVaultUri}secrets/azure-openai-api-key'
          identity: managedIdentityId
        }
        {
          name: 'content-safety-key'
          keyVaultUrl: '${keyVaultUri}secrets/content-safety-key'
          identity: managedIdentityId
        }
        {
        name: 'app-insights-connection-string'
        keyVaultUrl: '${keyVaultUri}secrets/application-insights-connection-string'
        identity: managedIdentityId
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'api'
          image: apiImage
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: [
            {
              name: 'APP_ENV'
              value: 'production'
            }
            {
              name: 'AZURE_SEARCH_ENDPOINT'
              value: azureSearchEndpoint
            }
            {
              name: 'AZURE_SEARCH_INDEX_NAME'
              value: azureSearchIndexName
            }
            {
              name: 'AZURE_SEARCH_ADMIN_KEY'
              secretRef: 'search-admin-key'
            }
            {
              name: 'AZURE_OPENAI_ENDPOINT'
              value: azureOpenAiEndpoint
            }
            {
              name: 'AZURE_OPENAI_CHAT_DEPLOYMENT'
              value: azureOpenAiChatDeployment
            }
            {
              name: 'AZURE_OPENAI_EMBEDDING_DEPLOYMENT'
              value: azureOpenAiEmbeddingDeployment
            }
            {
              name: 'AZURE_OPENAI_API_KEY'
              secretRef: 'openai-api-key'
            }
            {
              name: 'CONTENT_SAFETY_ENDPOINT'
              value: contentSafetyEndpoint
            }
            {
              name: 'CONTENT_SAFETY_KEY'
              secretRef: 'content-safety-key'
            }
            {
            name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
            secretRef: 'app-insights-connection-string'
            }
          ]
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 1
      }
    }
  }
}

output apiName string = api.name
output apiFqdn string = api.properties.configuration.ingress.fqdn
output apiUrl string = 'https://${api.properties.configuration.ingress.fqdn}'