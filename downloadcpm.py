# /// script
# requires-python = ">=3.14"
# dependencies = [
#  "azure-storage-blob",
#  "azure-identity",
#  "msal"
# ]
# ///

import os
from azure.identity import InteractiveBrowserCredential
from azure.storage.blob import BlobClient

# Replace with your actual values
STORAGE_ACCOUNT_URL = "https://crcportalstoragedev.blob.core.windows.net"
CONTAINER_NAME = "cpm"
BLOB_NAME = "ganymedepackagemanager-0.1.0.tar.gz"
DOWNLOAD_PATH = "./ganymedepackagemanager-0.1.0.tar.gz"


def download_blob_with_msal_auth(account_url, container_name, blob_name, download_path):
    """
    Downloads a blob from Azure Blob Storage using Microsoft Entra ID authentication.
    """
    try:
        # Obtain a credential object using InteractiveBrowserCredential
        # This will automatically try to authenticate using various methods (env variables, managed identity, etc.)
        credential = InteractiveBrowserCredential()

        # Create a BlobClient instance with the credential
        blob_client = BlobClient(
            account_url=account_url,
            container_name=container_name,
            blob_name=blob_name,
            credential=credential
        )

        print(f"Downloading blob '{blob_name}' to '{download_path}'...")

        # Download the blob data
        with open(download_path, "wb") as download_file:
            download_stream = blob_client.download_blob()
            download_file.write(download_stream.readall())

        print("Download complete.")

    except Exception as ex:
        print(f"An exception occurred: {ex}")

if __name__ == "__main__":
    download_blob_with_msal_auth(STORAGE_ACCOUNT_URL, CONTAINER_NAME, BLOB_NAME, DOWNLOAD_PATH)
