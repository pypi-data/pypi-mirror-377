# aiWare Python SDK

## Installation

The SDK is available as the [`aiware` package on PyPI](https://pypi.org/project/aiware/)

`uv add aiware`

## Features

### Core

Common aiWare features are available via the `Aiware` and `AsyncAiware`.

```python
aiware = AsyncAiware(
  graphql_endpoint="https://api.us-1.veritone.com/v3/graphql"
  # search_endpoint="https://api.us-1.veritone.com/v3/graphql" FIXME
  auth=EnvAuth()
)
```

### AION

### TextIO

### Code Generator

#### GraphQL

In `pyproject.toml`:

```toml
[tool.aiware-codegen.client]
core_graphql_url = "https://api.us-1.veritone.com/v3/graphql"
queries_path = "src/archive_scan/aiware/graphql/operations" # this is where your .graphql files are
# these correlate to where the client will be generated
target_package_name = "client_generated" 
target_package_path = "src/archive_scan/aiware/graphql"
async_client_name = "AsyncArchiveScanAiwareGraphQL"
sync_client_name = "ArchiveScanAiwareGraphQL"
```

To generate: `uv run aiware-codegen-client`
