"""OnchFS - Python implementation of OnchFS (On-Chain File System).

A Python library for interacting with the OnchFS protocol on Tezos blockchain.
Provides functionality for uploading, downloading, and managing files stored
on-chain.

Typical usage example:

  from onchfs import OnchfsClient, Network

  client = OnchfsClient(network=Network.MAINNET)
  result = client.upload_file("example.txt")
  print(f"Uploaded with hash: {result.directory_hash}")
"""

from .client import OnchfsClient
from .config import Network, DEFAULT_CONTRACTS
from .types import FileInode, DirectoryInode, IFile, OnchfsPrepareOptions
from .resolver import OnchfsResolver
from .uploader import OnchfsUploader

__version__ = "0.1.2"
__all__ = [
    "OnchfsClient",
    "OnchfsResolver",
    "OnchfsUploader",
    "Network",
    "DEFAULT_CONTRACTS",
    "FileInode",
    "DirectoryInode",
    "IFile",
    "OnchfsPrepareOptions",
]
