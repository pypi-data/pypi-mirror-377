"""Utility functions for OnchFS.

This module contains various utility functions used throughout the OnchFS
library for hashing, compression, file type detection, and data manipulation.
"""

import gzip
import io
import os
from typing import List

from pytezos.crypto.keccak import Keccak256

from .config import MIME_TYPES, DEFAULT_CHUNK_SIZE, INODE_BYTE_IDENTIFIER


def keccak256(data: bytes) -> bytes:
    """Compute Keccak-256 hash of data using pytezos.

    Args:
        data: The bytes to hash.

    Returns:
        The Keccak-256 hash as bytes.
    """
    return Keccak256(data).digest()


def chunk_bytes(
    data: bytes, chunk_size: int = DEFAULT_CHUNK_SIZE
) -> List[bytes]:
    """Split bytes into chunks of specified size.

    Args:
        data: The bytes to split into chunks.
        chunk_size: Size of each chunk in bytes.

    Returns:
        List of byte chunks.
    """
    return [data[i : i + chunk_size] for i in range(0, len(data), chunk_size)]


def compress_data(data: bytes) -> bytes:
    """Compress data using gzip with deterministic output.

    Args:
        data: The bytes to compress.

    Returns:
        Compressed data as bytes.
    """
    buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=buffer, mode="wb", mtime=0) as gz:
        gz.write(data)
    return buffer.getvalue()


def decompress_data(data: bytes) -> bytes:
    """Decompress gzip data.

    Args:
        data: The compressed bytes to decompress.

    Returns:
        Decompressed data as bytes.
    """
    return gzip.decompress(data)


def get_mime_type(filename: str) -> str:
    """Get MIME type from file extension.

    Args:
        filename: The filename to get MIME type for.

    Returns:
        MIME type string, defaults to 'application/octet-stream'.
    """
    _, ext = os.path.splitext(filename.lower())
    return MIME_TYPES.get(ext, "application/octet-stream")


def is_text_file(mime_type: str) -> bool:
    """Check if MIME type represents a text file.

    Args:
        mime_type: The MIME type to check.

    Returns:
        True if the MIME type represents a text file.
    """
    return mime_type.startswith("text/") or mime_type in [
        "application/javascript",
        "application/json",
    ]


def encode_filename(filename: str) -> bytes:
    """Encode filename to bytes.

    Args:
        filename: The filename to encode.

    Returns:
        Encoded filename as bytes.
    """
    return filename.encode("utf-8")


def compute_file_hash(content: bytes, metadata: bytes) -> bytes:
    """Compute hash for file following OnchFS specification.

    The hash is computed as: keccak(0x01, keccak(content), keccak(metadata))

    Args:
        content: The file content bytes.
        metadata: The file metadata bytes.

    Returns:
        The computed file hash as bytes.
    """
    content_hash = keccak256(content)
    metadata_hash = keccak256(metadata)
    return keccak256(
        INODE_BYTE_IDENTIFIER["FILE"] + content_hash + metadata_hash
    )


def compute_directory_hash(files_data: bytes) -> bytes:
    """Compute hash for directory with directory identifier.

    Args:
        files_data: The serialized directory files data.

    Returns:
        The computed directory hash as bytes.
    """
    return keccak256(INODE_BYTE_IDENTIFIER["DIRECTORY"] + files_data)


def bytes_to_hex(data: bytes) -> str:
    """Convert bytes to hex string.

    Args:
        data: The bytes to convert.

    Returns:
        Hex string representation.
    """
    return data.hex()


def hex_to_bytes(hex_str: str) -> bytes:
    """Convert hex string to bytes.

    Args:
        hex_str: The hex string to convert.

    Returns:
        Bytes representation.

    Raises:
        ValueError: If the hex string is invalid.
    """
    return bytes.fromhex(hex_str)


def should_compress(mime_type: str, size: int) -> bool:
    """Determine if file should be compressed based on type and size.

    Args:
        mime_type: The MIME type of the file.
        size: The size of the file in bytes.

    Returns:
        True if the file should be compressed.
    """
    # Don't compress already compressed formats
    compressed_types = {
        "image/png",
        "image/jpeg",
        "image/gif",
        "application/zip",
        "application/gzip",
        "video/",
        "audio/",
    }

    if any(mime_type.startswith(ct) for ct in compressed_types):
        return False

    # Only compress files larger than 100 bytes
    return size > 100


def validate_directory_hash(hash_str: str) -> bool:
    """Validate that a string is a valid directory hash.

    Args:
        hash_str: The hash string to validate.

    Returns:
        True if the hash string is valid.
    """
    try:
        # Should be 64 character hex string (32 bytes)
        if len(hash_str) != 64:
            return False
        bytes.fromhex(hash_str)
        return True
    except ValueError:
        return False
