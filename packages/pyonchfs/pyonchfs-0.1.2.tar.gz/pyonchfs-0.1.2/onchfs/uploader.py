"""OnchFS uploader for preparing and uploading files to the blockchain.

This module provides the OnchfsUploader class for preparing files and
directories for upload to the OnchFS protocol on Tezos blockchain.
"""

import os
import urllib.parse
from pathlib import Path
from typing import Dict, List

from hpack import Encoder

from .config import (
    CONTENT_STORE_CONTRACTS,
    Network,
    INODE_BYTE_IDENTIFIER,
)
from .types import (
    FileChunk,
    FileInode,
    DirectoryInode,
    IFile,
    PrepareDirectoryFile,
    PrepareDirectoryDir,
    UploadResult,
    OnchfsPrepareOptions,
)
from .utils import (
    chunk_bytes,
    compress_data,
    get_mime_type,
    should_compress,
    compute_file_hash,
    bytes_to_hex,
    keccak256,
)


class OnchfsUploader:
    """Uploader for preparing and uploading files to OnchFS.

    This class handles the preparation of files and directories for upload
    to the OnchFS protocol, including chunking, compression, and metadata
    encoding.

    Attributes:
        client: PyTezos client instance for blockchain operations.
        network: Network to determine content store contract.
        content_store_address: Address of the content store contract.
    """

    def __init__(self, pytezos_client=None, network: Network = None):
        """Initialize the uploader.

        Args:
            pytezos_client: PyTezos client instance for blockchain operations.
            network: Network to determine content store contract.
        """
        self.client = pytezos_client
        self.network = network
        self.content_store_address = None
        if network and network in CONTENT_STORE_CONTRACTS:
            self.content_store_address = CONTENT_STORE_CONTRACTS[network]

    def _check_chunk_exists(self, chunk_hash: bytes) -> bool:
        """Check if a chunk already exists in the content store.

        Args:
            chunk_hash: The hash of the chunk to check.

        Returns:
            True if chunk exists, False otherwise.
        """
        if not self.client or not self.content_store_address:
            return False

        try:
            # Use the chunk_exists view on the content store contract
            # Pass the chunk hash (bytes) directly to the view
            contract = self.client.contract(self.content_store_address)
            result = contract.chunk_exists(chunk_hash).run_view()
            return result
        except Exception as e:
            # If view call fails, assume chunk doesn't exist
            print(f"Warning: Failed to check chunk existence: {e}")
            return False

    def _check_file_exists(
        self, file_hash: bytes, contract_address: str
    ) -> bool:
        """Check if a file already exists in OnchFS.

        Args:
            file_hash: The hash of the file to check.
            contract_address: OnchFS contract address.

        Returns:
            True if file exists, False otherwise.
        """
        if not self.client:
            return False

        try:
            # Use the read_file view to check if file exists
            contract = self.client.contract(contract_address)
            contract.read_file(file_hash).run_view()
            return True  # If no exception, file exists
        except Exception:
            # If view call fails, file doesn't exist
            return False

    def _check_directory_exists(
        self, directory_hash: bytes, contract_address: str
    ) -> bool:
        """Check if a directory already exists in OnchFS.

        Args:
            directory_hash: The hash of the directory to check.
            contract_address: OnchFS contract address.

        Returns:
            True if directory exists, False otherwise.
        """
        if not self.client:
            return False

        try:
            # Use the read_directory view to check if directory exists
            contract = self.client.contract(contract_address)
            contract.read_directory(directory_hash).run_view()
            return True  # If no exception, directory exists
        except Exception:
            # If view call fails, directory doesn't exist
            return False

    def prepare_file(
        self, file_path: str, options: OnchfsPrepareOptions = None
    ) -> FileInode:
        """Prepare a single file for upload.

        Args:
            file_path: Path to the file to prepare.
            options: Preparation options.

        Returns:
            FileInode ready for upload.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        if options is None:
            options = OnchfsPrepareOptions()

        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Read file content
        with open(path, "rb") as f:
            content = f.read()

        # Get MIME type
        mime_type = get_mime_type(path.name)

        # Prepare metadata headers
        headers = [("content-type", mime_type)]

        # Compress if beneficial
        original_size = len(content)
        if options.compress and should_compress(mime_type, original_size):
            content = compress_data(content)
            headers.append(("content-encoding", "gzip"))

        # Encode metadata using HPACK with fresh encoder for deterministic results
        encoder = Encoder()
        metadata = encoder.encode(headers)

        # Split content into chunks
        chunk_data = chunk_bytes(content, options.chunk_size)
        chunks = []

        for chunk_bytes_data in chunk_data:
            # Use keccak256 for chunk hash
            chunk_hash = keccak256(chunk_bytes_data)
            chunks.append(FileChunk(bytes=chunk_bytes_data, hash=chunk_hash))

        # Compute file CID
        file_cid = compute_file_hash(content, metadata)

        return FileInode(
            type="file", chunks=chunks, cid=file_cid, metadata=metadata
        )

    def prepare_directory(
        self, directory_path: str, options: OnchfsPrepareOptions = None
    ) -> DirectoryInode:
        """Prepare a directory and all its files for upload.

        Args:
            directory_path: Path to the directory to prepare.
            options: Preparation options.

        Returns:
            DirectoryInode ready for upload.

        Raises:
            NotADirectoryError: If the path is not a directory.
        """
        if options is None:
            options = OnchfsPrepareOptions()

        path = Path(directory_path)
        if not path.exists() or not path.is_dir():
            raise NotADirectoryError(f"Directory not found: {directory_path}")

        # Build directory structure
        root_dir = self._build_directory_structure(path, options)

        # Convert to DirectoryInode
        return self._convert_to_directory_inode(root_dir)

    def _build_directory_structure(
        self, path: Path, options: OnchfsPrepareOptions
    ) -> PrepareDirectoryDir:
        """Build the directory structure recursively.

        Args:
            path: Path to the directory to process.
            options: Preparation options.

        Returns:
            PrepareDirectoryDir representing the directory structure.
        """
        root = PrepareDirectoryDir(type="directory", parent=None)

        for item in path.iterdir():
            # URL encode filename for safe storage
            encoded_name = urllib.parse.quote(item.name, safe="")

            if item.is_file():
                # Prepare file
                file_inode = self.prepare_file(str(item), options)
                file_node = PrepareDirectoryFile(
                    type="file",
                    name=encoded_name,
                    content=b"",  # Content is in inode
                    parent=root,
                    inode=file_inode,
                )
                root.files[encoded_name] = file_node

            elif item.is_dir():
                # Recursively process subdirectory
                subdir = self._build_directory_structure(item, options)
                subdir.parent = root
                root.files[encoded_name] = subdir

        return root

    def _convert_to_directory_inode(
        self, prepare_dir: PrepareDirectoryDir
    ) -> DirectoryInode:
        """Convert PrepareDirectoryDir to DirectoryInode.

        Args:
            prepare_dir: The prepared directory structure.

        Returns:
            DirectoryInode with computed hash.
        """
        files = {}

        for name, node in prepare_dir.files.items():
            if node.type == "file":
                files[name] = node.inode
            else:
                files[name] = self._convert_to_directory_inode(node)

        # Compute directory hash following OnchFS specification exactly
        hash_chunks = []
        filenames = sorted(files.keys())  # alphabetically ordered

        # Process files in sorted order following OnchFS spec
        for filename in filenames:
            inode = files[filename]
            # Add to hash_chunks: [cid, keccak(name), ...existing_chunks]
            hash_chunks = [
                inode.cid,  # fixed-length 32 bytes inode CID
                keccak256(filename.encode("utf-8")),  # hash the file name
                *hash_chunks,  # prepend to existing chunks
            ]

        # Final hash: keccak(concat(bytes(0x00), hash_chunks))
        directory_data = INODE_BYTE_IDENTIFIER["DIRECTORY"] + b"".join(
            hash_chunks
        )
        directory_cid = keccak256(directory_data)

        return DirectoryInode(type="directory", cid=directory_cid, files=files)

    def prepare_files(
        self, files: List[IFile], options: OnchfsPrepareOptions = None
    ) -> DirectoryInode:
        """Prepare a list of files for upload as a directory.

        Args:
            files: List of IFile objects.
            options: Preparation options.

        Returns:
            DirectoryInode ready for upload.
        """
        if options is None:
            options = OnchfsPrepareOptions()

        root = PrepareDirectoryDir(type="directory", parent=None)

        for file in files:
            # Get filename from path
            filename = os.path.basename(file.path)

            # URL encode filename for safe storage
            encoded_filename = urllib.parse.quote(filename, safe="")

            # Get MIME type
            mime_type = get_mime_type(filename)

            # Prepare content
            content = file.content
            headers = [("content-type", mime_type)]

            # Compress if beneficial
            if options.compress and should_compress(mime_type, len(content)):
                content = compress_data(content)
                headers.append(("content-encoding", "gzip"))

            # Encode metadata using HPACK with fresh encoder for deterministic results
            encoder = Encoder()
            metadata = encoder.encode(headers)

            # Create chunks
            chunk_data = chunk_bytes(content, options.chunk_size)
            chunks = []

            for chunk_bytes_data in chunk_data:
                # Use keccak256 for chunk hash
                chunk_hash = keccak256(chunk_bytes_data)
                chunks.append(
                    FileChunk(bytes=chunk_bytes_data, hash=chunk_hash)
                )

            # Create file inode
            file_cid = compute_file_hash(content, metadata)
            file_inode = FileInode(
                type="file", chunks=chunks, cid=file_cid, metadata=metadata
            )

            # Add to directory using encoded filename as key
            file_node = PrepareDirectoryFile(
                type="file",
                name=encoded_filename,
                content=b"",
                parent=root,
                inode=file_inode,
            )
            root.files[encoded_filename] = file_node

        return self._convert_to_directory_inode(root)

    def estimate_cost(self, directory_inode: DirectoryInode) -> Dict[str, int]:
        """Estimate the cost of uploading a directory.

        Args:
            directory_inode: The directory to estimate cost for.

        Returns:
            Dictionary with cost estimates.
        """
        total_chunks = 0
        total_size = 0
        file_count = 0

        def count_recursive(inode):
            nonlocal total_chunks, total_size, file_count

            if inode.type == "file":
                file_count += 1
                total_chunks += len(inode.chunks)
                for chunk in inode.chunks:
                    total_size += len(chunk.bytes)
            else:
                for child in inode.files.values():
                    count_recursive(child)

        count_recursive(directory_inode)

        return {
            "total_chunks": total_chunks,
            "total_size": total_size,
            "file_count": file_count,
            "estimated_gas": total_chunks * 1000,  # Rough estimate
            "estimated_storage_cost": total_size
            * 0.001,  # Rough estimate in XTZ
        }

    def upload_directory(
        self, directory_inode: DirectoryInode, contract_address: str = None
    ) -> UploadResult:
        """Upload a directory to the blockchain.

        Args:
            directory_inode: The directory to upload.
            contract_address: Contract address to upload to.

        Returns:
            UploadResult with operation details.

        Raises:
            RuntimeError: If PyTezos client is not configured.
            ValueError: If contract address is not provided.
        """
        if not self.client:
            raise RuntimeError("PyTezos client not configured")

        if not contract_address:
            raise ValueError("Contract address is required for upload")

        # Get the contract
        contract = self.client.contract(contract_address)

        # Upload all chunks first
        uploaded_chunks = set()
        total_size = 0
        compressed_size = 0

        def upload_chunks_recursive(inode):
            nonlocal total_size, compressed_size

            if inode.type == "file":
                for chunk in inode.chunks:
                    chunk_hash = bytes_to_hex(chunk.hash)
                    if chunk_hash not in uploaded_chunks:
                        # Check if chunk already exists in content store
                        if self._check_chunk_exists(chunk.hash):
                            print(
                                f"Chunk {chunk_hash[:16]}... already exists, "
                                "skipping upload"
                            )
                            uploaded_chunks.add(chunk_hash)
                        else:
                            # Upload chunk to blockchain
                            contract.write_chunk(chunk.bytes).send(
                                min_confirmations=1
                            )
                            uploaded_chunks.add(chunk_hash)
                            print(
                                f"Uploaded chunk {chunk_hash[:16]}... "
                                f"(size: {len(chunk.bytes)} bytes)"
                            )

                        total_size += len(chunk.bytes)
                        compressed_size += len(chunk.bytes)
            else:
                for child_inode in inode.files.values():
                    upload_chunks_recursive(child_inode)

        print("Uploading chunks...")
        upload_chunks_recursive(directory_inode)

        # Create files
        file_hashes = {}

        def create_files_recursive(inode):
            if inode.type == "file":
                file_hash = bytes_to_hex(inode.cid)

                # Check if file already exists
                if self._check_file_exists(inode.cid, contract_address):
                    print(
                        f"File {file_hash[:16]}... already exists, "
                        "skipping creation"
                    )
                    file_hashes[file_hash] = None  # Mark as existing
                else:
                    # Create file with chunk pointers and metadata
                    # Use hex strings for chunk pointers (like your working code)
                    chunk_pointers = [
                        bytes_to_hex(chunk.hash) for chunk in inode.chunks
                    ]

                    op = contract.create_file(
                        {
                            "chunk_pointers": chunk_pointers,
                            "metadata": inode.metadata,
                        }
                    ).send(min_confirmations=1)
                    file_hashes[file_hash] = op.hash()
                    print(f"Created file {file_hash[:16]}...")
            else:
                # First create all child files/directories
                for child_inode in inode.files.values():
                    create_files_recursive(child_inode)

        print("Creating files...")
        create_files_recursive(directory_inode)

        # Create directory structure
        def create_directory_structure(inode):
            if inode.type == "directory":
                directory_hash = bytes_to_hex(inode.cid)

                # Check if directory already exists
                if self._check_directory_exists(inode.cid, contract_address):
                    print(
                        f"Directory {directory_hash[:16]}... already exists, "
                        "skipping creation"
                    )
                    return None  # Directory already exists
                else:
                    # Build directory map with bytes CIDs (not hex strings)
                    directory_map = {}
                    for name, child_inode in inode.files.items():
                        directory_map[name] = (
                            child_inode.cid
                        )  # Use bytes directly, not hex

                    # Create directory on blockchain
                    op = contract.create_directory(directory_map).send(
                        min_confirmations=1
                    )
                    print(
                        f"Created directory {directory_hash[:16]}... "
                        f"with {len(directory_map)} items"
                    )
                    return op.hash()

        print("Creating directory structure...")
        final_op_hash = create_directory_structure(directory_inode)

        return UploadResult(
            directory_hash=bytes_to_hex(directory_inode.cid),
            file_hashes=file_hashes,
            operation_hash=final_op_hash,
            total_size=total_size,
            compressed_size=compressed_size,
        )

    def get_directory_hash(self, directory_inode: DirectoryInode) -> str:
        """Get the hash of a directory inode.

        Args:
            directory_inode: The directory inode.

        Returns:
            Hex string of the directory hash.
        """
        return bytes_to_hex(directory_inode.cid)
