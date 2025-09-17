"""Configuration settings for OnchFS.

This module contains network configurations, contract addresses, and other
constants used throughout the OnchFS library.
"""

from enum import Enum
from typing import Dict


class Network(Enum):
    """Supported blockchain networks for OnchFS operations."""

    MAINNET = "https://rpc.tzkt.io/mainnet"
    GHOSTNET = "https://ghostnet.tezos.ecadinfra.com"
    LOCALNET = "http://localhost:20000"


# Default OnchFS contract addresses for each network
DEFAULT_CONTRACTS: Dict[Network, str] = {
    Network.MAINNET: "KT1Ae7dT1gsLw2tRnUMXSCmEyF74KVkM6LUo",
    Network.GHOSTNET: "KT1FA8AGGcJha6S6MqfBUiibwTaYhK8u7s9Q",
    Network.LOCALNET: "",  # To be set for local development
}

# Content store contract addresses for chunk existence checks
CONTENT_STORE_CONTRACTS: Dict[Network, str] = {
    Network.MAINNET: "KT1JySSNRfQeRzrkZJypyoHDBRDaTbtTYAq1",
    Network.GHOSTNET: "KT1TGsvdj2m3JA3RmMGekRYHnK7Ygkje7Xbt",
    Network.LOCALNET: "",  # To be set for local development
}

# Inode type identifiers for hashing
INODE_BYTE_IDENTIFIER = {
    "FILE": b"\x01",
    "DIRECTORY": b"\x00",
}

# Default chunk size for file splitting (16KB)
DEFAULT_CHUNK_SIZE = 16384

# MIME type mappings for common file extensions
MIME_TYPES = {
    ".html": "text/html",
    ".css": "text/css",
    ".js": "application/javascript",
    ".json": "application/json",
    ".txt": "text/plain",
    ".md": "text/markdown",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
    ".pdf": "application/pdf",
    ".zip": "application/zip",
}
