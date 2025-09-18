
import argparse
import os
import glob
import re
import bk_job_xethhung12 as project
import logging
from j_vault_http_client_xethhung12 import client
from bk_job_xethhung12 import LogConfiguration

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Backup files to Azure Blob Storage using credentials from HashiCorp Vault.")
    parser.add_argument("--vault-addr", required=True, help="HashiCorp Vault address.")
    parser.add_argument("--role-id", required=True, help="Vault AppRole Role ID.")
    parser.add_argument("--secret-id", required=True, help="Vault AppRole Secret ID.")
    parser.add_argument("--mount-point", default="hkse", help="Vault secrets engine mount point.")
    parser.add_argument("--secret-path", default="bk/hkse-web/apache-log", help="Path to the secret in Vault.")
    parser.add_argument("--debug-log", help="Path to a file for debug logging. If not provided, debug logs are not saved.")

    subparsers = parser.add_subparsers(dest="command", required=True, help="Sub-command help")

    # Sub-command for single file upload
    parser_single = subparsers.add_parser("single", help="Upload a single file.")
    parser_single.add_argument("--local-file", required=True, help="Path to the local file to upload. Will be converted to an absolute path.")
    parser_single.add_argument("--rename-as", help="New name for the file in blob storage. Defaults to the original local filename.")
    parser_single.add_argument("--remote-dir", help="Directory in the blob container to place the file. Defaults to the root.")
    parser_single.add_argument("--exec", action="store_true", help="Execute the upload. If not provided, runs in dry-run mode.")

    # Sub-command for multiple file upload
    parser_multiple = subparsers.add_parser("multiple", help="Upload multiple files from a directory matching a regex pattern.")
    parser_multiple.add_argument("--local-dir", required=True, help="Directory to search for files.")
    parser_multiple.add_argument("--regex", required=True, help="Regular expression to match filenames against.")
    parser_multiple.add_argument("--remote-dir", help="Directory in the blob container to place the files. Defaults to the root.")
    parser_multiple.add_argument("--exec", action="store_true", help="Execute the upload. If not provided, runs in dry-run mode.")

    args = parser.parse_args()

    # Assign args to local variables for clarity
    vault_addr = args.vault_addr
    role_id = args.role_id
    secret_id = args.secret_id
    mount_point = args.mount_point
    secret_path = args.secret_path
    debug_log = args.debug_log
    command = args.command

    LogConfiguration("BK-JOB-APACHE-LOG", debug_log=debug_log).config()
    
    client.load_to_env()

    key_pairs = project.build_key_pairs(
        az_tenant_id="tenant_id",
        az_app_id="app_id",
        az_secret="secret_value",
        az_account="storage_account_name",
        az_container_name="container_name"
    )

    if command == "single":
        local_filename = os.path.abspath(args.local_file)
        if not os.path.isfile(local_filename):
            logger.error("File not found at '%s'", local_filename)
            return

        rename_as = args.rename_as
        remote_dir = args.remote_dir
        execute = args.exec

        blob_name = rename_as or os.path.basename(local_filename)

        remote_path = f"{remote_dir}/{blob_name}" if remote_dir else blob_name
        if remote_path.startswith("/"):
            remote_path = remote_path[1:]

        if execute:
            logger.info("Uploading single file: %s to %s", local_filename, remote_path)
            project.file_upload(
                vault_addr=vault_addr,
                role_id=role_id,
                secret_id=secret_id,
                mount_point=mount_point,
                secret_path=secret_path,
                keyPairs=key_pairs,
                file=local_filename,
                remote_filename=remote_path
            )
        else:
            logger.info("[Dry Run] Would upload single file: %s to %s", local_filename, remote_path)
    elif command == "multiple":
        local_dir = args.local_dir
        regex_pattern = args.regex
        remote_dir = args.remote_dir
        execute = args.exec

        files_to_upload = []
        try:
            regex = re.compile(regex_pattern)
        except re.error as e:
            logger.error("Invalid regular expression: %s", e)
            return
        try:
            for filename in os.listdir(local_dir):
                if regex.match(filename) and os.path.isfile(os.path.join(local_dir, filename)):
                    files_to_upload.append(os.path.join(local_dir, filename))
        except FileNotFoundError:
            logger.error("Directory not found: '%s'", local_dir)

        if not files_to_upload:
            logger.warning("No files found in '%s' matching regex: '%s'", local_dir, regex_pattern)
            return

        logger.info("Found %d files to process.", len(files_to_upload))
        for file_path in files_to_upload:
            if os.path.isfile(file_path):
                blob_name = os.path.basename(file_path)
                remote_path = f"{remote_dir}/{blob_name}" if remote_dir else blob_name
                if remote_path.startswith("/"):
                    remote_path = remote_path[1:]
                
                remote_filename = remote_path

                if execute:
                    try:
                        logger.info("Uploading: %s to %s", file_path, remote_filename)
                        project.file_upload(
                            vault_addr=vault_addr,
                            role_id=role_id,
                            secret_id=secret_id,
                            mount_point=mount_point,
                            secret_path=secret_path,
                            keyPairs=key_pairs,
                            file=file_path,
                            remote_filename=remote_path
                        )
                    except Exception as e:
                        logger.error("Failed to upload %s. Error: %s", file_path, e)
                else:
                    logger.info("[Dry Run] Would upload: %s to %s", file_path, remote_path)
