"""OnchFS resolver for downloading and extracting files from the blockchain.

This module provides the OnchfsResolver class for downloading files and
directories from the OnchFS protocol on Tezos blockchain.
"""

import gzip
from pathlib import Path
from typing import Dict, Optional, Union

from hpack import Decoder
from pytezos import pytezos

from .config import Network, DEFAULT_CONTRACTS
from .utils import is_text_file, validate_directory_hash


class OnchfsResolver:
    """Resolver for downloading files from OnchFS.

    This class provides methods to read directories and files from the OnchFS
    contract on the Tezos blockchain, and extract them to the local filesystem.

    Attributes:
        network: The blockchain network being used.
        contract_address: The OnchFS contract address.
        client: The PyTezos client instance.
        contract: The OnchFS contract interface.
        decoder: HPACK decoder for metadata.
    """

    def __init__(
        self,
        network: Network = Network.MAINNET,
        contract_address: Optional[str] = None,
    ):
        """Initialize the resolver.

        Args:
            network: The blockchain network to use.
            contract_address: Custom contract address (uses default if None).
        """
        self.network = network
        self.contract_address = contract_address or DEFAULT_CONTRACTS[network]

        # Initialize pytezos client
        self.client = pytezos.using(shell=network.value)
        self.contract = self.client.contract(self.contract_address)

        # Initialize HPACK decoder for metadata
        self.decoder = Decoder()

    def read_directory(self, directory_hash: str) -> Dict[str, bytes]:
        """Read directory contents from the blockchain.

        Args:
            directory_hash: The hash identifier of the directory.

        Returns:
            Dictionary mapping filenames to their pointer hashes.

        Raises:
            ValueError: If the directory hash is invalid.
            RuntimeError: If reading the directory fails.
        """
        if not validate_directory_hash(directory_hash):
            raise ValueError(f"Invalid directory hash: {directory_hash}")

        try:
            directory = self.contract.read_directory(directory_hash).run_view()
            return directory
        except Exception as e:
            raise RuntimeError(
                f"Failed to read directory {directory_hash}: {e}"
            ) from e

    def read_file(self, file_hash: Union[str, bytes]) -> Dict:
        """Read file inode from the blockchain.

        Args:
            file_hash: The hash identifier of the file.

        Returns:
            File inode data containing content and metadata.

        Raises:
            RuntimeError: If reading the file fails.
        """
        try:
            if isinstance(file_hash, str):
                if len(file_hash) == 64:
                    file_hash = bytes.fromhex(file_hash)
                else:
                    file_hash = file_hash.encode()

            inode = self.contract.read_file(file_hash).run_view()
            return inode
        except Exception as e:
            raise RuntimeError(f"Failed to read file {file_hash}: {e}") from e

    def extract_directory(
        self, directory_hash: str, target_dir: str, verbose: bool = True
    ) -> Dict[str, str]:
        """Extract all files from a directory to local filesystem.

        Args:
            directory_hash: The hash identifier of the directory.
            target_dir: Local directory path to extract files to.
            verbose: Whether to print progress information.

        Returns:
            Dictionary mapping filenames to their local paths.
        """
        # Create target directory if it doesn't exist
        target_path = Path(target_dir)
        target_path.mkdir(parents=True, exist_ok=True)

        if verbose:
            print(f"Created directory: {target_dir}")

        # Read directory contents
        directory = self.read_directory(directory_hash)
        extracted_files = {}

        for file_name, file_pointer in directory.items():
            try:
                # Read file inode
                inode = self.read_file(file_pointer)

                # Decode metadata using HPACK
                hpack_meta = self.decoder.decode(inode["metadata"])

                if verbose:
                    print(f"Processing {file_name}: {hpack_meta}")

                # Get file content
                file_content = inode["content"]

                # Check if file is gzip encoded
                is_gzipped = any(
                    header[0] == "content-encoding" and header[1] == "gzip"
                    for header in hpack_meta
                )

                if is_gzipped:
                    try:
                        # Decode gzip content
                        file_content = gzip.decompress(file_content)
                        if verbose:
                            print(f"Decoded gzip content for {file_name}")
                    except Exception as e:
                        print(f"Error decoding gzip for {file_name}: {e}")
                        continue

                # Write file to target directory
                file_path = target_path / file_name

                # Determine content type
                content_type = next(
                    (
                        header[1]
                        for header in hpack_meta
                        if header[0] == "content-type"
                    ),
                    "application/octet-stream",
                )

                # Write file based on content type
                if is_text_file(content_type):
                    # Write as text
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(file_content.decode("utf-8"))
                else:
                    # Write as binary
                    with open(file_path, "wb") as f:
                        f.write(file_content)

                extracted_files[file_name] = str(file_path)

                if verbose:
                    print(f"Saved {file_name} to {file_path}")

            except Exception as e:
                print(f"Error processing file {file_name}: {e}")
                continue

        if verbose:
            print(f"Extracted {len(extracted_files)} files to {target_dir}")
            print("Directory contents:", directory)

        return extracted_files

    def get_file_content(self, directory_hash: str, filename: str) -> bytes:
        """Get the content of a specific file from a directory.

        Args:
            directory_hash: The hash identifier of the directory.
            filename: Name of the file to retrieve.

        Returns:
            Raw file content as bytes.

        Raises:
            FileNotFoundError: If the file is not found in the directory.
        """
        directory = self.read_directory(directory_hash)

        if filename not in directory:
            raise FileNotFoundError(f"File {filename} not found in directory")

        file_pointer = directory[filename]
        inode = self.read_file(file_pointer)

        # Decode metadata to check for compression
        hpack_meta = self.decoder.decode(inode["metadata"])
        file_content = inode["content"]

        # Check if file is gzip encoded
        is_gzipped = any(
            header[0] == "content-encoding" and header[1] == "gzip"
            for header in hpack_meta
        )

        if is_gzipped:
            file_content = gzip.decompress(file_content)

        return file_content

    def get_file_metadata(
        self, directory_hash: str, filename: str
    ) -> Dict[str, str]:
        """Get the metadata of a specific file from a directory.

        Args:
            directory_hash: The hash identifier of the directory.
            filename: Name of the file to get metadata for.

        Returns:
            Dictionary of metadata headers.

        Raises:
            FileNotFoundError: If the file is not found in the directory.
        """
        directory = self.read_directory(directory_hash)

        if filename not in directory:
            raise FileNotFoundError(f"File {filename} not found in directory")

        file_pointer = directory[filename]
        inode = self.read_file(file_pointer)

        # Decode metadata using HPACK
        hpack_meta = self.decoder.decode(inode["metadata"])

        # Convert to dictionary
        metadata = {}
        for header in hpack_meta:
            metadata[header[0]] = header[1]

        return metadata
