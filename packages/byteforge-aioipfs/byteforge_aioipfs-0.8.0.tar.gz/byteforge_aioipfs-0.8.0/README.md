# byteforge-aioipfs

[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License: LGPL v3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)

An asynchronous Python client library for IPFS (InterPlanetary File System) using the RPC API. Compatible with [kubo](https://github.com/ipfs/kubo) (go-ipfs) versions 0.11.0 through 0.32.0.

## Why This Fork?

This project is a fork of the original [aioipfs](https://gitlab.com/cipres/aioipfs) library, which hadn't been updated since early 2024 and had several issues that needed addressing. I created this enhanced version to provide:

### 🔧 **Fixed Critical Issues**
- **Resolved test failures** - The original project had broken unit tests due to deprecated Python features and incompatible library usage
- **Fixed aiohttp compatibility** - Corrected improper use of `BytesIOPayload` that caused crashes with file operations
- **Eliminated deprecation warnings** - Updated from deprecated `distutils` to modern `packaging.version` library
- **Modernized dependency chain** - Upgraded Google Cloud and protobuf dependencies to eliminate datetime warnings

### 🚀 **Enhanced Development Experience**
- **Working test suite** - All 50+ unit tests now pass reliably
- **Clean requirements files** - Added `requirements.txt` and `requirements-dev.txt` for better dependency management
- **Updated documentation** - Comprehensive README and development instructions
- **Modern Python practices** - Code follows current Python standards and best practices

### 🛠 **Improved Maintenance**
- **Dependency updates** - Upgraded outdated packages to their latest compatible versions
- **Better error handling** - Fixed undefined variable references and missing imports
- **Debug capabilities** - Added debugging tools for troubleshooting IPFS operations
- **Future-proof** - Updated to work with the latest Python versions and IPFS releases

All changes maintain full backward compatibility while significantly improving reliability and developer experience.

## Features

- 🚀 **Fully async/await support** - Built on aiohttp for high performance
- 🌐 **Multiaddr connections** - Connect using multiaddr format (`/ip4/127.0.0.1/tcp/5001`)
- 🔐 **Multiple authentication methods** - Basic Auth and Bearer token support
- 📦 **Comprehensive API coverage** - Support for all major IPFS RPC endpoints
- 🔄 **Streaming operations** - Handle large files efficiently with async generators
- 📨 **PubSub messaging** - Full publish/subscribe functionality
- 📊 **DAG operations** - Work with Directed Acyclic Graphs
- 📌 **Pin management** - Control content persistence
- 🚗 **CAR file support** - Content Addressable aRchive handling (optional)
- 🧰 **Bohort REPL tool** - Interactive IPFS shell (optional)

## Installation

### Installation from Source
```bash
git clone https://github.com/jmazzahacks/byteforge-aioipfs.git
cd byteforge-aioipfs
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Basic installation
pip install -r requirements.txt

# Or with development dependencies
pip install -r requirements-dev.txt

# Or install in development mode with optional features
pip install -e ".[orjson,car,bohort,dev]"
```


## Quick Start

### Basic Usage
```python
import asyncio
import aioipfs

async def main():
    # Connect to local IPFS node
    async with aioipfs.AsyncIPFS() as client:
        # Add a file
        async for added in client.add('/path/to/file.txt'):
            print(f"Added: {added['Hash']}")
            file_hash = added['Hash']

        # Retrieve file content
        content = await client.cat(file_hash)
        print(content.decode())

asyncio.run(main())
```

### Custom Connection
```python
import aioipfs

# Using multiaddr
client = aioipfs.AsyncIPFS(maddr='/ip4/127.0.0.1/tcp/5001')

# Using host/port
client = aioipfs.AsyncIPFS(host='localhost', port=5001)

# With HTTPS
client = aioipfs.AsyncIPFS(host='my-ipfs-node.com', port=5001, scheme='https')
```

### Authentication
```python
import aioipfs

# Basic Authentication
client = aioipfs.AsyncIPFS(
    auth=aioipfs.BasicAuth('username', 'password')
)

# Bearer Token
client = aioipfs.AsyncIPFS(
    auth=aioipfs.BearerAuth('your-secret-token')
)
```

### Working with Directories
```python
async with aioipfs.AsyncIPFS() as client:
    # Add directory recursively
    async for added in client.add('/path/to/directory', recursive=True):
        print(f"{added['Name']}: {added['Hash']}")

    # Include hidden files
    async for added in client.add('/path/to/directory',
                                 recursive=True, hidden=True):
        print(f"{added['Name']}: {added['Hash']}")
```

## API Overview

The client provides access to all major IPFS APIs:

### Core Operations
```python
# Add content
async for result in client.add('file.txt'): pass
async for result in client.add_bytes(b'data'): pass
async for result in client.add_str('text'): pass
async for result in client.add_json({'key': 'value'}): pass

# Retrieve content
content = await client.cat('QmHash')
await client.get('QmHash', '/output/path')

# Node information
info = await client.id()
version = await client.version()
```

### Pinning
```python
# Pin content
await client.pin.add('QmHash')
pins = await client.pin.ls()
await client.pin.rm('QmHash')
```

### PubSub
```python
# Subscribe to topic
async for message in client.pubsub.sub('my-topic'):
    print(message)

# Publish message
await client.pubsub.pub('my-topic', b'Hello World!')
```

### DAG Operations
```python
# Add DAG node
dag_result = await client.dag.put({'data': 'value'})

# Get DAG node
dag_data = await client.dag.get('dag-cid')

# Export/Import CAR files
car_data = await client.dag.car_export('cid')
result = await client.dag.car_import(car_data)
```

### Files API (MFS - Mutable File System)
```python
# List directory
files = await client.files.ls('/')

# Read file
content = await client.files.read('/path/file.txt')

# Write file
await client.files.write('/path/file.txt', b'data')

# Create directory
await client.files.mkdir('/new/directory')
```

## Configuration

### Environment Variables
- `IPFS_API_ADDR` - Default API address (e.g., `/ip4/127.0.0.1/tcp/5001`)

### Client Options
```python
client = aioipfs.AsyncIPFS(
    host='127.0.0.1',          # IPFS API host
    port=5001,                 # IPFS API port
    scheme='http',             # http or https
    timeout=60,                # Request timeout in seconds
    auth=None,                 # Authentication object
    headers=None,              # Additional HTTP headers
    connector=None,            # Custom aiohttp connector
)
```

## Error Handling

```python
import aioipfs

async with aioipfs.AsyncIPFS() as client:
    try:
        result = await client.cat('invalid-hash')
    except aioipfs.APIError as e:
        print(f"API Error: {e}")
    except aioipfs.InvalidNodeAddressError as e:
        print(f"Connection Error: {e}")
```

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=aioipfs --cov-report=html

# Run specific test
pytest tests/test_client.py::TestAsyncIPFS::test_basic
```

## Development

This project uses:
- **pytest** for testing with async support
- **ruff** for linting
- **mypy** for type checking
- **black** for code formatting

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run linting
ruff check aioipfs

# Run type checking
mypy aioipfs

# Format code
black aioipfs tests
```

## Compatibility

- **Python**: 3.6, 3.7, 3.8, 3.9, 3.10, 3.11, 3.12
- **IPFS (kubo)**: 0.11.0 - 0.32.0
- **aiohttp**: >= 3.7.4

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the GNU Lesser General Public License v3.0 (LGPLv3). See the [LICENSE](LICENSE) file for details.

## Links

- **Original Repository**: https://gitlab.com/cipres/aioipfs
- **Documentation**: https://aioipfs.readthedocs.io
- **IPFS**: https://ipfs.tech/

## Acknowledgments

This is a fork of the original aioipfs project by cipres, enhanced with modern Python practices, comprehensive testing, and improved dependency management.