"""
Example: Prepare files for upload to OnchFS

This example demonstrates how to prepare files for upload,
including compression and metadata handling.
"""

from onchfs import OnchfsClient, Network, IFile, OnchfsPrepareOptions


def main():
    # Initialize client
    client = OnchfsClient(network=Network.MAINNET)

    print("PyOnchfs Preparation Example")
    print("=" * 40)

    # Example 1: Prepare files from memory
    print("\n1. Preparing files from memory...")

    files = [
        IFile(path="hello.txt", content=b"Hello, OnchFS!"),
        IFile(
            path="data.json",
            content=b'{"message": "This is a test JSON file", "compressed": true}',
        ),
        IFile(
            path="style.css",
            content=b"body { font-family: Arial; color: #333; }",
        ),
    ]

    # Prepare with compression enabled
    options = OnchfsPrepareOptions(chunk_size=1024, compress=True)
    directory_inode = client.prepare_files(files, options)

    print(f"Prepared directory with {len(directory_inode.files)} files")
    print(f"Directory hash: {client.get_directory_hash(directory_inode)}")

    # Estimate upload cost
    cost_estimate = client.estimate_upload_cost(directory_inode)
    print(f"Upload cost estimate: {cost_estimate}")

    # Example 2: Prepare a directory from filesystem (if extracted directory exists)
    print("\n2. Preparing directory from filesystem...")

    try:
        # Try to prepare the extracted directory if it exists
        extracted_dir = "extracted"
        fs_directory_inode = client.prepare_directory(extracted_dir, options)

        print(
            f"Prepared filesystem directory with {len(fs_directory_inode.files)} files"
        )
        print(
            f"Directory hash: {client.get_directory_hash(fs_directory_inode)}"
        )

        fs_cost_estimate = client.estimate_upload_cost(fs_directory_inode)
        print(f"Upload cost estimate: {fs_cost_estimate}")

    except Exception as e:
        print(f"Could not prepare filesystem directory: {e}")
        print("(This is expected if the 'extracted' directory doesn't exist)")

    # Example 3: Prepare with different options
    print("\n3. Preparing with different compression settings...")

    # Large text content to demonstrate compression
    large_content = "This is a test file with repeated content. " * 100
    large_files = [
        IFile(path="large.txt", content=large_content.encode()),
        IFile(path="small.txt", content=b"Small file"),
    ]

    # Without compression
    no_compress_options = OnchfsPrepareOptions(compress=False)
    no_compress_dir = client.prepare_files(large_files, no_compress_options)
    no_compress_cost = client.estimate_upload_cost(no_compress_dir)

    # With compression
    compress_options = OnchfsPrepareOptions(compress=True)
    compress_dir = client.prepare_files(large_files, compress_options)
    compress_cost = client.estimate_upload_cost(compress_dir)

    print(f"Without compression - Size: {no_compress_cost['total_size']} bytes")
    print(f"With compression - Size: {compress_cost['total_size']} bytes")
    print(
        f"Compression ratio: {compress_cost['total_size'] / no_compress_cost['total_size']:.2%}"
    )

    # Example 4: Inspect prepared directory structure
    print("\n4. Inspecting prepared directory structure...")

    def print_directory_structure(inode, indent=0):
        prefix = "  " * indent
        if inode.type == "file":
            print(
                f"{prefix}📄 File: {len(inode.chunks)} chunks, {len(inode.metadata)} bytes metadata"
            )
        else:
            print(f"{prefix}📁 Directory: {len(inode.files)} items")
            for name, child_inode in inode.files.items():
                print(f"{prefix}  └─ {name}")
                print_directory_structure(child_inode, indent + 2)

    print("Directory structure:")
    print_directory_structure(directory_inode)

    print("\n" + "=" * 40)
    print("Preparation complete! Files are ready for upload.")
    print(
        "Note: Actual upload requires a configured PyTezos client with a private key."
    )


if __name__ == "__main__":
    main()
