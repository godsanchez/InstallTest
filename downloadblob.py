# /// script
# requires-python = ">=3.14"
# dependencies = [
#  "azure-storage-blob",
#  "msal",
#  "msal-extensions",
#  "rich"
# ]
# ///

import os
import json
import shutil
import argparse
import requests
from azure.storage.blob import BlobClient
from msal import PublicClientApplication
from msal_extensions import build_encrypted_persistence, PersistedTokenCache
from rich import print

DOWNLOAD_ROOT = os.path.join(os.path.abspath(os.sep), "CRC", "Packages")

# Ganymede API values
API_URL = "https://crc-prod01-portal-api.azurewebsites.net"
SAS_TOKEN_ENDPOINT = "/api/sas/token/Assets"
METADATA_ENDPOINT = "/api/assets"
DOCUMENT_ENDPOINT = "/api/assets/{assetId}/contents/{assetId}-{revision}"

# Delegated auth values
CLIENT_ID = "209c395c-2407-416e-9e0a-72dfb350777d"
SCOPE = "api://209c395c-2407-416e-9e0a-72dfb350777d/user_impersonation"
TENANT_ID = "72f988bf-86f1-41af-91ab-2d7cd011db47"

# Token cache values
CACHE_LOCATION = os.path.join(os.path.expanduser("~"), ".crccache", "msal_token_cache.bin")
os.makedirs(os.path.dirname(CACHE_LOCATION), exist_ok=True)
persistence = build_encrypted_persistence(CACHE_LOCATION)
crc_token_cache = PersistedTokenCache(persistence)


parser = argparse.ArgumentParser(description="A script to download blobs from Azure Blob Storage.")
group = parser.add_argument_group()
group.add_argument("--package-guid", type=str, help="The guid of the asset to download.")
group.add_argument("--download-path", type=str, help="The destination path for the asset to download.")
group.add_argument("--version", type=str, help="The version of the asset to download.", default=str())
group.add_argument("--api-url", type=str, help="The API URL for the Ganymede API.", default=API_URL)
group.add_argument("--sas-token-endpoint", type=str, help="The SAS token endpoint for the Ganymede API.", default=SAS_TOKEN_ENDPOINT)
group.add_argument("--metadata-endpoint", type=str, help="The metadata endpoint for the Ganymede API.", default=METADATA_ENDPOINT)
group.add_argument("--document-endpoint", type=str, help="The document endpoint for the Ganymede API.", default=DOCUMENT_ENDPOINT)
group.add_argument("--client-id", type=str, help="The client ID for authentication.", default=CLIENT_ID)
group.add_argument("--scope", type=str, help="The scope for authentication.", default=SCOPE)
group.add_argument("--tenant-id", type=str, help="The tenant ID for authentication.", default=TENANT_ID)

args = parser.parse_args()


def get_ganymede_rest_token(client_id: str, tenant_id: str, scope: list[str]) -> str:
    """
    Obtains a token for accessing the Ganymede API.
    """

    # Set up variables for Microsoft User Delegation authentication using MSAL
    authority = f"https://login.microsoftonline.com/{tenant_id}"

    app = PublicClientApplication(
        client_id=client_id,
        authority=authority,
        token_cache=crc_token_cache
    )

    # First, try to get a token silently from the cache
    accounts = app.get_accounts()
    result = None

    if accounts:
        result = app.acquire_token_silent(scope, account=accounts[0])

    # If silent acquisition fails, fall back to interactive authentication
    if not result:
        result = app.acquire_token_interactive(
            scopes=scope
        )

    if isinstance(result, dict) and "access_token" in result:
        access_token = result["access_token"]
        return access_token
    else:
        print(result.get("error"))
        print(result.get("error_description"))
        return str()

def get_ganymede_rest_response(api_url:str, endpoint:str, token:str, params:dict={}) -> requests.Response:
    """
    Makes a GET request to the specified Ganymede API endpoint with the provided parameters and returns the response.

    param: endpoint: The API endpoint to send the GET request to (appended to the base URL from globals).
    param: params: A dictionary of query parameters to include in the GET request.
    """

    api_url = f"{api_url}{endpoint}"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.get(api_url, headers=headers, params=params, timeout=10)
    except requests.RequestException as e:
        print(f"Request to Ganymede API failed: {e}")
        response = requests.Response()  # Return an empty Response object

    return response

def get_asset_metadata_by_guid(api_url:str, endpoint:str, token:str, guid:str) -> dict:
    """
    Obtains metadata for an asset from the Ganymede API.

    param: guid: The GUID of the asset to retrieve metadata for.
    """

    response = get_ganymede_rest_response(api_url=api_url, endpoint=f"{endpoint}/{str(guid)}", token=token)

    if response.status_code == 200:
        metadata = response.json()
        return metadata
    else:
        print(f"Failed to obtain asset metadata. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return dict()

def get_asset_revision(guid: str, token: str, version: str = str()) -> int:
    """
    Get the latest revision for a given asset GUID and version.
    If version is blank, this will simply return the latest revision.
    """

    # Get metadata for the asset
    versions_data = get_asset_metadata_by_guid(
        api_url=args.api_url,
        endpoint=args.metadata_endpoint,
        token=token,
        guid=guid
    )

    revisions = versions_data.get("revisions", {})
    if not revisions:
        print("No revisions found in metadata.")
        return -1
    

    # Convert revisions object to a list of (revision, version) tuples and sort by revision number
    sorted_revisions = sorted(
        [(data.get("revision"), data.get("version")) for data in revisions],
        key=lambda x: x[0]
    )

    # Return the latest revision that matches the specified version, or the latest revision overall if version is blank
    for revision, rev_version in reversed(sorted_revisions):
        if version == str() or rev_version == version:
            return revision
        
    return -1  # Return -1 if no matching revision is found

def get_asset_document_by_guid_and_revision(api_url:str, endpoint:str, token:str, guid:str, revision:int) -> dict:
    """
    Obtains the document content for a specific asset revision from the Ganymede API.

    param: guid: The GUID of the asset to retrieve the document for.
    param: revision: The ID of the specific revision of the asset to retrieve.
    """

    formatted_endpoint = endpoint.format(assetId=guid, revision=revision)

    response = get_ganymede_rest_response(api_url=api_url, endpoint=formatted_endpoint, token=token)

    if response.status_code == 200:
        document_content = response.json()
        return document_content
    else:
        print(f"Failed to obtain asset document. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return dict()

def get_ganymede_sas_token(api_url:str, endpoint:str, token:str) -> str :
    """
    Obtains an SAS token from the Ganymede API for accessing Azure Blob Storage.
    """

    response = get_ganymede_rest_response(api_url=api_url, endpoint=endpoint, token=token)

    if response.status_code == 200:
        sas_token = response.text
        return sas_token
    else:
        print(f"Failed to obtain SAS token. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return str()

def download_asset(asset_guid: str, version: str = str(), download_path: str = str()) -> str:
    """
    Download a CRC asset from Azure Blob Storage using Microsoft Entra ID authentication.

    :param asset_guid: The GUID of the asset to be downloaded.
    :param revision: The revision of the asset to be downloaded.
    :param version: The version of the asset to be downloaded.
    :param download_path: The local file path to save the blob to (including filename).
    :param install: Whether to run installation scripts and install dependencies after downloading the asset files.
    """
    # Get token for accessing Ganymede API
    access_token = get_ganymede_rest_token(client_id=args.client_id, tenant_id=args.tenant_id, scope=[args.scope])

    # Get revision for asset version
    revision = get_asset_revision(guid=asset_guid, token=access_token, version=version)

    # Save latest package metadata to asset folder
    asset_metadata = get_asset_metadata_by_guid(guid=asset_guid, token=access_token, api_url=args.api_url, endpoint=args.metadata_endpoint)

    if asset_metadata:
        asset_metadata_local_path = os.path.join(DOWNLOAD_ROOT, asset_guid, "metadata.json")
        os.makedirs(os.path.dirname(asset_metadata_local_path), exist_ok=True)
        with open(asset_metadata_local_path, "w") as metadata_file:
            json.dump(asset_metadata, metadata_file, indent=4)
    
    # Get asset document content for the specified revision
    document_content = get_asset_document_by_guid_and_revision(
        api_url=args.api_url,
        endpoint=args.document_endpoint,
        token=access_token,
        guid=asset_guid,
        revision=revision
    )

    # Get SAS token for accessing Azure Blob Storage
    sas_token = get_ganymede_sas_token(api_url=args.api_url, endpoint=args.sas_token_endpoint, token=access_token)

    # Construct blob base names
    package_download_path = os.path.join(DOWNLOAD_ROOT, asset_guid, str(revision))

    # Skip download if package already exists at download path
    if os.path.exists(package_download_path):
        print(f"Asset with GUID: {asset_guid} and revision: {revision} already exists at download path: {package_download_path}. Skipping download...")
    else:
        # Download asset files listed in document_content (which is the index.json content)
        download_asset_files(index_data=document_content, sas_token=sas_token, download_path=package_download_path)

    # If download_path is provided, copy files from package_download_path to download_path
    if download_path:
        print(f"Copying folder from {package_download_path} to {download_path}...")
        shutil.copytree(package_download_path, download_path, dirs_exist_ok=True)
    else:
        download_path = package_download_path


    return download_path

def download_asset_files(index_data:dict, sas_token:str, download_path:str):
    """
    Download asset files listed in the index.json file in parallel.

    param: index_data: The dictionary containing the index.json data that lists the asset files to be downloaded.
    param: sas_token: The SAS token for authenticating to Azure Blob Storage.
    param: download_path: The local directory path to save the downloaded asset files to.
    """
    asset_files = index_data.get("files", [])

    for asset_file in asset_files:
        asset_filename = asset_file.get("fileName")
        asset_url = asset_file.get("url")
        blob_asset_local_path = os.path.join(download_path, asset_filename)

        download_blob_url_with_sas_token(blob_url=asset_url, sas_token=sas_token, download_path=blob_asset_local_path)

def download_blob_url_with_sas_token(blob_url, sas_token, download_path) -> str:
    """
    Downloads a blob from a URL using a SAS token.

    :param blob_url: The full URL to the blob (without the SAS token).
    :param sas_token: The SAS token string (starting with '?' if part of the URL).
    :param download_path: The full local file path to save the blob to (including filename).
    """

    # Combine the blob URL and SAS token
    # If the token already starts with '?', ensure there isn't a duplicate.
    full_blob_url = f"{blob_url}{sas_token}" if sas_token.startswith('?') else f"{blob_url}?{sas_token}"

    # Create a BlobClient object from the full URL with SAS
    blob_client = BlobClient.from_blob_url(full_blob_url)

    # Ensure the local parent directory exists
    directory = os.path.dirname(download_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    try:  
        with open(download_path, "wb") as download_file:
            download_stream = blob_client.download_blob()
            for chunk in download_stream.chunks():
                download_file.write(chunk)
    except Exception as e:
        print(f"Failed to download blob from URL: {full_blob_url}. Error: {e}")
        return str()
    
    print(f"Successfully downloaded {blob_client.blob_name} to {download_path}.")

    return download_path


if __name__ == "__main__":
    download_path = download_asset(asset_guid=args.package_guid, version=args.version, download_path=args.download_path)
