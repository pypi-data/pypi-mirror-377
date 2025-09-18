
import os
import logging
import hashlib
from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError, ResourceExistsError
from azure.core import MatchConditions


logger = logging.getLogger(__name__)

class AzBKFile:
    def __init__(self, azBk: 'AzBK', filename: str, remote_filename: str):
        self.azBk = azBk
        self.filename = filename
        self.remote_filename = remote_filename

    def _calculate_md5(self):
        """Calculates the MD5 hash of the local file."""
        hash_md5 = hashlib.md5()
        with open(self.filename, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.digest()
        
    def upload(self):
        """
        Uploads a file to Azure Blob Storage using client credentials.
        """
        try:
            # Resource acquiring step: get the blob service client
            blob_service_client = self.azBk.get_service_client()
            container_client = blob_service_client.get_container_client(self.azBk.container_name)
            blob_client = container_client.get_blob_client(self.remote_filename)
            
            # Calculate MD5 hash of the local file for integrity checking.
            local_md5 = self._calculate_md5()
            logger.info("Local file '%s' MD5: %s", self.filename, local_md5.hex())

            # First, check if the blob exists to get its ETag.
            try:
                properties = blob_client.get_blob_properties()
                etag = properties.etag
                remote_md5 = properties.content_settings.content_md5
                logger.info("Blob '%s' exists. ETag: %s, Remote MD5: %s", self.remote_filename, etag, remote_md5.hex() if remote_md5 else "None")

                if remote_md5 == local_md5:
                    logger.info("Remote blob MD5 matches local file. Skipping upload for '%s'.", self.remote_filename)
                    return
            except ResourceNotFoundError:
                etag = None
                logger.info("Blob '%s' does not exist.", self.remote_filename)

            if etag is None:
                # If the blob does not exist, upload with overwrite=False.
                # This will fail atomically if another process creates it in the meantime.
                with open(self.filename, "rb") as data:
                    blob_client.upload_blob(data, overwrite=False, validate_content=True)
                logger.info("Successfully uploaded new blob '%s'.", self.remote_filename)
            else:
                # If the blob exists, perform a conditional upload using the ETag.
                # This prevents overwriting the blob if it has been modified since we last checked.
                with open(self.filename, "rb") as data:
                    blob_client.upload_blob(data, etag=etag, match_condition=MatchConditions.IfNotModified, overwrite=True, validate_content=True)
                logger.info("Successfully uploaded and replaced '%s'.", self.remote_filename)
        except Exception as ex:
            logger.error("An error occurred during upload of '%s'", self.remote_filename, exc_info=True)


class AzBK():
    def __init__(
        self, tenant_id: str, client_id: str, client_secret: str, 
        storage_account_name: str, container_name: str
    ):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.storage_account_name = storage_account_name
        self.container_name = container_name
        self._service_client = None

    def get_service_client(self):
        """Returns a cached BlobServiceClient instance."""
        if self._service_client is None:
            # 1. Authenticate using client credentials
            credential = ClientSecretCredential(
                tenant_id=self.tenant_id,
                client_id=self.client_id,
                client_secret=self.client_secret
            )

            # 2. Create and cache the Blob Service Client
            self._service_client = BlobServiceClient(
                account_url=f"https://{self.storage_account_name}.blob.core.windows.net",
                credential=credential
            )
        
        return self._service_client
    
    def file(self, file_name: str, remote_file_name: str):
        return AzBKFile(self, file_name, remote_file_name)
