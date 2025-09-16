# PeerTube Python API Client

Modern Python client library for the PeerTube API using openapi-python-client. Provides type-safe, well-structured clients with both synchronous and asynchronous support.

## Overview

This package provides a comprehensive Python client for the PeerTube API, automatically generated from the official OpenAPI specification. It uses `httpx` for HTTP operations and `attrs` for type-safe data classes.

## Installation

```bash
pip install peertube
```

## Quick Start

### Basic Client Usage

```python
from peertube import Client
from peertube.api.video import get_categories, get_video

# Create an unauthenticated client for public endpoints
client = Client(base_url="https://your-peertube-instance.com")

# Get video categories
categories = get_categories.sync(client=client)
print(f"Available categories: {list(categories.keys())}")

# Get specific video details  
video = get_video.sync(client=client, id="video-uuid")
print(f"Video: {video.name}")
```

### Authenticated Client Usage

```python
from peertube import AuthenticatedClient
from peertube.api.my_user import get_user

# Create authenticated client for protected endpoints
auth_client = AuthenticatedClient(
    base_url="https://your-peertube-instance.com",
    token="your-api-token"
)

# Get current user information
user = get_user.sync(client=auth_client)
print(f"Logged in as: {user.username}")
```

### Asynchronous Usage

```python
import asyncio
from peertube import Client
from peertube.api.video import get_categories, get_languages

async def get_video_metadata():
    client = Client(base_url="https://your-peertube-instance.com")
    
    async with client as async_client:
        # Run multiple requests concurrently
        categories, languages = await asyncio.gather(
            get_categories.asyncio(client=async_client),
            get_languages.asyncio(client=async_client)
        )
        
        return categories, languages

# Run async function
categories, languages = asyncio.run(get_video_metadata())
```

### Advanced Configuration

```python
from peertube import AuthenticatedClient

# Client with custom configuration
client = AuthenticatedClient(
    base_url="https://your-peertube-instance.com",
    token="your-api-token",
    timeout=30.0,
    verify_ssl=True,  # Set to False only for testing
    follow_redirects=True,
    headers={"User-Agent": "MyPeerTubeApp/1.0"},
    httpx_args={
        "proxies": {"https://": "https://proxy.example.com"}
    }
)
```

### Response Handling

```python
from peertube.api.video import get_video

# Simple response (just the data)
video = get_video.sync(client=client, id="video-uuid")

# Detailed response (includes status code, headers, etc.)
response = get_video.sync_detailed(client=client, id="video-uuid")
if response.status_code == 200:
    video = response.parsed
    print(f"Status: {response.status_code}")
    print(f"Headers: {response.headers}")
else:
    print(f"Error: {response.status_code}")
```

## API Coverage

The client provides access to all PeerTube API endpoints organized by functionality:

### Core API Modules
- **video**: Video management (get, delete, categories, languages, licenses)
- **videos**: Video listing and import operations
- **accounts**: Account and user information
- **users**: User management and administration
- **session**: Authentication and session management
- **search**: Video, channel, and playlist search
- **my_user**: Current user profile and settings
- **video_channels**: Video channel management
- **video_playlists**: Playlist operations

### Additional Modules
- **config**: Instance configuration
- **register**: User registration
- **my_subscriptions**: Subscription management
- **my_notifications**: Notification handling
- **video_comments**: Comment operations
- **live_videos**: Live streaming
- **stats**: Instance statistics

## Error Handling

```python
from peertube.errors import UnexpectedStatus
from peertube.api.video import get_video

try:
    video = get_video.sync(client=client, id="invalid-uuid")
except UnexpectedStatus as e:
    print(f"API error: {e.status_code} - {e.content}")
```

## Type Safety

The client provides full type annotations and IDE auto-completion:

```python
from peertube.models import Video
from peertube.types import Response

# Type-safe response handling
response: Response[Video] = get_video.sync_detailed(client=client, id="uuid")
video: Video = response.parsed  # Fully typed video object
```

## Requirements

- Python 3.10+
- httpx >= 0.23.0
- attrs >= 22.2.0

## Development

This package is automatically generated from the PeerTube OpenAPI specification using openapi-python-client.

### Regenerating the Client

To update the client when the PeerTube API changes:

```bash
# Install development dependencies
pip install openapi-python-client

# Update the OpenAPI spec in assets/openapi.json
# Then regenerate the client
openapi-python-client generate --path assets/openapi.json --output-path src/peertube --meta none --overwrite
```

### Testing

```bash
# Run all tests
pytest

# Run specific test files
pytest tests/test_client_generation.py -v
pytest tests/test_api_functions.py -v
```

## Examples

See the `examples/` directory for complete usage examples:

- `examples/client_usage.py` - Basic client usage patterns
- More examples coming soon...

## Features

### Generated Client Benefits
- **Type Safety**: Full type annotations with proper typing support
- **Dual Clients**: `Client` (unauthenticated) and `AuthenticatedClient` (with token)
- **Async Support**: Both sync and async methods for all endpoints
- **httpx Based**: Uses modern httpx library for HTTP requests
- **Context Manager**: Proper resource management with `with` statements
- **Customizable**: Supports custom timeout, SSL settings, headers, cookies

### API Endpoint Coverage
- ✅ **Video Management**: Get, list, upload, delete videos
- ✅ **Video Metadata**: Categories, languages, licenses
- ✅ **Search**: Videos, channels, playlists
- ✅ **User Management**: Registration, profiles, settings
- ✅ **Authentication**: Login, logout, token management
- ✅ **Video Channels**: Channel operations and management
- ✅ **Playlists**: Playlist creation and management
- ✅ **Comments**: Video comment operations
- ✅ **Live Streaming**: Live video operations
- ✅ **Moderation**: Content moderation tools
- ✅ **Instance**: Configuration and statistics

## Contributing

This project follows modern Python development practices:

- Type hints for all functions
- Pydantic models for data validation
- Comprehensive error handling
- 100-character line length limit
- pytest for testing

## License

MIT License
