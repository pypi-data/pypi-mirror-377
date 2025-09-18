from h_vault_extractor_xethhung12 import GetSecrets,Pair
from bk_job_xethhung12 import AzBK, AzBKFile
import os
import logging

logger = logging.getLogger(__name__)

def build_key_pairs(
    az_tenant_id: str,
    az_app_id: str,
    az_secret: str,
    az_account: str,
    az_container_name: str,
)->[Pair]:
    return [
        Pair("az_tenant_id",az_tenant_id),
        Pair('az_app_id',az_app_id),
        Pair('az_secret',az_secret),
        Pair('az_account',az_account),
        Pair('az_container_name',az_container_name)
    ]

def file_upload(
    vault_addr: str, role_id: str, secret_id: str,
    mount_point: str, secret_path: str, keyPairs: [Pair],
    file: str, remote_filename: str
    ):
        # az_tenant_id, az_app_id, az_secret, az_account, az_container_name = 
        secret = GetSecrets(
            vault_addr=vault_addr, role_id=role_id, secret_id=secret_id,
            mount_point=mount_point, secret_path=secret_path,keys_to_extract = keyPairs
        )
        az_tenant_id = secret['az_tenant_id']
        az_app_id = secret['az_app_id']
        az_secret = secret['az_secret']
        az_account = secret['az_account']
        az_container_name = secret['az_container_name']

        az_file=AzBK(
            az_tenant_id, az_app_id, az_secret, az_account, az_container_name
        ).file(file, remote_filename)

        az_file.upload()
