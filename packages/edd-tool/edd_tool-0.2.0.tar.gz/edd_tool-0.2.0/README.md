# EDD Tool

`edd-tool` is a command-line utility for deploying and managing EDD (Effelsberg Direct Digitisation) backend instances.  
It automates cloning site repositories, resolving variables from Ansible inventories, installing plugins, and running playbooks.

## Purpose

The `edd-tool` simplifies the deployment of EDD site repositories managing the docker update cycle and plugin installation phases of an EDD backend deployment.

## Installation

It is strongly recommended to install and run `edd-tool` inside a Python virtual environment to avoid dependency conflicts.

```bash
# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install from PyPI
pip install edd-tool
```

You can verify the installation with:

```bash
edd-tool --help
```

## Basic usage

```
usage: edd-tool deploy [-h] [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}] [--version VERSION] [--deploy-dir DEPLOY_DIR] --inventory
                       INVENTORY --vault-pass-file VAULT_PASS_FILE --site-config SITE_CONFIG
                       [--plugin-install-method {galaxy,git-submodule}] [--no-pullremote] [--force] [--dry-run]
                       project

positional arguments:
  project               Git URL of the EDD site repository

options:
  -h, --help            show this help message and exit
  --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Set the logging level (default: INFO)
  --version VERSION     Branch or tag for the site repository
  --deploy-dir DEPLOY_DIR
                        Deployment directory
  --inventory INVENTORY
                        Ansible inventory path (file, dir, or script)
  --vault-pass-file VAULT_PASS_FILE
                        Path to vault password file
  --site-config SITE_CONFIG
                        Path to site configuration YAML
  --plugin-install-method {galaxy,git-submodule}
  --no-pullremote       Skip pullremote tag
  --force               Force overwrite of deployment directory
  --dry-run             Dry run the deployment
```
