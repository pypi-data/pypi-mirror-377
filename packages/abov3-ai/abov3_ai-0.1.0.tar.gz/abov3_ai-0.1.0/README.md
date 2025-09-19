# ABOV3 AI Python SDK

[![PyPI version](https://img.shields.io/pypi/v/abov3-ai.svg)](https://pypi.org/project/abov3-ai/)
[![Python versions](https://img.shields.io/pypi/pyversions/abov3-ai.svg)](https://pypi.org/project/abov3-ai/)
[![Documentation](https://img.shields.io/badge/docs-abov3.ai-blue)](https://docs.abov3.ai)

The official Python SDK for **ABOV3 AI** - the advanced code generation and AI development framework.

## Installation

```bash
pip install abov3-ai
```

## Quick Start

```python
from abov3 import Abov3Client

# Initialize the client
client = Abov3Client(
    api_key="your-api-key",
    base_url="https://api.abov3.ai"  # Optional, defaults to production
)

# Create a session
session = await client.sessions.create(
    model="claude-3-opus",
    system_prompt="You are a helpful coding assistant"
)

# Send a message
response = await client.messages.create(
    session_id=session.id,
    content="Write a Python function to calculate fibonacci numbers"
)

print(response.content)
```

## Features

- 🚀 **Full API Coverage** - Complete access to all ABOV3 AI capabilities
- 🔒 **Type Safety** - Full type hints and runtime validation with Pydantic
- ⚡ **Async Support** - Built on httpx for high-performance async operations
- 🔄 **Auto Retry** - Automatic retry with exponential backoff
- 📊 **Streaming** - Support for streaming responses
- 🧪 **Well Tested** - Comprehensive test coverage

## Streaming Responses

```python
async with client.messages.stream(
    session_id=session.id,
    content="Generate a long story"
) as stream:
    async for chunk in stream:
        print(chunk.content, end="")
```

## Error Handling

```python
from abov3.exceptions import Abov3Error, RateLimitError

try:
    response = await client.messages.create(...)
except RateLimitError as e:
    print(f"Rate limited: {e}")
    # Wait and retry
except Abov3Error as e:
    print(f"API error: {e}")
```

## Configuration

### Environment Variables

```bash
export ABOV3_API_KEY="your-api-key"
export ABOV3_BASE_URL="https://api.abov3.ai"  # Optional
```

### Code Configuration

```python
client = Abov3Client(
    api_key="your-api-key",
    timeout=30.0,  # Request timeout in seconds
    max_retries=3,  # Maximum retry attempts
    proxy="http://proxy.example.com:8080"  # Optional proxy
)
```

## Available Models

- `claude-3-opus` - Most capable model for complex tasks
- `claude-3-sonnet` - Balanced performance and speed
- `gpt-4-turbo` - OpenAI's most capable model
- `gpt-3.5-turbo` - Fast and cost-effective

## API Reference

### Sessions

```python
# Create a session
session = await client.sessions.create(model="claude-3-opus")

# Get session
session = await client.sessions.get(session_id)

# List sessions
sessions = await client.sessions.list(limit=10)

# Delete session
await client.sessions.delete(session_id)
```

### Messages

```python
# Send message
message = await client.messages.create(
    session_id=session_id,
    content="Your message here"
)

# Stream message
async with client.messages.stream(...) as stream:
    async for chunk in stream:
        process(chunk)
```

### Files

```python
# Upload file
file = await client.files.upload(
    file_path="./document.pdf",
    purpose="analysis"
)

# List files
files = await client.files.list()

# Delete file
await client.files.delete(file_id)
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/fajardofahad/abov3-sdk-python.git
cd abov3-sdk-python

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src tests
ruff check src tests

# Type checking
mypy src
```

## Support

- **Documentation**: [https://docs.abov3.ai](https://docs.abov3.ai)
- **Website**: [https://www.abov3.ai](https://www.abov3.ai)
- **GitHub**: [https://github.com/fajardofahad/abov3-sdk-python](https://github.com/fajardofahad/abov3-sdk-python)
- **Issues**: [GitHub Issues](https://github.com/fajardofahad/abov3-sdk-python/issues)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## About ABOV3

ABOV3 AI is an advanced code generation framework that revolutionizes how developers interact with AI. Visit [abov3.ai](https://www.abov3.ai) to learn more.