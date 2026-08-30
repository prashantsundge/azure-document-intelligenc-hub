@description('Azure region for the Container App.')
param location string = resourceGroup().location

@description('Container Apps environment resource ID.')
param managedEnvironmentId string

@description('User-assigned managed identity resource ID.')
param managedIdentityId string

@description('Azure Container Registry login server.')
param containerRegistryLoginServer string

@description('Full frontend image name, including tag.')
param frontendImage string

var frontendContainerAppName = 'ca-docintel-web-dev'

resource frontend 'Microsoft.App/containerApps@2025-02-02-preview' = {
  name: frontendContainerAppName
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
        targetPort: 80
        transport: 'http'
        allowInsecure: false
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
    }
    template: {
      containers: [
        {
          name: 'frontend'
          image: frontendImage
          resources: {
            cpu: json('0.25')
            memory: '0.5Gi'
          }
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 1
      }
    }
  }
}

output frontendName string = frontend.name
output frontendUrl string = 'https://${frontend.properties.configuration.ingress.fqdn}'