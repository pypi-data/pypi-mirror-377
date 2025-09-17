# OnchFS Python Client

Python client for the OnchFS (On-Chain File System) protocol on Tezos blockchain.

## Installation

```bash
pip install pyonchfs
```

## Command Line Interface

OnchFS includes a powerful CLI for easy file uploads and downloads:

### Setup

```bash
# Set your Tezos secret key (required for uploads)
export TZ_SK="edsk3oYfrKXpqHgXTWXm7YKzGAKszVQ7ehh9PViFdJc83pV7VDiJnB"
```

### Upload Files

```bash
# Upload a single file
onchfs upload myfile.txt
# or
python -m onchfs upload myfile.txt

# Upload a directory with compression
onchfs upload ./my-website --compress

# Upload to mainnet (defaults to ghostnet)
onchfs upload ./docs --network mainnet

# Skip confirmation prompt
onchfs upload ./data --yes
```

### Download Files

```bash
# Download from hash
onchfs download 6a89c4e7d38f8ffc1ddba97037aa83181b56326bf5e1f5b95070ba7789813832 ./downloaded
# or
python -m onchfs download 6a89c4e7d38f8ffc1ddba97037aa83181b56326bf5e1f5b95070ba7789813832 ./downloaded

# Download from onchfs:// URL
onchfs download onchfs://6a89c4e7d38f8ffc1ddba97037aa83181b56326bf5e1f5b95070ba7789813832 ./downloaded
```

### CLI Options

```bash
onchfs --help                    # Show help
python -m onchfs --help          # Alternative way
onchfs upload --help             # Upload help
onchfs download --help           # Download help

# Global options
--network {mainnet,ghostnet,localnet}  # Choose network (default: ghostnet)

# Upload options
--compress                       # Enable compression
--chunk-size SIZE               # Set chunk size in bytes (default: 16384)
--yes, -y                       # Skip confirmation prompt
```

## Python API

### Quick Start

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

### Upload a Whole Directory (Improved API)

```python
import os
from onchfs import OnchfsUploader, Network, OnchfsPrepareOptions
from pytezos import pytezos

# Load Tezos secret key from environment
secret_key = os.getenv('TZ_SK')
if not secret_key:
    raise ValueError("TZ_SK environment variable not set")

# Initialize PyTezos client with secret key
pytezos_client = pytezos.using(
    key=secret_key,
    shell=Network.GHOSTNET.value  # or your preferred RPC endpoint
)

# Initialize OnchFS uploader with network (contracts auto-resolved!)
uploader = OnchfsUploader(pytezos_client, Network.GHOSTNET)

# Prepare directory for upload
directory_path = "./my_website"  # Path to your directory
directory_inode = uploader.prepare_directory(
    directory_path,
    options=OnchfsPrepareOptions(compress=True)
)

# Get the directory hash (this is what you'll use to access files)
directory_hash = uploader.get_directory_hash(directory_inode)
print(f"Directory hash: {directory_hash}")

# Estimate upload cost
cost_estimate = uploader.estimate_cost(directory_inode)
print(f"Estimated cost: {cost_estimate}")

# Upload to OnchFS (contract address automatically resolved!)
print("Starting upload...")
result = uploader.upload_directory(directory_inode)

print(f"Upload operation hash: {result.operation_hash}")
print(f"Your files are now accessible at: onchfs://{result.directory_hash}")
```

**Environment Setup:**

```bash
# Set your Tezos secret key
export TZ_SK="edsk..."  # Your Tezos secret key

# Run your upload script
python upload_directory.py
```

## API

### OnchfsUploader (Recommended)

```python
from onchfs import OnchfsUploader, Network
from pytezos import pytezos

# Initialize with automatic contract resolution
uploader = OnchfsUploader(pytezos_client, Network.GHOSTNET)

# Upload without specifying contract address
result = uploader.upload_directory(directory_inode)
```

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
