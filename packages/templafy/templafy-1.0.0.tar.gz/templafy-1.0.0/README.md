# Templafy API Client

A Python client for the Templafy API using openapi-python-client for type-safe, modern Python API access.

## Overview

This package provides a Python client for the Templafy API, allowing you to programmatically access templates, documents, images, and other assets in your Templafy workspace.

## Installation

```bash
pip install -e .
```

## Quick Start

### Basic Usage

```python
from templafy import AuthenticatedClient
from templafy.api import spaces, documents

# Initialize client
client = AuthenticatedClient(
    base_url="https://your-tenant.api.templafy.com/v3",
    token="your-api-token"
)

# Use with context manager (recommended)
with client as client:
    # List all spaces
    all_spaces = spaces.get_spaces(client=client)
    print(f"Found {len(all_spaces)} spaces")
    
    # List documents  
    all_documents = documents.get_documents(client=client)
    print(f"Found {len(all_documents)} documents")
```

### Available API Endpoints

The client provides access to the following Templafy API resources:

- **Spaces** - Workspace/tenant management
- **Libraries** - Library management across spaces  
- **Documents** - Document template operations and generation
- **Folders** - Folder structure management
- **Images** - Image asset management
- **Slides** - PowerPoint slide management
- **Spreadsheets** - Excel template operations
- **Links** - Link asset management

### Models

The client includes type-safe models for all API resources:

```python
from templafy import Space, Document, Library, Image

# Models are automatically used when calling API methods
spaces = spaces.get_spaces(client=client)
for space in spaces:
    print(f"Space: {space.name} (ID: {space.id})")
```

## API Structure

```
templafy/
├── client.py           # Base Client and AuthenticatedClient classes
├── models/             # Type-safe models for all schemas
│   ├── space.py        # Space-related models
│   ├── document.py     # Document-related models
│   ├── library.py      # Library-related models
│   └── ...
├── api/                # API endpoint modules by resource
│   ├── spaces.py       # Spaces API endpoints
│   ├── documents.py    # Documents API endpoints
│   ├── libraries.py    # Libraries API endpoints
│   └── ...
├── types.py            # Common type definitions
└── errors.py           # Error classes and exceptions
```

## Error Handling

The client provides specific error classes for different types of API errors:

```python
from templafy.errors import (
    AuthenticationError,
    AuthorizationError, 
    NotFoundError,
    ValidationError,
    RateLimitError,
    ServerError
)

try:
    documents = documents.get_documents(client=client)
except AuthenticationError:
    print("API token is invalid")
except AuthorizationError:
    print("Insufficient permissions")
except NotFoundError:
    print("Resource not found")
except RateLimitError:
    print("Rate limit exceeded")
```

## Development

### Dependencies

This project requires Python 3.12+ and the following dependencies:

- `httpx` - HTTP client
- `pydantic` - Data validation and settings management
- `typing-extensions` - Additional typing features

### Testing

```bash
python -m pytest tests/ -v
```

### Code Quality

The project uses `ruff` for linting and formatting:

```bash
ruff check src/templafy --fix
ruff format src/templafy
```

## Contributing

1. Install development dependencies
2. Make your changes
3. Run tests and linting
4. Submit a pull request

## License

MIT License - see LICENSE file for details.
