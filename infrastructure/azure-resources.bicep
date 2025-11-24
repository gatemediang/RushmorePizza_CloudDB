param location string = resourceGroup().location
param projectName string = 'rushmorepizza'
param environment string = 'prod'
param adminUsername string = 'rushmoreadmin'
@secure()
param adminPassword string

var uniqueSuffix = uniqueString(resourceGroup().id)
var shortSuffix = substring(uniqueSuffix, 0, 6)  // Shortened to 6 characters
var postgresServerName = '${projectName}-pg-${shortSuffix}'
var containerGroupName = '${projectName}-api-${shortSuffix}'
var keyVaultName = 'kv-${projectName}-${shortSuffix}'  // Fixed: max 24 chars
var appInsightsName = '${projectName}-ai-${environment}'
var containerImageName = 'mcr.microsoft.com/azuredocs/aci-helloworld:latest'

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

// Firewall rule to allow all IPs (for demo purposes)
resource firewallRuleClientIP 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2023-03-01-preview' = {
  parent: postgresServer
  name: 'AllowAllIPs'
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

// Azure Container Instances
resource containerGroup 'Microsoft.ContainerInstance/containerGroups@2023-05-01' = {
  name: containerGroupName
  location: location
  properties: {
    containers: [
      {
        name: 'fastapi-app'
        properties: {
          image: containerImageName
          resources: {
            requests: {
              cpu: 1
              memoryInGB: json('1.5')
            }
          }
          ports: [
            {
              port: 8000
              protocol: 'TCP'
            }
          ]
          environmentVariables: [
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
              secureValue: adminPassword
            }
            {
              name: 'SSL_MODE'
              value: 'require'
            }
            {
              name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
              value: appInsights.properties.ConnectionString
            }
          ]
        }
      }
    ]
    osType: 'Linux'
    restartPolicy: 'Always'
    ipAddress: {
      type: 'Public'
      ports: [
        {
          port: 8000
          protocol: 'TCP'
        }
      ]
      dnsNameLabel: containerGroupName
    }
  }
}

output postgresServerFqdn string = postgresServer.properties.fullyQualifiedDomainName
output containerUrl string = 'http://${containerGroup.properties.ipAddress.fqdn}:8000'
output keyVaultName string = keyVault.name
output containerGroupName string = containerGroup.name
output containerFqdn string = containerGroup.properties.ipAddress.fqdn
