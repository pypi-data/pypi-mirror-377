# OnchFS Python Client

Python client for the OnchFS (On-Chain File System) protocol on Tezos blockchain.

## Installation

```bash
pip install pyonchfs
```

## Quick Start

### Download Files

```python
from onchfs import OnchfsClient, Network

client = OnchfsClient(network=Network.MAINNET)

# Download directory
directory_hash = "f8020273fba472a3e87baf6eb0f3929915edabace0fa409a261c4c4fa6684b21"
files = client.download_directory(directory_hash, "downloaded/")

# Get specific file
content = client.get_file(directory_hash, "index.html")
```

### Prepare Files for Upload

```python
from onchfs import OnchfsClient, IFile, OnchfsPrepareOptions

client = OnchfsClient()

# Prepare files
files = [
    IFile(path="hello.txt", content=b"Hello, OnchFS!"),
    IFile(path="data.json", content=b'{"message": "test"}')
]

directory_inode = client.prepare_files(files)
directory_hash = client.get_directory_hash(directory_inode)
```

## API

### OnchfsClient

```python
client = OnchfsClient(
    network=Network.MAINNET,  # MAINNET, GHOSTNET, LOCALNET
    contract_address=None,    # Optional custom contract
    pytezos_client=None      # Optional PyTezos client
)
```

**Download Methods:**

- `download_directory(hash, target_dir)` - Download all files
- `get_file(hash, filename)` - Get file content
- `get_file_metadata(hash, filename)` - Get file metadata
- `list_directory(hash)` - List directory contents

**Preparation Methods:**

- `prepare_files(files, options=None)` - Prepare files for upload
- `prepare_directory(path, options=None)` - Prepare directory
- `estimate_upload_cost(directory_inode)` - Estimate costs
- `get_directory_hash(directory_inode)` - Get hash

### Types

```python
from onchfs import IFile, OnchfsPrepareOptions

file = IFile(path="example.txt", content=b"content")
options = OnchfsPrepareOptions(chunk_size=16384, compress=True)
```

## Examples

Run the included examples:

```bash
python examples/download_example.py
python examples/prepare_example.py
```

## Contract Addresses

- **Mainnet**: `KT1Ae7dT1gsLw2tRnUMXSCmEyF74KVkM6LUo`
- **Ghostnet**: `KT1FA8AGGcJha6S6MqfBUiibwTaYhK8u7s9Q`
