"""
Example: Download files from OnchFS

This example demonstrates how to download and extract files from OnchFS.
"""

from onchfs import OnchfsClient, Network


def main():
    # Initialize client for mainnet
    client = OnchfsClient(network=Network.MAINNET)

    # Example directory hash
    directory_hash = (
        "f8020273fba472a3e87baf6eb0f3929915edabace0fa409a261c4c4fa6684b21"
    )

    print(f"Downloading directory: {directory_hash}")
    print(f"Network: {client.get_network_info()}")

    # Download and extract all files
    extracted_files = client.download_directory(
        directory_hash, "pyonchfs_extracted/"
    )

    print(f"\nSuccessfully extracted {len(extracted_files)} files:")
    for filename, filepath in extracted_files.items():
        print(f"  {filename} -> {filepath}")

    # Get specific file content
    print("\n--- Getting specific file content ---")
    try:
        index_content = client.get_file(directory_hash, "index.html")
        print(f"index.html size: {len(index_content)} bytes")
        print(
            f"First 100 chars: {index_content[:100].decode('utf-8', errors='ignore')}"
        )
    except Exception as e:
        print(f"Error getting index.html: {e}")

    # Get file metadata
    print("\n--- File metadata ---")
    try:
        metadata = client.get_file_metadata(directory_hash, "index.html")
        print(f"index.html metadata: {metadata}")
    except Exception as e:
        print(f"Error getting metadata: {e}")

    # List directory contents
    print("\n--- Directory listing ---")
    directory_contents = client.list_directory(directory_hash)
    print("Directory contents:")
    for filename, file_hash in directory_contents.items():
        print(f"  {filename}: {file_hash.hex()}")


if __name__ == "__main__":
    main()
