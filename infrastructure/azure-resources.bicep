param location string = resourceGroup().location
param projectName string = 'rushmorepizza'
param environment string = 'prod'
param adminUsername string = 'rushmoreadmin'
@secure()
param adminPassword string

var uniqueSuffix = uniqueString(resourceGroup().id)
var postgresServerName = '${projectName}-postgres-${uniqueSuffix}'
var appServicePlanName = '${projectName}-asp-${environment}'
var webAppName = '${projectName}-api-${uniqueSuffix}'
var keyVaultName = '${projectName}-kv-${uniqueSuffix}'
var appInsightsName = '${projectName}-ai-${environment}'

// PostgreSQL Flexible Server
resource postgresServer 'Microsoft.DBforPostgreSQL/flexibleServers@2023-03-01-preview' = {
  name: postgresServerName
  location: location
  sku: {
    name: 'Standard_B1ms'
    tier: 'Burstable'
  }
  properties: {
    administratorLogin: adminUsername
    administratorLoginPassword: adminPassword
    version: '16'
    storage: {
      storageSizeGB: 32
    }
    backup: {
      backupRetentionDays: 7
      geoRedundantBackup: 'Disabled'
    }
    highAvailability: {
      mode: 'Disabled'
    }
  }
}

// PostgreSQL Database
resource postgresDatabase 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2023-03-01-preview' = {
  parent: postgresServer
  name: 'rushmore_db'
  properties: {
    charset: 'UTF8'
    collation: 'en_US.utf8'
  }
}

// Firewall rule to allow Azure services
resource firewallRuleAzure 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2023-03-01-preview' = {
  parent: postgresServer
  name: 'AllowAzureServices'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

// Firewall rule to allow your IP (update this)
resource firewallRuleClientIP 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2023-03-01-preview' = {
  parent: postgresServer
  name: 'AllowClientIP'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '255.255.255.255'
  }
}

// Key Vault
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enabledForDeployment: true
    enabledForTemplateDeployment: true
    enabledForDiskEncryption: false
    enableRbacAuthorization: true
    publicNetworkAccess: 'Enabled'
  }
}

// Application Insights
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

// App Service Plan (Linux)
resource appServicePlan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: appServicePlanName
  location: location
  sku: {
    name: 'B1'
    tier: 'Basic'
  }
  kind: 'linux'
  properties: {
    reserved: true
  }
}

// Web App (FastAPI)
resource webApp 'Microsoft.Web/sites@2023-01-01' = {
  name: webAppName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      alwaysOn: true
      ftpsState: 'Disabled'
      appSettings: [
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: appInsights.properties.ConnectionString
        }
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: 'true'
        }
        {
          name: 'DB_HOST'
          value: '${postgresServerName}.postgres.database.azure.com'
        }
        {
          name: 'DB_PORT'
          value: '5432'
        }
        {
          name: 'DB_NAME'
          value: 'rushmore_db'
        }
        {
          name: 'DB_USER'
          value: adminUsername
        }
        {
          name: 'DB_PASSWORD'
          value: '@Microsoft.KeyVault(SecretUri=${keyVault.properties.vaultUri}secrets/db-password/)'
        }
        {
          name: 'SSL_MODE'
          value: 'require'
        }
      ]
    }
  }
}

// Store secrets in Key Vault
resource dbPasswordSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'db-password'
  properties: {
    value: adminPassword
  }
}

resource dbConnectionStringSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'db-connection-string'
  properties: {
    value: 'postgresql://${adminUsername}:${adminPassword}@${postgresServerName}.postgres.database.azure.com:5432/rushmore_db?sslmode=require'
  }
}

// Grant Key Vault access to Web App
resource keyVaultAccessPolicy 'Microsoft.KeyVault/vaults/accessPolicies@2023-07-01' = {
  parent: keyVault
  name: 'add'
  properties: {
    accessPolicies: [
      {
        tenantId: subscription().tenantId
        objectId: webApp.identity.principalId
        permissions: {
          secrets: [
            'get'
            'list'
          ]
        }
      }
    ]
  }
}

output postgresServerFqdn string = postgresServer.properties.fullyQualifiedDomainName
output webAppUrl string = 'https://${webApp.properties.defaultHostName}'
output keyVaultName string = keyVault.name
output webAppName string = webApp.name
