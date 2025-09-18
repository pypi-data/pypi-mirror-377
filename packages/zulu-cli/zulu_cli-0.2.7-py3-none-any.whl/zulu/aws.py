import os
import sys
import subprocess
from typing import Any, Dict

import boto3
from botocore.exceptions import (
    NoCredentialsError,
    SSOTokenLoadError,
    ClientError,
    ProfileNotFound,
    UnauthorizedSSOTokenError,
)


def assume_role(
    role_arn: str, external_id: str, session_name: str = "AssumeRoleSession"
) -> Dict[str, str]:
    sts_client = boto3.client("sts")
    try:
        assumed_role_object = sts_client.assume_role(
            RoleArn=role_arn, RoleSessionName=session_name, ExternalId=external_id
        )
        credentials = assumed_role_object["Credentials"]
        return {
            "AccessKeyId": credentials["AccessKeyId"],
            "SecretAccessKey": credentials["SecretAccessKey"],
            "SessionToken": credentials["SessionToken"],
        }
    except Exception as e:
        print(f"Error assuming role {role_arn}: {str(e)}")
        raise e


def get_aws_credentials(profile_name: str) -> Dict[str, str]:
    session = boto3.Session(profile_name=profile_name)
    credentials = session.get_credentials().get_frozen_credentials()
    return {
        "AccessKeyId": credentials.access_key,
        "SecretAccessKey": credentials.secret_key,
        "SessionToken": credentials.token,
    }


def profile_exists(profile_name: str, aws_config_file: str) -> bool:
    if not os.path.exists(aws_config_file):
        return False

    with open(aws_config_file, "r") as f:
        lines = f.readlines()
        return any(line.strip() == f"[profile {profile_name}]" for line in lines)


def configure_aws_sso(
    profile_name: str,
    sso_start_url: str,
    sso_region: str,
    sso_account_id: str,
    sso_role_name: str,
    default_region: str,
) -> None:
    aws_config_dir = os.path.expanduser("~/.aws")
    aws_config_file = os.path.join(aws_config_dir, "config")

    if not os.path.exists(aws_config_dir):
        os.makedirs(aws_config_dir)

    if profile_exists(profile_name, aws_config_file):
        print(f"Profile '{profile_name}' already exists in {aws_config_file}")
        return

    config_content = (
        f"[profile {profile_name}]\n"
        f"sso_start_url = {sso_start_url}\n"
        f"sso_region = {sso_region}\n"
        f"sso_account_id = {sso_account_id}\n"
        f"sso_role_name = {sso_role_name}\n"
        f"region = {default_region}\n"
        f"output = json\n"
    )

    with open(aws_config_file, "a") as f:
        f.write(config_content)

    print(
        f"AWS SSO configuration for profile '{profile_name}' added to {aws_config_file}"
    )


def aws_sso_login(environment: str) -> None:
    required_env_vars = [
        "SSO_START_URL",
        "SSO_ROLE_NAME",
        "SSO_ACCOUNT_ID_DEVELOP",
        "SSO_ACCOUNT_ID_STAGE",
        "SSO_ACCOUNT_ID_PRODUCTION",
    ]
    missing_env_vars = [var for var in required_env_vars if os.getenv(var) is None]

    if missing_env_vars:
        print(f"Error: Missing environment variables: {', '.join(missing_env_vars)}")
        sys.exit(1)

    sso_start_url = os.getenv("SSO_START_URL")
    sso_region = os.getenv("SSO_REGION", "us-east-1")
    sso_role_name = os.getenv("SSO_ROLE_NAME")

    account_ids = {
        "develop": os.getenv("SSO_ACCOUNT_ID_DEVELOP"),
        "stage": os.getenv("SSO_ACCOUNT_ID_STAGE"),
        "production": os.getenv("SSO_ACCOUNT_ID_PRODUCTION"),
    }

    for env, account_id in account_ids.items():
        configure_aws_sso(
            profile_name=f"sso_{env}",
            sso_start_url=sso_start_url,
            sso_region=sso_region,
            sso_account_id=account_id,
            sso_role_name=sso_role_name,
            default_region="us-east-1",
        )

    if environment not in account_ids:
        print(
            f"Error: Invalid environment '{environment}'. Please choose one of: {', '.join(account_ids.keys())}"
        )
        return

    os.environ["AWS_PROFILE"] = f"sso_{environment}"

    try:
        subprocess.run(["aws", "sso", "login"], check=True)
        print(f"Successfully logged in to AWS SSO for environment '{environment}'")
    except subprocess.CalledProcessError as e:
        print(f"Error executing 'aws sso login': {e}")


def is_sso_session_active(profile_name: str) -> bool:
    try:
        session = boto3.Session(profile_name=f"sso_{profile_name}")
        sts_client = session.client("sts")
        sts_client.get_caller_identity()
        return True
    except (SSOTokenLoadError, ClientError, ProfileNotFound, UnauthorizedSSOTokenError):
        return False


def get_secret(
    secret_name: str, region_name: str, environment: str = "develop"
) -> Dict[str, Any]:
    ci_environment = os.getenv("CI", "false").lower() == "true"
    local_environment = os.getenv("LOCAL_CI", "false").lower() == "true"

    if ci_environment:
        role_arn = os.getenv("AWS_ASSUME_ROLE_ARN")
        external_id = os.getenv("AWS_ASSUME_ROLE_EXTERNAL_ID")
        if not role_arn or not external_id:
            raise ValueError(
                "Environment variables AWS_ASSUME_ROLE_ARN and AWS_ASSUME_ROLE_EXTERNAL_ID must be set"
            )
        credentials = assume_role(role_arn, external_id)
    elif local_environment:
        try:
            credentials = get_aws_credentials(environment)
        except NoCredentialsError:
            raise ValueError(f"No credentials found for environment: {environment}")
    else:
        if not is_sso_session_active(environment):
            aws_sso_login(environment)
        session = boto3.Session(profile_name=f"sso_{environment}")
        credentials = session.get_credentials().get_frozen_credentials()

    if isinstance(credentials, dict):
        access_key = credentials["AccessKeyId"]
        secret_key = credentials["SecretAccessKey"]
        session_token = credentials["SessionToken"]
    else:
        access_key = credentials.access_key
        secret_key = credentials.secret_key
        session_token = credentials.token

    client = boto3.client(
        "secretsmanager",
        region_name=region_name,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        aws_session_token=session_token,
    )

    try:
        response = client.get_secret_value(SecretId=secret_name)
        if "SecretString" in response:
            return response["SecretString"]
        else:
            raise ValueError(
                "The secret value is binary and cannot be processed in this script."
            )
    except Exception as e:
        print(f"Error retrieving secret {secret_name}: {str(e)}")
        raise e
