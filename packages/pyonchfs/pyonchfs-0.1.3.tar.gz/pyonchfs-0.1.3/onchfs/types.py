"""Type definitions for OnchFS.

This module contains all the data classes and type definitions used throughout
the OnchFS library for representing files, directories, and operation results.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Union


@dataclass
class FileChunk:
    """Represents a chunk of file data.

    Attributes:
        bytes: The raw bytes of the chunk.
        hash: The hash of the chunk bytes.
    """

    bytes: bytes
    hash: bytes


@dataclass
class FileInode:
    """Represents a file inode with chunks and metadata.

    Attributes:
        type: The inode type, always "file".
        chunks: List of file chunks that make up the file.
        cid: Content identifier for the file.
        metadata: Encoded metadata for the file.
    """

    type: str = "file"
    chunks: List[FileChunk] = None
    cid: bytes = None
    metadata: bytes = None

    def __post_init__(self):
        if self.chunks is None:
            self.chunks = []


@dataclass
class DirectoryInode:
    """Represents a directory inode with files.

    Attributes:
        type: The inode type, always "directory".
        cid: Content identifier for the directory.
        files: Dictionary mapping filenames to their inodes.
    """

    type: str = "directory"
    cid: bytes = None
    files: Dict[str, Union["DirectoryInode", "FileInode"]] = None

    def __post_init__(self):
        if self.files is None:
            self.files = {}


# Union type for any inode
INode = Union[DirectoryInode, FileInode]


@dataclass
class IFile:
    """Represents a file with path and content.

    Attributes:
        path: The file path/name.
        content: The raw file content as bytes.
    """

    path: str
    content: bytes


@dataclass
class PrepareDirectoryFile:
    """Temporary file representation during directory preparation.

    Attributes:
        type: The node type, always "file".
        name: The filename.
        content: The file content as bytes.
        parent: Reference to parent directory node.
        inode: The prepared file inode.
    """

    type: str = "file"
    name: str = ""
    content: bytes = b""
    parent: Optional["PrepareDirectoryDir"] = None
    inode: Optional[FileInode] = None


@dataclass
class PrepareDirectoryDir:
    """Temporary directory representation during directory preparation.

    Attributes:
        type: The node type, always "directory".
        files: Dictionary of child files and directories.
        parent: Reference to parent directory node.
        inode: The prepared directory inode.
    """

    type: str = "directory"
    files: Dict[str, Union["PrepareDirectoryFile", "PrepareDirectoryDir"]] = (
        None
    )
    parent: Optional["PrepareDirectoryDir"] = None
    inode: Optional[DirectoryInode] = None

    def __post_init__(self):
        if self.files is None:
            self.files = {}


# Union type for prepare nodes
PrepareDirectoryNode = Union[PrepareDirectoryFile, PrepareDirectoryDir]


@dataclass
class OnchfsPrepareOptions:
    """Options for preparing files for upload.

    Attributes:
        chunk_size: Size in bytes for file chunks.
        compress: Whether to compress file content.
    """

    chunk_size: int = 16384
    compress: bool = True


@dataclass
class UploadResult:
    """Result of an upload operation.

    Attributes:
        directory_hash: Hash of the uploaded directory.
        file_hashes: Dictionary mapping filenames to their hashes.
        operation_hash: Hash of the blockchain operation.
        total_size: Total size of uploaded data in bytes.
        compressed_size: Size after compression in bytes.
    """

    directory_hash: str
    file_hashes: Dict[str, str]
    operation_hash: str
    total_size: int
    compressed_size: int
