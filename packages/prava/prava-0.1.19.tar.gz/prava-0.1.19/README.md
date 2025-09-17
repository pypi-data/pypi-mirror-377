# Prava Python SDK

API for Labor - skilled digital work via computer-use agents.

## Install

```
pip install prava
```

## Usage

```python
from prava import Prava
import os

client = Prava(api_key=os.getenv("PRAVA_API_KEY"))

task = client.tasks.create({
    "workflow": "quickbooks_sync",
    "data": {
        "invoices_folder": "s3://acme-invoices/march-2025/",
        "vendor_mapping": "existing_vendors.csv"
    },
    "max_price": 5000,    # Don't pay more than $50
    "deadline": "2025-09-15T17:00:00Z"
})

# Get results
result = client.tasks.get(task["id"])
print(f"Status: {result['status']}")
```

## Configuration

- `api_key`: Explicit API key, or set `PRAVA_API_KEY` env var.
- `timeout`: Request timeout seconds (default 60).

## License

MIT

