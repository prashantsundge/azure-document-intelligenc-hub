@description('GitHub repository owner.')
param githubOwner string = 'prashantsundge'

@description('Immutable GitHub numeric owner ID.')
param githubOwnerId string = '120663250'

@description('GitHub repository name without .git.')
param githubRepositoryName string = 'azure-document-intelligenc-hub'

@description('Immutable GitHub numeric repository ID.')
param githubRepositoryId string = '1348784684'

@description('Protected GitHub Actions environment allowed to deploy.')
param githubEnvironment string = 'production'

@description('Existing Azure Container Registry name.')
param containerRegistryName string = 'acrdocintelawjtcgryz5xpw'

@description('Existing API Container App name.')
param apiContainerAppName string = 'ca-docintel-api-dev'

@description('Existing frontend Container App name.')
param frontendContainerAppName string = 'ca-docintel-web-dev'

param location string = resourceGroup().location

var uniqueSuffix = toLower(uniqueString(subscription().id, resourceGroup().id))
var deploymentIdentityName = 'id-docintel-github-${uniqueSuffix}'

var acrPushRoleId = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  '8311e382-0749-4cb8-b61a-304f252e45ec'
)

var contributorRoleId = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  'b24988ac-6180-42a0-ab88-20f7382dd24c'
)

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-07-01' existing = {
  name: containerRegistryName
}

resource apiContainerApp 'Microsoft.App/containerApps@2025-02-02-preview' existing = {
  name: apiContainerAppName
}

resource frontendContainerApp 'Microsoft.App/containerApps@2025-02-02-preview' existing = {
  name: frontendContainerAppName
}

resource githubDeploymentIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: deploymentIdentityName
  location: location
  tags: {
    project: 'document-intelligence-hub'
    environment: 'dev'
    purpose: 'github-actions-oidc'
    managedBy: 'bicep'
  }
}

resource githubProductionFederatedCredential 'Microsoft.ManagedIdentity/userAssignedIdentities/federatedIdentityCredentials@2023-01-31' = {
  parent: githubDeploymentIdentity
  name: 'github-production'
  properties: {
    audiences: [
      'api://AzureADTokenExchange'
    ]
    issuer: 'https://token.actions.githubusercontent.com'
    subject: 'repo:${githubOwner}@${githubOwnerId}/${githubRepositoryName}@${githubRepositoryId}:environment:${githubEnvironment}'
  }
}

resource githubAcrPush 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(containerRegistry.id, githubDeploymentIdentity.name, acrPushRoleId)
  scope: containerRegistry
  properties: {
    roleDefinitionId: acrPushRoleId
    principalId: githubDeploymentIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

resource githubApiContributor 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(apiContainerApp.id, githubDeploymentIdentity.name, contributorRoleId)
  scope: apiContainerApp
  properties: {
    roleDefinitionId: contributorRoleId
    principalId: githubDeploymentIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

resource githubFrontendContributor 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(frontendContainerApp.id, githubDeploymentIdentity.name, contributorRoleId)
  scope: frontendContainerApp
  properties: {
    roleDefinitionId: contributorRoleId
    principalId: githubDeploymentIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

output githubDeploymentIdentityName string = githubDeploymentIdentity.name
output githubClientId string = githubDeploymentIdentity.properties.clientId
output azureTenantId string = subscription().tenantId
output azureSubscriptionId string = subscription().subscriptionId