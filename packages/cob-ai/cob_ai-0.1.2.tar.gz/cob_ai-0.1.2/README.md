# COB AI

Python client for the COB SharePoint search API.

## Installation

```bash
pip install cob-ai
```

## Usage

```python
from cob_ai import COB

# Initialize the client
client = COB(apikey="your-api-key", apiurl="https://your-api-url.com")

# Search SharePoint documents
results = client.search("your search query", top_n=10)
print(results)

# Trigger synchronization
sync_status = client.sync()
print(sync_status)

# Check sync status
status = client.status()
print(status)
```

## Configuration

You can configure the client using environment variables:

- `COB_APIKEY`: Your API key for authentication

## Requirements

- Python 3.8+
- requests
- attrs

## License

MIT License