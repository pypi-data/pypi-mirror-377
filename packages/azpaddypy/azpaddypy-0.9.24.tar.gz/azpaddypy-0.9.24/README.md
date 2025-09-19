# AzPaddyPy

A comprehensive Python package for Azure cloud services integration with standardized configuration management, OpenTelemetry tracing, and builder patterns.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AzPaddyPy Architecture                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐ │
│  │   Management    │    │    Resources    │    │    Tools    │ │
│  │   Services      │    │    Services     │    │             │ │
│  ├─────────────────┤    ├─────────────────┤    ├─────────────┤ │
│  │ • Identity      │    │ • Key Vault     │    │ • Config    │ │
│  │ • Logging       │    │ • Storage       │    │   Manager   │ │
│  │ • Environment   │    │ • Cosmos DB     │    │ • Prompt    │ │
│  │   Detection     │    │                 │    │   Manager   │ │
│  └─────────────────┘    └─────────────────┘    └─────────────┘ │
│           │                       │                    │        │
│           └───────────────────────┼────────────────────┘        │
│                                   │                             │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    Builder Pattern                         │ │
│  │                                                             │ │
│  │  ┌─────────────────┐    ┌─────────────────┐                │ │
│  │  │ Configuration   │    │   Azure         │                │ │
│  │  │ Setup Builder   │───▶│ Management      │                │ │
│  │  │                 │    │ Builder         │                │ │
│  │  └─────────────────┘    └─────────────────┘                │ │
│  │           │                       │                        │ │
│  │           └───────────────────────┼────────────────────────┘ │
│  │                                   │                          │
│  │  ┌─────────────────┐    ┌─────────────────┐                │ │
│  │  │   Azure         │    │   Resource      │                │ │
│  │  │   Resource      │◀───│   Director      │                │ │
│  │  │   Builder       │    │                 │                │ │
│  │  └─────────────────┘    └─────────────────┘                │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    mgmt_config.py                          │ │
│  │                                                             │ │
│  │  • Centralized configuration                               │ │
│  │  • Pre-configured services                                 │ │
│  │  • Environment detection                                   │ │
│  │  • Service validation                                      │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Features

- **Azure Identity Management**: Automatic credential handling with token caching
- **Azure Key Vault Integration**: Secure secrets management with multiple vault support
- **Azure Storage Operations**: Blob, file, and queue storage with SAS token generation
- **Comprehensive Logging**: Application Insights integration with OpenTelemetry
- **Builder Patterns**: Flexible service composition and configuration
- **Environment Detection**: Automatic Docker vs. local environment handling
- **Configuration Management**: Centralized configuration with JSON and environment variables
- **Prompt Management**: Cosmos DB-based prompt storage and retrieval

## Installation

```bash
pip install azpaddypy
```

## Quick Start

### Basic Usage with mgmt_config.py

Every project using azpaddypy gets a pre-configured `mgmt_config.py` file that provides centralized access to Azure services:

```python
from mgmt_config import logger, keyvaults, storage_accounts, cosmos_dbs

# Logging with Application Insights integration
logger.info("Application started")
logger.error("An error occurred", exc_info=True)

# Access Key Vault secrets
main_keyvault = keyvaults.get("main")
secret = main_keyvault.get_secret("my-secret")

# Storage operations
main_storage = storage_accounts.get("main")
container_client = main_storage.get_container_client("my-container")

# Cosmos DB operations
prompt_db = cosmos_dbs.get("promptmgmt")
database = prompt_db.get_database_client("prompts")
```

### Environment Configuration

Set up your environment variables:

```bash
# Required environment variables
export key_vault_uri="https://my-vault.vault.azure.net/"
export head_key_vault_uri="https://my-head-vault.vault.azure.net/"

# Optional environment variables
export LOGGER_LOG_LEVEL="INFO"
export APPLICATIONINSIGHTS_CONNECTION_STRING="your-connection-string"
```

### Builder Pattern Usage

For advanced scenarios, use the builder pattern for custom configurations:

```python
from azpaddypy.builder import (
    ConfigurationSetupBuilder,
    AzureManagementBuilder,
    AzureResourceBuilder
)

# Build environment configuration
environment_config = (
    ConfigurationSetupBuilder()
    .with_local_env_management()
    .with_environment_detection()
    .with_service_configuration()
    .with_logging_configuration()
    .with_identity_configuration()
    .build()
)

# Build management services
management_config = (
    AzureManagementBuilder(environment_config)
    .with_logger()
    .with_identity()
    .with_keyvault(vault_url="https://my-vault.vault.azure.net/", name="main")
    .build()
)

# Build resource services
resource_config = (
    AzureResourceBuilder(management_config, environment_config)
    .with_storage(name="main", account_url="https://mystorage.blob.core.windows.net/")
    .with_cosmosdb(name="promptmgmt", endpoint="https://mycosmos.documents.azure.com:443/")
    .build()
)

# Access services
logger = management_config.logger
keyvault = management_config.keyvaults.get("main")
storage = resource_config.storage_accounts.get("main")
```

### Key Vault Operations

```python
from mgmt_config import keyvaults

# Get Key Vault client
main_vault = keyvaults.get("main")
head_vault = keyvaults.get("head")

# Retrieve secrets
api_key = main_vault.get_secret("api-key")
connection_string = main_vault.get_secret("database-connection")

# Store secrets
main_vault.set_secret("new-secret", "secret-value")

# List secrets
secrets = main_vault.list_properties_of_secrets()
```

### Storage Operations

```python
from mgmt_config import storage_accounts

# Get storage client
storage = storage_accounts.get("main")

# Blob operations
container_client = storage.get_container_client("my-container")
blob_client = container_client.get_blob_client("my-blob.txt")

# Upload file
with open("local-file.txt", "rb") as data:
    blob_client.upload_blob(data, overwrite=True)

# Download file
with open("downloaded-file.txt", "wb") as download_file:
    download_stream = blob_client.download_blob()
    download_file.write(download_stream.readall())

# Queue operations
queue_client = storage.get_queue_client("my-queue")
queue_client.send_message("Hello, World!")

# File share operations
file_client = storage.get_file_client("my-share", "my-file.txt")
file_client.upload_file("local-file.txt")
```

### Cosmos DB Operations

```python
from mgmt_config import cosmos_dbs

# Get Cosmos DB client
cosmos_client = cosmos_dbs.get("promptmgmt")

# Database operations
database = cosmos_client.get_database_client("prompts")
container = database.get_container_client("my-container")

# Query documents
query = "SELECT * FROM c WHERE c.type = 'prompt'"
items = container.query_items(query=query, enable_cross_partition_query=True)

# Create document
document = {"id": "unique-id", "type": "prompt", "content": "Hello World"}
container.create_item(body=document)
```

### Configuration Management

```python
from mgmt_config import configuration_manager

# Get configuration
config = configuration_manager.get_config("my-config")

# Access nested configuration
api_settings = configuration_manager.get_config("api.settings")

# Print all configurations
print(configuration_manager)

# Reload configurations
configuration_manager.reload()
```

### Prompt Management

```python
from mgmt_config import prompt_manager

# Save a prompt
prompt_manager.save_prompt(
    prompt_id="my-prompt",
    prompt_type="system",
    content="You are a helpful assistant.",
    metadata={"version": "1.0", "author": "user"}
)

# Retrieve a prompt
prompt = prompt_manager.get_prompt("my-prompt")

# List all prompts
prompts = prompt_manager.list_prompts()

# Delete a prompt
prompt_manager.delete_prompt("my-prompt")
```

### Direct Service Usage

For direct access to azpaddypy services without mgmt_config:

```python
from azpaddypy.mgmt.identity import create_azure_identity
from azpaddypy.mgmt.logging import create_app_logger
from azpaddypy.resources.keyvault import create_azure_keyvault
from azpaddypy.resources.storage import create_azure_storage

# Create identity
identity = create_azure_identity(
    service_name="my-service",
    service_version="1.0.0"
)

# Create logger
logger = create_app_logger(
    service_name="my-service",
    service_version="1.0.0"
)

# Create Key Vault client
keyvault = create_azure_keyvault(
    vault_url="https://my-vault.vault.azure.net/",
    identity=identity,
    logger=logger
)

# Create storage client
storage = create_azure_storage(
    account_url="https://mystorage.blob.core.windows.net/",
    identity=identity,
    logger=logger
)
```

## Advanced Usage

### Custom Environment Configuration

```python
from azpaddypy.mgmt.local_env_manager import create_local_env_manager

# Create custom environment settings
local_settings = create_local_env_manager(
    env_file_path="./.env",
    env_var_prefix="MY_APP_",
    include_system_env=True
)

# Access environment variables
database_url = local_settings.get("DATABASE_URL")
api_key = local_settings.get("API_KEY")
```

### Function App Logging

```python
from azpaddypy.mgmt.logging import create_function_logger

# Create function-specific logger
logger = create_function_logger(
    service_name="my-function",
    service_version="1.0.0"
)

def my_function():
    logger.info("Function started")
    # Your function logic here
    logger.info("Function completed")
```

### SAS Token Generation

```python
from mgmt_config import storage_accounts

storage = storage_accounts.get("main")

# Generate container SAS token
container_sas = storage.generate_container_sas(
    container_name="my-container",
    permission="read",
    expiry=datetime.utcnow() + timedelta(hours=1)
)

# Generate blob SAS token
blob_sas = storage.generate_blob_sas(
    container_name="my-container",
    blob_name="my-blob.txt",
    permission="read",
    expiry=datetime.utcnow() + timedelta(hours=1)
)
```

## Error Handling

```python
from mgmt_config import logger, keyvaults

try:
    # Attempt to access Key Vault
    secret = keyvaults.get("main").get_secret("my-secret")
except Exception as e:
    logger.error(f"Failed to retrieve secret: {e}", exc_info=True)
    # Handle error appropriately
```

## Testing

```python
import pytest
from unittest.mock import patch
from mgmt_config import logger, keyvaults

def test_keyvault_operations():
    with patch('mgmt_config.keyvaults') as mock_keyvaults:
        # Your test logic here
        pass
```

## Dependencies

- `azure-monitor-opentelemetry==1.6.10`
- `azure-identity==1.23.0`
- `azure-keyvault-secrets==4.10.0`
- `azure-keyvault-keys==4.11.0`
- `azure-keyvault-certificates==4.10.0`
- `azure-storage-blob==12.25.1`
- `azure-storage-file-share==12.21.0`
- `azure-storage-queue==12.12.0`
- `azure-cosmos==4.9.0`
- `chardet==5.2.0`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 