# n8npy-client

Python client for the n8n Public REST API.

## Installation
```bash
pip install n8npy-client
```

## Usage
```python
from n8n_api import N8nClient

client = N8nClient()
print(client.list_workflows(limit=10))
```

## Development
See repository documentation for details.
