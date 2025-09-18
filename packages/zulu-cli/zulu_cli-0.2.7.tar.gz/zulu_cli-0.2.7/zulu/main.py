import yaml
import os
import argparse
from typing import Any, Dict, Optional
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

from zulu import secrets_tool
from zulu import aws

class DotDict(dict):
    """A dictionary with dot notation access."""
    def __getattr__(self, item: str):
        value = self.get(item)
        if isinstance(value, dict):
            return DotDict(value)
        return value

    def __setattr__(self, key: str, value):
        self[key] = value

    def __delattr__(self, key: str):
        del self[key]
        

def find_git_root(max_depth: int = 6) -> Optional[str]:
    """Find the root of the git repository starting from the current directory, up to a specified maximum depth."""
    return find_parent_directory_with_file_or_dir('.git', max_depth)

def find_secrets_file(max_depth: int = 6,environment_long_name: str = "dev") -> Optional[str]:
    """Find the root of the git repository starting from the current directory, up to a specified maximum depth."""
    return find_parent_directory_with_file_or_dir(f'envs/{environment_long_name}/secrets.yaml', max_depth)

def find_secrets_file_by_client(max_depth: int = 6,environment_long_name: str = "dev", client_name:str = "zulu") -> Optional[str]:
    """Find the root of the git repository starting from the current directory, up to a specified maximum depth."""
    return find_parent_directory_with_file_or_dir(f'envs/{environment_long_name}/{client_name}/secrets.yaml', max_depth)

def find_envs_root(max_depth: int = 6) -> Optional[str]:
    """Find the root of the git repository starting from the current directory, up to a specified maximum depth."""
    return find_parent_directory_with_file_or_dir('envs', max_depth)

def find_config_file(max_depth: int = 6) -> Optional[str]:
    """Find the .config.yaml file in the current folder or parent folders, up to a specified maximum depth."""
    return find_parent_directory_with_file_or_dir('.config.yaml', max_depth)

def find_parent_directory_with_file_or_dir(name: str, max_depth: int = 6) -> Optional[str]:
    """Find a directory containing the specified file or directory name, up to a specified maximum depth."""
    current_path = os.getcwd()
    depth = 0

    while current_path != os.path.dirname(current_path) and depth < max_depth:
        target_path = os.path.join(current_path, name)
        if os.path.exists(target_path):
            return target_path if os.path.isfile(target_path) else current_path
        current_path = os.path.dirname(current_path)
        depth += 1

    return None

def load_yaml(file_path: str) -> DotDict:
    """Load YAML file and return a DotDict."""
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
    return DotDict(data)

def get_nested_attr(data: DotDict, attr_path: str):
    """Get nested attribute using dot notation."""
    attrs = attr_path.split('.')
    current = data
    for attr in attrs:
        current = getattr(current, attr)
    return current

class BaseCommand:
    def __init__(self, parser):
        self.parser = parser

    def add_arguments(self):
        pass

    def execute(self, args):
        pass

class ConfigsCommand(BaseCommand):
    def __init__(self, parser):
        super().__init__(parser)

    def add_arguments(self):
        self.parser.add_argument('--read', metavar='VARIABLE', type=str, nargs='?',
                                 help='Read the entire configuration or a specific variable using dot notation')

    def execute(self, args):
        config_path = find_config_file()

        if not config_path:
            print("Error: .config.yaml file not found.")
            return

        config = load_yaml(config_path)
        if args.read is not None:
            if args.read == 'all':
                print(config)
            else:
                try:
                    value = get_nested_attr(config, args.read)
                    print(value)
                except AttributeError:
                    print(f"Error: Variable '{args.read}' not found in the configuration.")
        else:
            self.parser.print_help()

class SecretsCommand(BaseCommand):
    ENVIRONMENTS_LONG_NAMES = {
        'dev': 'develop',
        'develop': 'develop',
        'demo': 'production',
        'stg': 'stage',
        'stage': 'stage',
        'prd': 'production',
        'production': 'production'
    }

    def __init__(self, parser):
        super().__init__(parser)

    def add_arguments(self):
        self.parser.add_argument('--env', choices=self.ENVIRONMENTS_LONG_NAMES.keys(),
                                 help='Specify environment (dev, stg, prd)')
        self.parser.add_argument('--encrypt', action='store_true',
                                 help='Encrypt secrets')
        self.parser.add_argument('--decrypt', action='store_true',
                                 help='Decrypt secrets')
        self.parser.add_argument('--client')
    def execute(self, args):
        if args.env:
            environment = self.ENVIRONMENTS_LONG_NAMES.get(args.env)
            secrets_path = find_secrets_file(environment_long_name=environment)

            if environment:
                if args.encrypt and args.decrypt:
                    print("Error: Cannot specify both --encrypt and --decrypt.")
                    return
                elif args.encrypt:
                    if secrets_path:
                        secret: Dict[str, Any] = aws.get_secret("ZULU_PRIVATE_KEY_ENVIRONMENT_SECRETS", region_name="us-east-1", environment=environment)
                        secrets_tool.encrypt_yaml_file(secrets_path,secret)
                        if args.client:
                            company_secrets_path = find_secrets_file_by_client(environment_long_name=environment,client_name=args.client)
                            if company_secrets_path:
                                secrets_tool.encrypt_yaml_file(company_secrets_path,secret)
                        print("{}")
                    else:
                        print("Error: Secrets file not found.")
                elif args.decrypt:
                    if secrets_path:
                        secret: Dict[str, Any] = aws.get_secret("ZULU_PRIVATE_KEY_ENVIRONMENT_SECRETS", region_name="us-east-1", environment=environment)
                        secrets_tool.decrypt_yaml_file(secrets_path,secret)
                        if args.client:
                            company_secrets_path = find_secrets_file_by_client(environment_long_name=environment,client_name=args.client)
                            if company_secrets_path:
                                secrets_tool.decrypt_yaml_file(company_secrets_path,secret)
                        print("{}")
                    else:
                        print("{}")
                else:
                    print("No operation specified. Use --encrypt or --decrypt.")

            else:
                print("Error: Invalid environment specified.")
        else:
            print("Error: --env argument is required.")
            self.parser.print_help()

def main():
    parser = argparse.ArgumentParser(prog='zulu', description="Zulu CLI.")

    subcommands = {
        'configs': ConfigsCommand,
        'secrets': SecretsCommand,
        # Add more subcommands as needed
    }

    subparsers = parser.add_subparsers(dest='command', help='Subcommands')

    for command_name, command_class in subcommands.items():
        command_parser = subparsers.add_parser(command_name, help=f'Manage {command_name}')
        command_instance = command_class(command_parser)
        command_instance.add_arguments()

    args = parser.parse_args()

    if args.command:
        command_class = subcommands.get(args.command)
        if command_class:
            command_instance = command_class(parser)
            command_instance.execute(args)
        else:
            print(f"Error: Unknown command '{args.command}'")
            parser.print_help()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()