
# bk-job-xethhung12

A command-line tool to back up local files to Azure Blob Storage, using credentials securely fetched from HashiCorp Vault.

## Execution

### General Help
Run through python interpreter:
```shell
python -m bk_job_xethhung12 --help
```

Run through python project script
```shell
bk-job-xethhung12 -h
```

### Demo

Assuming:
* the vault server address is `https://vault.example.com`
* the role id is `aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee`
* the secret id is `gggggggg-hhhh-iiii-jjjj-kkkkkkkkkkkk`
* the mounting point for secret is `system-a`
* the path for secret is `bk/agent1`
* the file to be uploaded `example.log`
* the remote director for the blob `bk/agent1/logs`


```shell
valut_address=https://vault.example.com
role_id=aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee
secret_id=gggggggg-hhhh-iiii-jjjj-kkkkkkkkkkkk
mount_point=system-a
secret_path=bk/agent1

local_file=example.log
remote_dir=bk/agent1/logs

# Dry run
bk-job-xethhung --vault-address $valut_address \
    --role-id $role_id \
    --secret-id $secret_id \
    --mount-point $mount_point \
    --secret-path $secret_path \
    single --local-file $local_file \
    --remote-dir $remote_dir

## Expeced result as
# [BK-JOB-APACHE-LOG] [Dry Run] Would upload single file: /home/ubuntu/example.log to bk/agent1/logs/example.log

# Execute
bk-job-xethhung --vault-address $valut_address \
    --role-id $role_id \
    --secret-id $secret_id \
    --mount-point $mount_point \
    --secret-path $secret_path \
    single --local-file $local_file \
    --remote-dir $remote_dir \
    --exec

## Expeced result as
# [BK-JOB-APACHE-LOG] Uploading single file: /home/ubuntu/example.log to bk/agent1/logs/example.log
# .
# .
# .
# [BK-JOB-APACHE-LOG] Successfully uploaded new blob 'bk/agent1/logs/example.log'.
```

The is antoher multipe command for uploading specified directory files, the files is filtered by regular expression through command argument `--regex`. For example, if the want to upload all shell script to remote blob, can pass in `.*\.sh` as filter. 

Please be don't append the `--exec` argument, until you confirm the regular expression filter work perfectly as you expected.

## Development
The project requires `python` (3+ version) installed and `pip` ready for use on adding manage dependencies

#### Tools
|Name|Platform|Type|Description|
|---|---|---|---|
|install-dependencies.sh|shell|script| The scripts for installing depencies required|
|build.sh|shell|script| The scripts for build the package|
|build-and-deploy.sh|shell|script| The scripts for build and deploy the package|

* install-dependencies.sh
The script will install dependencies listed in `dev-requirements.txt` and `requirements.txt`. The first requirement file contains the dependencies for development like build and deploy tools. The second requirement file defined all required dependencies for the making the package works (**actual dependencies**).

## Useful Scripts
### Project Versioning
For version update in `pyproject.toml`.
This project use package [`xh-py-project-versioning`](https://github.com/xh-dev/xh-py-project-versioning) to manipulate the project version.

Simple usage includes:\
Base on current version, update the patch number with dev id
`python -m xh_py_project_versioning --patch` \
In case current version is `0.0.1`, the updated version will be `0.0.2-dev+000` 

To prompt the dev version to official version use command.
`python -m xh_py_project_versioning -r`.
Through the command, version `0.0.2-dev+000` will be prompt to `0.0.2` official versioning.

Base on current version, update the patch number directly
`python -m xh_py_project_versioning --patch -d` \
In case current version is `0.0.1`, the updated version will be `0.0.2` 

Base on current version, update the minor number directly
`python -m xh_py_project_versioning --minor -d` \
In case current version is `0.0.1`, the updated version will be `0.1.0` 

Base on current version, update the minor number directly
`python -m xh_py_project_versioning --minor -d` \
In case current version is `0.0.1`, the updated version will be `1.0.0` 