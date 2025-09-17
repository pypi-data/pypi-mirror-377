#!/usr/bin/env python3
"""OnchFS Command Line Interface.

A command-line tool for uploading and downloading files using OnchFS.
"""

import argparse
import os
import sys
from pathlib import Path

from pytezos import pytezos

from .config import Network
from .resolver import OnchfsResolver
from .types import OnchfsPrepareOptions, IFile
from .uploader import OnchfsUploader


def get_network_from_string(network_str: str) -> Network:
    """Convert string to Network enum.

    Args:
        network_str: Network name as string.

    Returns:
        Network enum value.

    Raises:
        ValueError: If network string is invalid.
    """
    network_map = {
        "mainnet": Network.MAINNET,
        "ghostnet": Network.GHOSTNET,
        "localnet": Network.LOCALNET,
    }

    network_lower = network_str.lower()
    if network_lower not in network_map:
        valid_options = ", ".join(network_map.keys())
        raise ValueError(
            f"Invalid network: {network_str}. Valid options: {valid_options}"
        )

    return network_map[network_lower]


def get_secret_key() -> str:
    """Get Tezos secret key from environment variable.

    Returns:
        Secret key string.

    Raises:
        ValueError: If TZ_SK environment variable is not set.
    """
    secret_key = os.getenv("TZ_SK")
    if not secret_key:
        raise ValueError(
            "TZ_SK environment variable not set. "
            "Please set it to your Tezos secret key."
        )
    return secret_key


def upload_command(args) -> None:
    """Handle upload command.

    Args:
        args: Parsed command line arguments.
    """
    try:
        # Get secret key
        secret_key = get_secret_key()

        # Get network
        network = get_network_from_string(args.network)

        # Initialize PyTezos client
        pytezos_client = pytezos.using(key=secret_key, shell=network.value)

        # Initialize uploader
        uploader = OnchfsUploader(pytezos_client, network)

        # Check if path exists
        path = Path(args.path)
        if not path.exists():
            print(f"Error: Path {args.path!r} does not exist", file=sys.stderr)
            sys.exit(1)

        # Prepare options
        options = OnchfsPrepareOptions(
            compress=args.compress, chunk_size=args.chunk_size
        )

        file_type = "directory" if path.is_dir() else "file"
        print(f"Preparing {file_type}: {path}")

        # Prepare for upload
        if path.is_dir():
            directory_inode = uploader.prepare_directory(str(path), options)
        else:
            # For single file, create a directory with just that file
            file_obj = IFile(path=str(path), content=path.read_bytes())
            directory_inode = uploader.prepare_files([file_obj], options)

        # Get directory hash
        directory_hash = uploader.get_directory_hash(directory_inode)
        print(f"Directory hash: {directory_hash}")

        # Estimate cost
        cost_estimate = uploader.estimate_cost(directory_inode)
        print("Estimated cost:")
        print(f"  Files: {cost_estimate['file_count']}")
        print(f"  Chunks: {cost_estimate['total_chunks']}")
        print(f"  Total size: {cost_estimate['total_size']} bytes")
        print(f"  Estimated gas: {cost_estimate['estimated_gas']}")
        storage_cost = cost_estimate['estimated_storage_cost']
        print(f"  Estimated storage cost: {storage_cost:.6f} XTZ")

        # Ask for confirmation unless --yes flag is used
        if not args.yes:
            response = input("\nProceed with upload? (y/N): ")
            if response.lower() not in ["y", "yes"]:
                print("Upload cancelled.")
                return

        # Upload
        print("\nStarting upload...")
        result = uploader.upload_directory(directory_inode)

        print("\nUpload completed!")
        print(f"Directory hash: {result.directory_hash}")
        print(f"Operation hash: {result.operation_hash}")
        print(f"Total size: {result.total_size} bytes")
        print(f"Compressed size: {result.compressed_size} bytes")
        onchfs_url = f"onchfs://{result.directory_hash}"
        print(f"\nYour files are now accessible at: {onchfs_url}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def download_command(args) -> None:
    """Handle download command.

    Args:
        args: Parsed command line arguments.
    """
    try:
        # Get network
        network = get_network_from_string(args.network)

        # Initialize resolver
        resolver = OnchfsResolver(network)

        # Parse hash from URL or use directly
        hash_value = args.hash
        if hash_value.startswith("onchfs://"):
            hash_value = hash_value[9:]  # Remove 'onchfs://' prefix

        print(f"Downloading from hash: {hash_value}")

        # Create output directory
        output_path = Path(args.output)
        output_path.mkdir(parents=True, exist_ok=True)

        # Download directory
        resolver.download_directory(hash_value, str(output_path))

        print(f"Download completed to: {output_path}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="OnchFS CLI - Upload and download files using OnchFS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Upload a file
  onchfs upload myfile.txt

  # Upload a directory with compression
  onchfs upload ./my-website --compress

  # Upload to mainnet
  onchfs upload ./docs --network mainnet

  # Download files
  onchfs download abc123def456... ./downloaded

  # Download from onchfs URL
  onchfs download onchfs://abc123def456... ./downloaded

Environment Variables:
  TZ_SK    Tezos secret key (required for uploads)
        """,
    )

    # Global options
    parser.add_argument(
        "--network",
        choices=["mainnet", "ghostnet", "localnet"],
        default="ghostnet",
        help="Tezos network to use (default: ghostnet)",
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Upload command
    upload_parser = subparsers.add_parser(
        "upload", help="Upload files or directories to OnchFS"
    )
    upload_parser.add_argument("path", help="Path to file or directory to upload")
    upload_parser.add_argument(
        "--compress", action="store_true", help="Enable compression for uploaded files"
    )
    upload_parser.add_argument(
        "--chunk-size",
        type=int,
        default=16384,
        help="Chunk size in bytes (default: 16384)",
    )
    upload_parser.add_argument(
        "--yes", "-y", action="store_true", help="Skip confirmation prompt"
    )

    # Download command
    download_parser = subparsers.add_parser(
        "download", help="Download files from OnchFS"
    )
    download_parser.add_argument(
        "hash", help="Directory hash or onchfs:// URL to download"
    )
    download_parser.add_argument("output", help="Output directory path")

    # Parse arguments
    args = parser.parse_args()

    # Show help if no command provided
    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    if args.command == "upload":
        upload_command(args)
    elif args.command == "download":
        download_command(args)


if __name__ == "__main__":
    main()
