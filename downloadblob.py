# /// script
# requires-python = ">=3.14"
# dependencies = [
#  "azure-identity",
#  "azure-storage-blob",
# ]
# ///

import os
import argparse
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

parser = argparse.ArgumentParser(description="A script to download blobs from Azure Blob Storage.")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("--blob-name", type=str, help="The filename of the blob to download (including subpath and filename).")
group.add_argument("--blob-prefix", type=str, help="The prefix of the blob to download (including subpath and filename). The newest-versioned filename will be selected.")
parser.add_argument("--download-path", type=str, help="The local folder path to save the downloaded blob.")
parser.add_argument("--account-url", type=str, help="The URL of the storage account (e.g., https://myaccount.blob.core.windows.net).")
parser.add_argument("--container-name", type=str, help="The name of the blob container (e.g. assets).")

def download_blob_with_msal_auth(account_url: str, container_name: str, blob_name: str = str(), blob_prefix: str = str(), download_path: str = "."):
    """
    Downloads a blob from Azure Blob Storage using Microsoft Entra ID authentication.
    """
    try:
        # Obtain a credential object
        credential = DefaultAzureCredential(exclude_interactive_browser_credential=False)
        
        blob_service_client = BlobServiceClient(account_url=account_url, credential=credential)
        container_client = blob_service_client.get_container_client(container_name)

        if blob_prefix:
            print(f"Searching for blobs with prefix '{blob_prefix}'...")
            blob_list = container_client.list_blobs(name_starts_with=blob_prefix)
            
            # Sort blobs by name in descending order to find the latest version
            sorted_blobs = sorted(blob_list, key=lambda blob: blob.name, reverse=True)
            
            if not sorted_blobs:
                raise ValueError(f"No blobs found with prefix '{blob_prefix}'.")
                
            blob_name = sorted_blobs[0].name
            print(f"Found latest version: '{blob_name}'")

        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

        # Resolve the full download path, including filename
        if os.path.isdir(download_path):
            download_path = os.path.join(download_path, os.path.basename(blob_name))
        else:
            # Ensure the directory for the specified file path exists
            os.makedirs(os.path.dirname(download_path), exist_ok=True)

        print(f"Downloading blob '{blob_name}' to '{download_path}'...")

        # Ensure the download directory exists
        download_dir = os.path.dirname(download_path)
        if download_dir:
            os.makedirs(download_dir, exist_ok=True)

        # Download the blob data
        with open(download_path, "wb") as download_file:
            download_stream = blob_client.download_blob(max_concurrency=10)
            download_file.write(download_stream.readall())

        print(f"Download complete.")

    except Exception as ex:
        print(f"An exception occurred: {ex}")





if __name__ == "__main__":
    args = parser.parse_args()
    download_blob_with_msal_auth(
        account_url=args.account_url, 
        container_name=args.container_name,
        blob_name=args.blob_name, 
        blob_prefix=args.blob_prefix,
        download_path=args.download_path
    )
