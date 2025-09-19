# Zymmr Client

A Python client library for interacting with the Zymmr Project Management API.

## Features

- Simple and intuitive API interface
- Authentication handling
- Full CRUD operations for projects, tasks, and resources
- Error handling and retry mechanisms
- Type hints for better development experience

## Installation

```bash
pip install zymmr-client
```

## Quick Start

```python
from zymmr_client import ZymmrClient

# Initialize the client
client = ZymmrClient(
    base_url="https://your-zymmr-instance.com",
    api_key="your-api-key"
)

# Get all projects
projects = client.projects.list()

# Create a new task
task = client.tasks.create({
    "title": "My Task",
    "project_id": "project-123",
    "status": "open"
})
```

## Development

This project uses `uv` for dependency management:

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Build package
uv build
```

## License

MIT License
