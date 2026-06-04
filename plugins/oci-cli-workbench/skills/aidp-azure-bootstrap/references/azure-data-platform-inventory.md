# Azure Data Platform Inventory

## Purpose

Use these read-only commands to inventory Azure data-platform resources before AIDP migration planning. Prefer resource-group, subscription, or tag scoping when the user provides a boundary.

## Azure CLI readiness

Check the CLI:

```powershell
az version
az extension list --query "[].{name:name,version:version}" --output table
```

If Azure CLI cannot write command logs under `C:\Users\jeggg\.azure\commands`, use a temporary config directory for sandbox-safe checks:

```powershell
$env:AZURE_CONFIG_DIR = Join-Path $env:TEMP "codex-azure-cli"
New-Item -ItemType Directory -Force -Path $env:AZURE_CONFIG_DIR | Out-Null
az version
```

Confirm login and subscription:

```powershell
az account show --query "{name:name,id:id,tenantId:tenantId,user:user.name}" --output json
az account list --query "[].{name:name,id:id,isDefault:isDefault,tenantId:tenantId,state:state}" --output table
```

Only switch subscriptions when the user explicitly selects one:

```powershell
az account set --subscription "<subscription-id-or-name>"
```

## Broad read-only discovery

Use a generic resource list when Azure Resource Graph is unavailable:

```powershell
az resource list --query "[?type=='Microsoft.Storage/storageAccounts' || type=='Microsoft.Synapse/workspaces' || type=='Microsoft.Databricks/workspaces' || type=='Microsoft.DataFactory/factories' || type=='Microsoft.EventHub/namespaces' || type=='Microsoft.Sql/servers' || type=='Microsoft.DocumentDB/databaseAccounts' || type=='Microsoft.KeyVault/vaults'].{name:name,type:type,resourceGroup:resourceGroup,location:location,tags:tags}" --output json
```

If Resource Graph is available, use it for a cleaner cross-resource view:

```powershell
az graph query -q "Resources | where type in~ ('microsoft.storage/storageaccounts','microsoft.synapse/workspaces','microsoft.databricks/workspaces','microsoft.datafactory/factories','microsoft.eventhub/namespaces','microsoft.sql/servers','microsoft.documentdb/databaseaccounts','microsoft.keyvault/vaults') | project name, type, resourceGroup, location, tags" --first 1000
```

If a command group is unavailable, report the missing extension or provider visibility. Do not run `az extension add` or accept extension-install prompts unless the user explicitly asks.

## Service-specific inventory

Storage accounts and ADLS Gen2:

```powershell
az storage account list --query "[].{name:name,resourceGroup:resourceGroup,location:location,kind:kind,sku:sku.name,hns:isHnsEnabled,networkDefaultAction:networkRuleSet.defaultAction,privateEndpoints:privateEndpointConnections[].privateEndpoint.id,tags:tags}" --output json
```

Synapse:

```powershell
az synapse workspace list --query "[].{name:name,resourceGroup:resourceGroup,location:location,defaultDataLakeStorage:defaultDataLakeStorage,managedResourceGroupName:managedResourceGroupName,sqlAdministratorLogin:sqlAdministratorLogin,tags:tags}" --output json
```

Azure Databricks:

```powershell
az databricks workspace list --query "[].{name:name,resourceGroup:resourceGroup,location:location,workspaceUrl:workspaceUrl,managedResourceGroupId:managedResourceGroupId,sku:sku.name,tags:tags}" --output json
```

Azure Data Factory:

```powershell
az datafactory factory list --query "[].{name:name,resourceGroup:resourceGroup,location:location,identity:identity.type,tags:tags}" --output json
```

Event Hubs:

```powershell
az eventhubs namespace list --query "[].{name:name,resourceGroup:resourceGroup,location:location,sku:sku.name,capacity:sku.capacity,isAutoInflateEnabled:isAutoInflateEnabled,tags:tags}" --output json
```

Azure SQL:

```powershell
az sql server list --query "[].{name:name,resourceGroup:resourceGroup,location:location,fullyQualifiedDomainName:fullyQualifiedDomainName,publicNetworkAccess:publicNetworkAccess,tags:tags}" --output json
az sql db list --resource-group "<resource-group>" --server "<server-name>" --query "[].{name:name,status:status,edition:edition,serviceObjectiveName:serviceObjectiveName,maxSizeBytes:maxSizeBytes}" --output json
```

Cosmos DB:

```powershell
az cosmosdb list --query "[].{name:name,resourceGroup:resourceGroup,location:location,kind:kind,api:kind,consistency:consistencyPolicy.defaultConsistencyLevel,publicNetworkAccess:publicNetworkAccess,tags:tags}" --output json
```

Key Vault dependencies, without secret values:

```powershell
az keyvault list --query "[].{name:name,resourceGroup:resourceGroup,location:location,tenantId:properties.tenantId,sku:properties.sku.name,enableRbacAuthorization:properties.enableRbacAuthorization,publicNetworkAccess:properties.publicNetworkAccess,tags:tags}" --output json
```

Private networking:

```powershell
az network private-endpoint list --query "[].{name:name,resourceGroup:resourceGroup,location:location,subnet:subnet.id,connections:privateLinkServiceConnections[].privateLinkServiceId,tags:tags}" --output json
az network private-dns zone list --query "[].{name:name,resourceGroup:resourceGroup,tags:tags}" --output json
```

Managed identities and role assignments can explain runtime dependencies, but can be large. Scope them when possible:

```powershell
az identity list --query "[].{name:name,resourceGroup:resourceGroup,location:location,clientId:clientId,tags:tags}" --output json
az role assignment list --scope "<resource-id>" --query "[].{principalName:principalName,principalType:principalType,roleDefinitionName:roleDefinitionName,scope:scope}" --output json
```

## Azure-to-AIDP interpretation

Map inventory to AIDP planning evidence:

| Azure signal | AIDP migration meaning |
| --- | --- |
| ADLS Gen2 or Blob containers | Source prefixes, landing zones, historical source candidates, source manifest paths |
| Synapse workspaces | SQL transformations, warehouse dependencies, Spark or pipeline evidence |
| Databricks workspaces | Notebook, job, Delta table, cluster, and library evidence for medallion mapping |
| Data Factory factories | Orchestration graph, triggers, schedules, linked services, and dependency order |
| Event Hubs namespaces | Streaming source systems, checkpoint needs, batch-versus-streaming coexistence |
| Azure SQL servers and DBs | Relational sources, reference data, control tables, or validation truth candidates |
| Cosmos DB accounts | NoSQL source systems, partition keys, change-feed or API-specific migration risks |
| Key Vaults | Secret dependency inventory only; never export secret values |
| Private endpoints and DNS | Network prerequisites for source export, AIDP access, and migration staging |

## Handoff shape

Summarize results in this order:

1. Azure CLI and subscription status.
2. Data-platform resource inventory grouped by service.
3. Source systems and storage roots likely to feed AIDP.
4. Orchestration, streaming, and private-network dependencies.
5. Evidence that should be copied or exported into `.source/`.
6. Gaps, permissions, and the next skill: `$aidp-source-intake` or `$aidp-source-manifest`.
