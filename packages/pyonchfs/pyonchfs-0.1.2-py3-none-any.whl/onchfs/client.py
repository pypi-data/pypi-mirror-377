"""Main client for OnchFS - unified interface for OnchFS operations.

This module provides the main OnchfsClient class that serves as a unified
interface for both uploading and downloading files from the OnchFS protocol
on Tezos blockchain.
"""

import os
from typing import Dict, List, Optional

from pytezos import pytezos

from .config import Network, DEFAULT_CONTRACTS
from .resolver import OnchfsResolver
from .types import DirectoryInode, IFile, OnchfsPrepareOptions, UploadResult
from .uploader import OnchfsUploader


class OnchfsClient:
    """Main client for interacting with OnchFS.

    Provides a unified interface for both uploading and downloading files
    from the OnchFS protocol on Tezos blockchain.

    Attributes:
        network: The blockchain network being used.
        contract_address: The OnchFS contract address.
        pytezos_client: The PyTezos client instance.
        resolver: The OnchFS resolver for downloads.
        uploader: The OnchFS uploader for uploads.
    """

    def __init__(
        self,
        network: Network = Network.MAINNET,
        contract_address: Optional[str] = None,
        pytezos_client=None,
    ):
        """Initialize the OnchFS client.

        Args:
            network: The blockchain network to use.
            contract_address: Custom contract address (uses default if None).
            pytezos_client: Custom PyTezos client instance.
        """
        self.network = network
        self.contract_address = contract_address or DEFAULT_CONTRACTS[network]

        # Initialize PyTezos client
        if pytezos_client:
            self.pytezos_client = pytezos_client
        else:
            self.pytezos_client = pytezos.using(shell=network.value)

        # Initialize resolver and uploader
        self.resolver = OnchfsResolver(network, contract_address)
        self.uploader = OnchfsUploader(self.pytezos_client, network)

    def set_key(self, key: str):
        """Set the private key for the PyTezos client.

        Args:
            key: Private key for signing transactions.
        """
        self.pytezos_client = self.pytezos_client.using(key=key)
        self.uploader.client = self.pytezos_client

    def set_network(
        self, network: Network, contract_address: Optional[str] = None
    ):
        """Switch to a different network.

        Args:
            network: The new network to use.
            contract_address: Custom contract address for the new network.
        """
        self.network = network
        self.contract_address = contract_address or DEFAULT_CONTRACTS[network]

        # Update clients
        self.pytezos_client = self.pytezos_client.using(shell=network.value)
        self.resolver = OnchfsResolver(network, self.contract_address)
        self.uploader = OnchfsUploader(self.pytezos_client, network)

    # Download/Resolver methods
    def download_directory(
        self, directory_hash: str, target_dir: str, verbose: bool = True
    ) -> Dict[str, str]:
        """Download and extract all files from a directory.

        Args:
            directory_hash: The hash identifier of the directory.
            target_dir: Local directory path to extract files to.
            verbose: Whether to print progress information.

        Returns:
            Dictionary mapping filenames to their local paths.
        """
        return self.resolver.extract_directory(
            directory_hash, target_dir, verbose
        )

    def get_file(self, directory_hash: str, filename: str) -> bytes:
        """Get the content of a specific file from a directory.

        Args:
            directory_hash: The hash identifier of the directory.
            filename: Name of the file to retrieve.

        Returns:
            Raw file content as bytes.
        """
        return self.resolver.get_file_content(directory_hash, filename)

    def get_file_metadata(
        self, directory_hash: str, filename: str
    ) -> Dict[str, str]:
        """Get the metadata of a specific file from a directory.

        Args:
            directory_hash: The hash identifier of the directory.
            filename: Name of the file to get metadata for.

        Returns:
            Dictionary of metadata headers.
        """
        return self.resolver.get_file_metadata(directory_hash, filename)

    def list_directory(self, directory_hash: str) -> Dict[str, bytes]:
        """List the contents of a directory.

        Args:
            directory_hash: The hash identifier of the directory.

        Returns:
            Dictionary mapping filenames to their pointer hashes.
        """
        return self.resolver.read_directory(directory_hash)

    # Upload/Preparation methods
    def prepare_file(
        self, file_path: str, options: OnchfsPrepareOptions = None
    ) -> DirectoryInode:
        """Prepare a single file for upload (wrapped in a directory).

        Args:
            file_path: Path to the file to prepare.
            options: Preparation options.

        Returns:
            DirectoryInode containing the prepared file.
        """
        # Read file content
        with open(file_path, "rb") as f:
            content = f.read()

        # Create IFile and prepare as directory
        filename = os.path.basename(file_path)
        files = [IFile(path=filename, content=content)]

        return self.uploader.prepare_files(files, options)

    def prepare_directory(
        self, directory_path: str, options: OnchfsPrepareOptions = None
    ) -> DirectoryInode:
        """Prepare a directory and all its files for upload.

        Args:
            directory_path: Path to the directory to prepare.
            options: Preparation options.

        Returns:
            DirectoryInode ready for upload.
        """
        return self.uploader.prepare_directory(directory_path, options)

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
        return self.uploader.prepare_files(files, options)

    def estimate_upload_cost(
        self, directory_inode: DirectoryInode
    ) -> Dict[str, int]:
        """Estimate the cost of uploading a directory.

        Args:
            directory_inode: The directory to estimate cost for.

        Returns:
            Dictionary with cost estimates.
        """
        return self.uploader.estimate_cost(directory_inode)

    def get_directory_hash(self, directory_inode: DirectoryInode) -> str:
        """Get the hash of a prepared directory.

        Args:
            directory_inode: The directory inode.

        Returns:
            Hex string of the directory hash.
        """
        return self.uploader.get_directory_hash(directory_inode)

    def upload_directory(self, directory_inode: DirectoryInode) -> UploadResult:
        """Upload a prepared directory to the blockchain.

        Args:
            directory_inode: The directory to upload.

        Returns:
            UploadResult with operation details.
        """
        return self.uploader.upload_directory(
            directory_inode, self.contract_address
        )

    # Convenience methods
    def upload_file(
        self, file_path: str, options: OnchfsPrepareOptions = None
    ) -> UploadResult:
        """Prepare and upload a single file.

        Args:
            file_path: Path to the file to upload.
            options: Preparation options.

        Returns:
            UploadResult with operation details.
        """
        directory_inode = self.prepare_file(file_path, options)
        return self.upload_directory(directory_inode)

    def upload_files(
        self, files: List[IFile], options: OnchfsPrepareOptions = None
    ) -> UploadResult:
        """Prepare and upload a list of files.

        Args:
            files: List of IFile objects.
            options: Preparation options.

        Returns:
            UploadResult with operation details.
        """
        directory_inode = self.prepare_files(files, options)
        return self.upload_directory(directory_inode)

    def upload_directory_path(
        self, directory_path: str, options: OnchfsPrepareOptions = None
    ) -> UploadResult:
        """Prepare and upload a directory from filesystem.

        Args:
            directory_path: Path to the directory to upload.
            options: Preparation options.

        Returns:
            UploadResult with operation details.
        """
        directory_inode = self.prepare_directory(directory_path, options)
        return self.upload_directory(directory_inode)

    # Utility methods
    def get_network_info(self) -> Dict[str, str]:
        """Get information about the current network configuration.

        Returns:
            Dictionary with network information.
        """
        client_address = "Not set"
        if hasattr(self.pytezos_client.key, "public_key_hash"):
            client_address = self.pytezos_client.key.public_key_hash()

        return {
            "network": self.network.name,
            "rpc_url": self.network.value,
            "contract_address": self.contract_address,
            "client_address": client_address,
        }
