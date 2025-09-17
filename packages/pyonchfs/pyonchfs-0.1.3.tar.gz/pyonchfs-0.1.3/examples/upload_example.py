#!/usr/bin/env python3
"""Example showing the improved OnchFS upload with automatic contract resolution.

This example demonstrates the new simplified API where contract addresses
are automatically resolved based on the network configuration.
"""

import os
from pathlib import Path

from pytezos import pytezos

from onchfs import Network, OnchfsPrepareOptions
from onchfs.uploader import OnchfsUploader


def main():
    """Upload example with automatic contract resolution."""
    # Load Tezos secret key from environment
    secret_key = os.getenv("TZ_SK")
    if not secret_key:
        raise ValueError("TZ_SK environment variable not set")

    # Initialize PyTezos client with secret key
    pytezos_client = pytezos.using(
        key=secret_key, shell=Network.GHOSTNET.value  # or your preferred RPC endpoint
    )

    # Initialize OnchFS uploader with network (contracts auto-resolved)
    uploader = OnchfsUploader(pytezos_client, Network.GHOSTNET)

    # Prepare directory for upload
    directory_path = "./extracted"  # Path to your directory
    if not Path(directory_path).exists():
        print(f"Directory {directory_path} does not exist. Creating example...")
        Path(directory_path).mkdir(exist_ok=True)
        (Path(directory_path) / "example.txt").write_text("Hello OnchFS!")

    directory_inode = uploader.prepare_directory(
        directory_path, options=OnchfsPrepareOptions(compress=True)
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


if __name__ == "__main__":
    main()
