import argparse
import subprocess
import sys
import tempfile
import shutil
import json
import logging
import os
import pprint
from contextlib import contextmanager
from pathlib import Path
import importlib.resources as pkg_resources

import yaml

from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager
from ansible.vars.manager import VariableManager
from ansible.template import Templar
from ansible.parsing.vault import VaultSecret, VaultSecretsContext

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("edd-installer")

def ensure_rc_file():
    """Ensure that ~/.edd-tool.rc exists. Create from template if missing."""
    rc_file = Path.home() / ".edd-tool.rc"
    if rc_file.exists():
        return

    try:
        # Load the packaged template
        with pkg_resources.files("edd_tool.data").joinpath("edd-tool.rc.template").open("r") as template:
            rc_file.write_text(template.read())
        logger.info(f"Created default config file at {rc_file}")
    except Exception as e:
        logger.warning(f"Could not create default RC file: {e}")


@contextmanager
def working_directory(path):
    """Temporarily change the working directory inside the context."""
    original_dir = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(original_dir)


def run_cmd(cmd, cwd=None, check=True, env=None):
    """
    Run a subprocess command.

    Args:
        cmd (list[str]): Command and arguments
        cwd (str|Path, optional): Directory to run command in
        check (bool): Exit on non-zero return code

    Returns:
        str: stdout of the command
    """
    logger.debug(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=False, text=True, check=False, env=env)
    if result.returncode != 0 and check:
        logger.error(f"Command failed: {' '.join(cmd)}")
        sys.exit(result.returncode)


def default_deployment_dir(args):
    """
    Compute the default deployment directory for a site_repo/version/inventory combination.

    Args:
        args (Namespace): Parsed argparse arguments with site_repo, version, inventory

    Returns:
        Path: Absolute path for deployment directory
    """
    site_repo = args.site_repo.split("/")[-1].replace(".git", "")
    path = Path.home() / ".edd" / "deployments" / site_repo / str(args.version) / args.inventory
    return path


def create_deployment_dir(path, force=False):
    """
    Create a deployment directory, optionally clearing it if it exists and is not empty.

    Args:
        path (str|Path): Path to create
        force (bool): If True, remove contents if directory exists

    Returns:
        Path: Absolute path of the deployment directory
    """
    path = Path(path).absolute()
    if path.exists():
        if any(path.iterdir()):
            if not force:
                raise RuntimeError(f"Deployment directory {path} already exists and is not empty. Use --force to override.")
            logger.warning(f"Deployment directory {path} exists and is not empty. Force enabled, clearing contents.")
            for item in path.iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
    else:
        path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Deployment directory ready: {path}")
    return path


def clone_or_copy_site_repo(site_repo_path, deploy_dir, branch=None):
    """
    Clone a git repository into the deployment directory.

    Args:
        site_repo_path (str): Git URL of the site_repo
        deploy_dir (str|Path): Deployment directory
        branch (str, optional): Branch or tag to checkout
    """
    logger.info(f"Cloning repository from {site_repo_path} into {deploy_dir}")
    if branch:
        run_cmd(["git", "clone", "--single-branch", "--depth", "1", "--branch",
                 branch, site_repo_path, str(deploy_dir)])
    else:
        run_cmd(["git", "clone", "--single-branch", "--depth", "1", site_repo_path, str(deploy_dir)])


def parse_inventory(inventory_source, vault_pass_file=None):
    """
    Parse the Ansible inventory and extract variables and EDD_PLUGINS,
    resolving Jinja2 templates and decrypting vault-encrypted variables.

    Args:
        inventory_source (str): Path to inventory (file, directory, or script)
        vault_pass_file (str, optional): Path to Ansible vault password file

    Returns:
        tuple: (all_vars: dict of merged variables, plugins: list of plugin dicts)
    """
    loader = DataLoader()

    vault_secret = None
    if vault_pass_file:
        with open(vault_pass_file, "rb") as f:
            vault_secret = VaultSecret(f.read().strip())

    if vault_secret:
        VaultSecretsContext.initialize(VaultSecretsContext([("default", vault_secret)]))

    inventory = InventoryManager(loader=loader, sources=[inventory_source])
    variable_manager = VariableManager(loader=loader, inventory=inventory)

    all_vars = {}
    all_plugins = []

    for host in inventory.get_hosts():
        host_vars = variable_manager.get_vars(host=host)
        templar = Templar(loader=loader, variables=host_vars)

        resolved_vars = {k: templar.template(v) if isinstance(v, str) else v
                         for k, v in host_vars.items()}
        all_vars.update(resolved_vars)

        if "EDD_PLUGINS" in resolved_vars:
            rendered_plugins = []
            for plugin in resolved_vars["EDD_PLUGINS"]:
                rendered_plugins.append({k: templar.template(v) if isinstance(v, str) else v
                                         for k, v in plugin.items()})
            all_plugins.extend(rendered_plugins)

    # Deduplicate plugins by JSON-serialized content
    deduped_plugins = list({json.dumps(p, sort_keys=True): p for p in all_plugins}.values())
    logger.info(f"Found {len(deduped_plugins)} plugins after templating and decryption")
    return all_vars, deduped_plugins


def display_vars(vars_dict):
    """
    Pretty-print a dictionary of variables.

    Args:
        vars_dict (dict): Dictionary of variables
    """
    logger.info(pprint.pformat(vars_dict, indent=2))


def install_plugins(plugins, method="galaxy"):
    """
    Install plugins using the specified method.

    Args:
        plugins (list[dict]): List of plugin dictionaries
        method (str): "galaxy" or "git"
    """
    if not plugins:
        logger.info("No plugins to install.")
        return

    if method == "galaxy":
        req_file = tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".yml")
        req_file.write("collections:\n")
        for p in plugins:
            req_file.write(f"  - type: git\n    source: {p['source']}\n    version: \"{p['version']}\"\n")
        req_file.close()
        run_cmd(["ansible-galaxy", "collection", "install", "-r", req_file.name, "-p", "./ansible_collections/"])
    elif method == "git-submodule":
        run_cmd(["git", "submodule", "update", "--init", "--recursive"])
        run_cmd(["git", "submodule", "update", "--remote", "--recursive"])
    else:
        raise NotImplementedError(f"Plugin install method '{method}' is unsupported")


def run_playbook(inventory, vault_args, site_config, tags=None, dry_run=False):
    """
    Run an Ansible playbook.

    Args:
        inventory (str): Inventory path
        vault_args (list[str]): Vault argument list (--vault-password-file or --ask-vault-pass)
        site_config (str): Playbook YAML file
        tags (str, optional): Tags to limit execution
        dry_run (bool): If True, log the command instead of running
    """
    collections = (Path().cwd() / "ansible_collections").absolute()
    env = os.environ.copy()
    env['ANSIBLE_COLLECTIONS_PATH'] = str(collections)
    
    cmd = ["ansible-playbook", "-i", inventory] + vault_args + [site_config]
    if tags:
        cmd.extend(["--tags", tags])

    if dry_run:
        logger.info("Would run: %s", " ".join(cmd))
    else:
        run_cmd(cmd, env=env)


def cmd_install(args):
    """
    Main install/deploy command handler.

    Args:
        args (Namespace): Parsed command-line arguments
    """
    deploy_dir = args.deploy_dir or default_deployment_dir(args)
    logger.info("Creating deployment directory: %s", deploy_dir)
    deploy_dir = create_deployment_dir(deploy_dir, force=args.force)

    # Resolve vault password file
    vault_pass_file = None
    if args.vault_pass_file:
        vault_pass_file = str(Path(args.vault_pass_file).expanduser().absolute())
    elif os.getenv("ANSIBLE_VAULT_PASSWORD_FILE"):
        vault_pass_file = os.getenv("ANSIBLE_VAULT_PASSWORD_FILE")
        logger.debug(f"Using vault password file from environment: {vault_pass_file}")

    if vault_pass_file:
        vault_args = ["--vault-password-file", vault_pass_file]
    else:
        logger.warning("No vault password file provided. Falling back to --ask-vault-pass.")
        vault_args = ["--ask-vault-pass"]

    with working_directory(deploy_dir):
        logger.info("Cloning site repository: %s (version: %s)", args.site_repo, args.version)
        clone_or_copy_site_repo(args.site_repo, "./", branch=args.version)
        logger.info("Parsing ansible inventory")
        vars_dict, plugins = parse_inventory(args.inventory, vault_pass_file)
        display_vars(vars_dict)

        if not args.dry_run:
            logger.info("Installing plugins")
            install_plugins(plugins, method=args.plugin_install_method)
        else:
            for plugin in plugins:
                logger.info("Would install plugin: %s", plugin)

        if not args.no_pullremote:
            logger.info("Pulling docker images")
            run_playbook(args.inventory, vault_args, args.site_config,
                         tags="pullremote", dry_run=args.dry_run)
        logger.info("Running deployment")
        run_playbook(args.inventory, vault_args, args.site_config, dry_run=args.dry_run)
        logger.info("Deployment finished")


def load_rc_config(profile):
    """
    Load configuration profile from ~/.edd-tool.rc.

    Args:
        profile (str): Profile name (e.g. 'production')

    Returns:
        dict: Profile configuration or raises RuntimeError if not found
    """
    rc_path = Path.home() / ".edd-tool.rc"
    if not rc_path.exists():
        logger.warning("No ~/.edd-tool.rc found, skipping profile loading")
        return {}

    with open(rc_path, "r") as f:
        config = yaml.safe_load(f) or {}

    if profile not in config:
        raise RuntimeError(f"Profile '{profile}' not found in {rc_path}")
    return config[profile]


def merge_args_with_profile(args, profile_data):
    """
    Merge profile data into argparse Namespace.
    CLI arguments always override profile values.

    Args:
        args (Namespace): Parsed CLI arguments
        profile_data (dict): Profile defaults
    """
    for key, value in profile_data.items():
        # Argparse converts CLI args to snake_case
        arg_key = key.replace("-", "_")
        current_value = getattr(args, arg_key, None)
        if current_value is None:
            setattr(args, arg_key, value)
            logger.debug(f"Using profile default for {arg_key}={value}")
        else:
            logger.debug(f"CLI override in effect for {arg_key}={current_value}")


def main():
    ensure_rc_file()
    
    """Command-line entry point for the EDD installer with profile support."""
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level (default: INFO)"
    )

    parser = argparse.ArgumentParser(prog="edd-tool", description="EDD Installer Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sp_install = subparsers.add_parser(
        "deploy",
        help="Install and deploy EDD backend instance",
        parents=[parent_parser]
    )
    sp_install.add_argument(
        "config_profile",
        nargs="?",
        help="Optional profile name from ~/.edd-tool.rc (e.g. 'production', 'devel')"
    )
    sp_install.add_argument("--site-repo", help="Git URL of the EDD site repository")
    sp_install.add_argument("--version", default=None, help="Branch or tag for the site repository")
    sp_install.add_argument("--deploy-dir", default=None, help="Deployment directory")
    sp_install.add_argument("--inventory", help="Ansible inventory path (file, dir, or script)")
    sp_install.add_argument(
        "--vault-pass-file",
        help="Path to vault password file (defaults to $ANSIBLE_VAULT_PASSWORD_FILE if set)"
    )
    sp_install.add_argument("--site-config", help="Path to site configuration YAML")
    sp_install.add_argument("--plugin-install-method", choices=["galaxy", "git-submodule"], default="galaxy")
    sp_install.add_argument("--no-pullremote", action="store_true", help="Skip pullremote tag")
    sp_install.add_argument("--force", action="store_true", help="Force overwrite of deployment directory")
    sp_install.add_argument("--dry-run", action="store_true", help="Dry run the deployment")
    sp_install.set_defaults(func=cmd_install)

    args = parser.parse_args()

    # Apply profile defaults if specified
    if args.command == "deploy" and args.config_profile:
        try:
            profile_data = load_rc_config(args.config_profile)
            merge_args_with_profile(args, profile_data)
        except RuntimeError as e:
            logger.error(str(e))
            sys.exit(1)

    # Enforce required arguments AFTER profile merge
    missing = []
    for required in ["site_repo", "inventory", "site_config", "version"]:
        if getattr(args, required, None) is None:
            missing.append(required)
    if missing:
        logger.error(f"Missing required arguments after profile merge: {', '.join(missing)}")
        sys.exit(2)

    # Set log level after parsing
    numeric_level = getattr(logging, args.log_level.upper(), logging.INFO)
    logger.setLevel(numeric_level)
    logging.getLogger().setLevel(numeric_level)
    logger.debug("Log level set to %s", args.log_level)

    args.func(args)




if __name__ == "__main__":
    main()
