import argparse
import os
import re
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

def camel_to_snake_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).upper()

def snake_to_camel_case(name):
    components = name.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

def fetch_secrets_from_keyvault(keyvault_name):
    credential = DefaultAzureCredential()
    keyvault_url = f"https://{keyvault_name}.vault.azure.net"
    secret_client = SecretClient(vault_url=keyvault_url, credential=credential)

    secrets = {}
    for secret_properties in secret_client.list_properties_of_secrets():
        secret = secret_client.get_secret(secret_properties.name)
        snake_case_name = camel_to_snake_case(secret.name)
        secrets[snake_case_name] = secret.value

    return secrets

def upload_secrets_to_keyvault(keyvault_name, secrets):
    credential = DefaultAzureCredential()
    keyvault_url = f"https://{keyvault_name}.vault.azure.net"
    secret_client = SecretClient(vault_url=keyvault_url, credential=credential)

    for key, value in secrets.items():
        camel_case_name = snake_to_camel_case(key)
        secret_client.set_secret(camel_case_name, value)

def read_from_file(input_file_path):
    secrets = {}
    with open(input_file_path, 'r') as f:
        for line in f:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                secrets[key] = value
    return secrets

def write_to_file(secrets, output_file_path, file_format):
    prefix = "export " if file_format == "export" else ""
    with open(output_file_path, 'w') as f:
        for key, value in secrets.items():
            f.write(f"{prefix}{key}={value}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='This script interacts with Azure Key Vault to either fetch secrets and write them to an output file or read secrets from an input file and upload them to the Key Vault.'
    )
    parser.add_argument('keyvault_name', type=str, help='Name of the Azure Key Vault to interact with.')
    parser.add_argument('--mode', type=str, choices=['fetch', 'upload'], default='fetch', help='Mode of operation: "fetch" to get secrets from Key Vault, "upload" to upload secrets to Key Vault. Defaults to "fetch".')
    parser.add_argument('--file', type=str, help='Path of the .env file for fetching or uploading secrets. Required for "upload" mode.')
    parser.add_argument('--format', type=str, choices=['env', 'export'], default='env', help='Format of the output file when fetching secrets. "env" for .env format and "export" for shell script. Defaults to "env".')

    args = parser.parse_args()

    if args.mode == 'fetch':
        if not args.file:
            args.file = ".env" if args.format == "env" else "env.sh"
        secrets = fetch_secrets_from_keyvault(args.keyvault_name)
        write_to_file(secrets, args.file, args.format)
        print(f"Fetched secrets from Key Vault '{args.keyvault_name}' and written to {args.file}")

    elif args.mode == 'upload':
        if not args.file:
            raise ValueError("Input file path is required in upload mode.")
        secrets = read_from_file(args.file)
        upload_secrets_to_keyvault(args.keyvault_name, secrets)
        print(f"Uploaded secrets from {args.file} to Key Vault '{args.keyvault_name}'")
