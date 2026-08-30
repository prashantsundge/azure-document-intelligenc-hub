@description('Deployment environment name.')
param environmentName string = 'dev'

@description('Owner tag value.')
param owner string = 'portfolio'

@description('Cost center tag value.')
param costCenter string = 'learning'

@description('Azure region. Defaults to the existing resource group location.')
param location string = resourceGroup().location

var projectName = 'document-intelligence-hub'
var uniqueSuffix = toLower(uniqueString(subscription().id, resourceGroup().id))

var containerRegistryName = 'acrdocintel${uniqueSuffix}'
var logAnalyticsName = 'log-docintel-${environmentName}-${uniqueSuffix}'
var applicationInsightsName = 'appi-docintel-${environmentName}-${uniqueSuffix}'
var containerAppsEnvironmentName = 'cae-docintel-${environmentName}-${uniqueSuffix}'
var managedIdentityName = 'id-docintel-${environmentName}-${uniqueSuffix}'

var commonTags = {
  project: projectName
  environment: environmentName
  owner: owner
  costCenter: costCenter
  managedBy: 'bicep'
}

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: containerRegistryName
  location: location
  tags: commonTags
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: false
    publicNetworkAccess: 'Enabled'
  }
}

resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: logAnalyticsName
  location: location
  tags: commonTags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: applicationInsightsName
  location: location
  kind: 'web'
  tags: commonTags
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalyticsWorkspace.id
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: containerAppsEnvironmentName
  location: location
  tags: commonTags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalyticsWorkspace.properties.customerId
        sharedKey: logAnalyticsWorkspace.listKeys().primarySharedKey
      }
    }
  }
}

resource containerAppIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: managedIdentityName
  location: location
  tags: commonTags
}

var acrPullRoleDefinitionId = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  '7f951dda-4ed3-4680-a7ca-43fe172d538d'
)

resource acrPullRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(
    containerRegistry.id,
    containerAppIdentity.name,
    'AcrPull'
  )
  scope: containerRegistry
  properties: {
    roleDefinitionId: acrPullRoleDefinitionId
    principalId: containerAppIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

output containerRegistryName string = containerRegistry.name
output containerRegistryLoginServer string = containerRegistry.properties.loginServer
output containerAppsEnvironmentName string = containerAppsEnvironment.name
output containerAppsEnvironmentId string = containerAppsEnvironment.id
output managedIdentityId string = containerAppIdentity.id
output applicationInsightsConnectionString string = applicationInsights.properties.ConnectionString