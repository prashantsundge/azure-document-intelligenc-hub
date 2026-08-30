@description('Signed-in developer Microsoft Entra object ID.')
param operatorObjectId string

@description('Principal ID of the existing Container Apps managed identity.')
param containerIdentityPrincipalId string

param location string = resourceGroup().location

var uniqueSuffix = toLower(uniqueString(subscription().id, resourceGroup().id))
var keyVaultName = 'kvdocintel${uniqueSuffix}'

var keyVaultSecretsOfficerRoleId = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  'b86a8fe4-44ce-4948-aee5-eccb2c155cd7'
)

var keyVaultSecretsUserRoleId = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  '4633458b-17de-408a-b874-0445c86b69e6'
)

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  tags: {
    project: 'document-intelligence-hub'
    environment: 'dev'
    owner: 'prashant'
    costCenter: 'azure-learning'
    managedBy: 'bicep'
  }
  properties: {
    tenantId: subscription().tenantId
    sku: {
      family: 'A'
      name: 'standard'
    }
    enableRbacAuthorization: true
    
    softDeleteRetentionInDays: 7
    publicNetworkAccess: 'Enabled'
  }
}

resource operatorSecretsOfficer 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(keyVault.id, operatorObjectId, keyVaultSecretsOfficerRoleId)
  scope: keyVault
  properties: {
    roleDefinitionId: keyVaultSecretsOfficerRoleId
    principalId: operatorObjectId
    principalType: 'User'
  }
}

resource containerAppSecretsUser 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(
    keyVault.id,
    containerIdentityPrincipalId,
    keyVaultSecretsUserRoleId
  )
  scope: keyVault
  properties: {
    roleDefinitionId: keyVaultSecretsUserRoleId
    principalId: containerIdentityPrincipalId
    principalType: 'ServicePrincipal'
  }
}

output keyVaultName string = keyVault.name
output keyVaultUri string = keyVault.properties.vaultUri
output keyVaultId string = keyVault.id