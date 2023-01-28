"""
    Copyright (c) 2022. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/verbacratis/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

from logging import Logger
import traceback
import hashlib
import uuid
from pathlib import Path
import os
# from os import access, R_OK
# from os.path import isfile
import sys
import copy
from sqlalchemy import create_engine
import yaml
from verbacratis.utils.file_io import get_directory_from_path, get_file_from_path
from verbacratis.models import GenericLogger
from verbacratis.models.ordering import Item, Items, get_ordered_item_list_for_named_scope


AWS_REGIONS = (
    "af-south-1",
    "ap-south-1",
    "eu-north-1",
    "eu-west-3",
    "eu-west-2",
    "eu-west-1",
    "ap-northeast-3",
    "ap-northeast-2",
    "ap-northeast-1",
    "ca-central-1",
    "sa-east-1",
    "ap-southeast-1",
    "ap-southeast-2",
    "eu-central-1",
    "us-east-1",
    "us-east-2",
    "us-west-1",
    "us-west-2",
)


DEFAULT_CONFIG_DIR = '{}{}{}'.format(
    str(Path.home()),
    os.sep,
    '.verbacratis'
)

DEFAULT_STATE_DB = 'sqlite:///{}{}{}'.format(
    DEFAULT_CONFIG_DIR,
    os.sep,
    '.verbacratis.db'
)

DEFAULT_GLOBAL_CONFIG = """---
apiVersion: v1-alpha
kind: Project
metadata:
  name: test
spec:
  environments:
  - name: default
  includeFileRegex:
  - '*\.yml'
  - '*\.yaml'
  locations:
    files:
    - path: {}{}/default_project.yaml
      type: YAML
---
apiVersion: v1-alpha
kind: GlobalConfiguration
metadata:
  name: verbacratis
spec:
  stateStore:
    provider: sqlalchemy
    dbConfig:
      url: "{}"
  logging:
    handlers:
    - name: StreamHandler
      parameters:
    - parameterName: format
      parameterType: str
      parameterValue: '%(funcName)s:%(lineno)d -  %(levelname)s - %(message)s'
  infrastructureAccounts:
  - accountName: deployment-host
    accountProvider: ShellScript
    authentication:
      runOnDeploymentHost: true
""".format(DEFAULT_STATE_DB, DEFAULT_CONFIG_DIR, os.sep)


class Project(Item):

    def __init__(
        self,
        name: str,
        logger: GenericLogger = GenericLogger(),
        use_default_scope: bool = True
    ):
        super().__init__(name, logger, use_default_scope)
        self.manifest_directories = list()  # List of dict with items "path" and "type", where type can only be YAML (for now at least)
        self.manifest_files = list()        # List of dict with items "path" and "type", where type can only be YAML (for now at least)
        self.include_file_regex = ('*\.yml', '*\.yaml')
        self.project_effective_manifest = None      # The manifest for the particular scopes
        self.previous_project_checksum = dict()     # Checksum of the previous effective manifest, per environment (scope)
        self.current_project_checksum = None        # The current checksum of the project_effective_manifest

    def add_environment(self, environment_name: str):
        self.add_scope(scope_name=environment_name)
        # self.environments.append(environment_name)

    def add_parent_project(self, parent_project_name: str):
        self.add_parent_item_name(parent_item_name=parent_project_name)

    def add_manifest_directory(self, path: str, type: str='YAML'):
        self.manifest_directories.append({'path': path, 'type': type})

    def override_include_file_regex(self, include_file_regex: tuple):
        self.include_file_regex = include_file_regex

    def add_manifest_file(self, path: str, type: str='YAML'):
        self.manifest_files.append({'path': path, 'type': type})

    def get_environment_names(self)->list:
        return self.scopes

    def as_dict(self):
        root = dict()
        root['spec'] = dict()
        root['apiVersion'] = 'v1-alpha'
        root['kind'] = 'Project'
        root['metadata'] = dict()
        root['metadata']['name'] = self.name
        root['spec'] = dict()
        data = dict()
        # data['name'] = self.name
        data['includeFileRegex'] = list()
        if len(self.include_file_regex) > 0:
            for file_regex in self.include_file_regex:
                data['includeFileRegex'].append(file_regex)
        if len(self.manifest_directories) > 0:
            if 'locations' not in data:
                data['locations'] = dict()
            data['locations']['directories'] = list()
            for directory in self.manifest_directories:
                if 'path' in directory and 'type' in directory:
                    directory_data = {
                        'path': directory['path'],
                        'type': directory['type'],
                    }
                    data['locations']['directories'].append(directory_data)
        if len(self.manifest_files) > 0:
            if 'locations' not in data:
                data['locations'] = dict()
            data['locations']['files'] = list()
            for file in self.manifest_files:
                if 'path' in directory and 'type' in file:
                    file_data = {
                        'path': file['path'],
                        'type': file['type'],
                    }
                    data['locations']['files'].append(file_data)
        data['environments'] = [{'name': 'default'},]
        if len(self.scopes) > 0:
            data['environments'] = list()
            for scope_name in self.scopes:
                data['environments'].append({'name': scope_name, })
        if len(self.parent_item_names) > 0:
            data['parentProjects'] = list()
            for parent_name in self.parent_item_names:
                data['parentProjects'].append({'name': parent_name,})
        root['spec'] = data
        return root

    def __str__(self)->str:
        return yaml.dump(self.as_dict())


class Projects(Items):

    def __init__(self, logger: GenericLogger = GenericLogger()):
        super().__init__(logger)
        self.project_names_per_environment = dict()

    def add_project(self, project: Project):
        self.add_item(item=project)
        for environment_name in project.scopes:
            if environment_name not in self.project_names_per_environment:
                self.project_names_per_environment[environment_name] = list()
            self.project_names_per_environment[environment_name].append(project.name)
            

    def get_project_names_for_named_environment(self, environment_name: str='default')->list:
        if environment_name in self.project_names_per_environment:
            return self.project_names_per_environment[environment_name]
        raise Exception('Environment named "{}" not found in collection of projects'.format(environment_name))

    def get_project_by_name(self, project_name: str)->Project:
        return self.get_item_by_name(name=project_name)

    def __str__(self)->str:
        yaml_str = ''
        for project_name, project in self.items.items():
            yaml_str = '{}---\n{}'.format(yaml_str, str(project))
        return yaml_str


class UnixHostAuthentication:
    """Base class for remote Unix host authentication

    Attributes:
        hostname: A string containing the hostname or IP address of the remote host
    
    """
    def __init__(self, hostname: str) -> None:
        self.authentication_type = None
        self.hostname = hostname
        self.username = None

    def as_dict(self):
        root = dict()
        root['spec'] = dict()
        root['apiVersion'] = 'v1-alpha'
        root['kind'] = 'InfrastructureAccount'
        root['metadata'] = dict()
        root['metadata']['name'] = self.hostname
        root['spec'] = dict()
        data = dict()
        data['authenticationType'] = self.authentication_type
        root['spec'] = data
        return root

    def __str__(self)->str:
        return yaml.dump(self.as_dict())


class SshHostBasedAuthenticationConfig(UnixHostAuthentication): 
    """For hosts with configuration defined in /etc/ssh
    
    This would be similar to SSH to a host using the command `ssh username@hostname`

    Attributes:
        hostname: A string containing the hostname or IP address of the remote host
        username: The username to authenticate against
    """

    def __init__(self, hostname: str, username: str) -> None:
        super().__init__(hostname)
        if username is None:
            raise Exception('username is required')
        if not isinstance(username, str):
            raise Exception('username must be a string value')
        if len(username) == 0:
            raise Exception('username is required')
        self.authentication_type = 'SshUsingHostConfig'
        self.username = username

    def as_dict(self):
        root = dict()
        root['spec'] = dict()
        root['apiVersion'] = 'v1-alpha'
        root['kind'] = 'InfrastructureAccount'
        root['metadata'] = dict()
        root['metadata']['name'] = '{}@{}'.format(self.username, self.hostname)
        root['spec'] = dict()
        data = dict()
        data['authenticationType'] = self.authentication_type
        root['spec'] = data
        return root


class SshCredentialsBasedAuthenticationConfig(SshHostBasedAuthenticationConfig):
    """For hosts requiring SSH with password based authentication
    
    The password attribute can contain an environment variable directive for example: 
    `{EnvironmentVariables:computed:systemXyzPassword}` - this environment variable will have to be defined in the 
    `EnvironmentVariables` kind manifest.

    Attributes:
        hostname: A string containing the hostname or IP address of the remote host
        username: The username to authenticate against
        password: The password for authentication WARNING: Never store password in version control or in clear text files!
    """
    def __init__(self, hostname: str, username: str, password: str) -> None:
        super().__init__(hostname, username)
        self.password = password
        self.password_is_final = True
        if password.startswith('${') and password.endswith('}'):
            self.password_is_final = False                          # Password still needs to be resolved via Environment...
        self.authentication_type = 'SshUsingCredentials'

    def as_dict(self):
        root = dict()
        root['spec'] = dict()
        root['apiVersion'] = 'v1-alpha'
        root['kind'] = 'InfrastructureAccount'
        root['metadata'] = dict()
        root['metadata']['name'] = '{}@{}'.format(self.username, self.hostname)
        root['spec'] = dict()
        data = dict()
        data['authenticationType'] = self.authentication_type
        if len(self.password) > 0:
            data['password'] = '*'*len(self.password)
            if self.password_is_final is False:
                data['password'] = self.password
        root['spec'] = data
        return root


class SshPrivateKeyBasedAuthenticationConfig(SshHostBasedAuthenticationConfig):
    """For hosts requiring SSH with authentication using a private key
    
    Attributes:
        hostname: A string containing the hostname or IP address of the remote host
        username: The username to authenticate against
        private_key_path: Path to the private key

    Raises:
        Exception: If the private key value is not valid or the file cannot be read when creating an instance of this object, and exception will be thrown
    """
    def __init__(self, hostname: str, username: str, private_key_path: str) -> None:
        super().__init__(hostname, username)
        if os.path.isfile(private_key_path) is False:
            raise Exception('Private Key file "{}" does not exist'.format(private_key_path))
        if os.access(private_key_path, os.R_OK) is False:
            raise Exception('Private Key file "{}" cannot be read'.format(private_key_path))
        self.private_key_path = private_key_path
        self.authentication_type = 'SshUsingPrivateKey'

    def as_dict(self):
        root = dict()
        root['spec'] = dict()
        root['apiVersion'] = 'v1-alpha'
        root['kind'] = 'InfrastructureAccount'
        root['metadata'] = dict()
        root['metadata']['name'] = '{}@{}'.format(self.username, self.hostname)
        root['spec'] = dict()
        data = dict()
        data['authenticationType'] = self.authentication_type
        data['privateKeyPath'] = self.private_key_path
        root['spec'] = data
        return root


class AwsAuthentication:

    def __init__(
        self,
        account_reference: str,
        region: str=os.getenv('AWS_DEFAULT_REGION', 'eu-central-1')
    ):
        self.account_reference = account_reference
        self.region = region.lower()
        if os.getenv('AWS_REGION', None) is not None:
            if os.getenv('AWS_REGION').lower() in AWS_REGIONS:
                self.region = os.getenv('AWS_REGION').lower()

    def as_dict(self):
        root = dict()
        root['apiVersion'] = 'v1-alpha'
        root['kind'] = 'AwsAuthentication'
        root['metadata'] = dict()
        root['metadata']['name'] = '{}'.format(self.account_reference)
        root['spec'] = dict()
        root['spec']['region'] = self.region
        return root

    def __str__(self)->str:
        return yaml.dump(self.as_dict())


class AwsKeyBasedAuthentication(AwsAuthentication):
    """For AWS accounts not defined as profiles and not using environment variables but access and secret keys instead
    
    The secret_key attribute can contain an environment variable directive for example: 
    `${EnvironmentVariables:computed:someSecret}` - this environment variable will have to be defined in the 
    `EnvironmentVariables` kind manifest.

    Manifest Format:

        apiVersion: v1-alpha
        kind: AwsKeyBasedAuthentication
        metadata:
            name: default
        spec:
            access_key: abc
            region: eu-central-1
            secret_key: ${{EnvironmentVariables:computed:someSecret}}

    Attributes:
        account_reference: A string with a name that can be referenced by other resources
        access_key: A string containing the access key value
        secret_key: A string containing the secret key value
        region: The AWS region for this config. Must be one as defined in `AWS_REGIONS`
    """
    def __init__(
        self,
        account_reference: str,
        access_key: str = os.getenv('AWS_ACCESS_KEY_ID', ''),
        secret_key: str = os.getenv('AWS_SECRET_ACCESS_KEY', ''),
        region: str = os.getenv('AWS_DEFAULT_REGION', 'eu-central-1')
    ):
        super().__init__(account_reference, region)
        self.access_key = access_key
        self.secret_key = secret_key
        self.secret_key_is_final = True
        if secret_key.startswith('${') and secret_key.endswith('}'):
            self.secret_key_is_final = False                        # Secret key still needs to be resolved via Environment...

    def as_dict(self):
        root = dict()
        root['apiVersion'] = 'v1-alpha'
        root['kind'] = 'AwsKeyBasedAuthentication'
        root['metadata'] = dict()
        root['metadata']['name'] = '{}'.format(self.account_reference)
        root['spec'] = dict()
        root['spec']['region'] = self.region
        root['spec']['access_key'] = self.access_key
        if len(self.secret_key) > 0:
            root['spec']['secret_key'] = '*'*len(self.secret_key)
            if self.secret_key_is_final is False:
                root['spec']['secret_key'] = self.secret_key
        return root

    def __str__(self)->str:
        return yaml.dump(self.as_dict())


class AwsProfileBasedAuthentication(AwsAuthentication):
    """For AWS accounts not defined as profiles and not using environment variables but access and secret keys instead
    
    The secret_key attribute can contain an environment variable directive for example: 
    `{EnvironmentVariables:computed:someSecret}` - this environment variable will have to be defined in the 
    `EnvironmentVariables` kind manifest.

    Attributes:
        account_reference: A string with a name that can be referenced by other resources
        access_key: A string containing the access key value
        secret_key: A string containing the secret key value
        region: The AWS region for this config. Must be one as defined in `AWS_REGIONS`
    """
    def __init__(
        self,
        account_reference: str,
        profile_name: str = os.getenv('AWS_PROFILE', ''),
        region: str = os.getenv('AWS_DEFAULT_REGION', 'eu-central-1')
    ):
        super().__init__(account_reference, region)
        self.profile_name = profile_name
        if len(self.profile_name) == 0:
            raise Exception('Profile name cannot have zero length')

    def as_dict(self):
        root = dict()
        root['apiVersion'] = 'v1-alpha'
        root['kind'] = 'AwsProfileBasedAuthentication'
        root['metadata'] = dict()
        root['metadata']['name'] = '{}'.format(self.account_reference)
        root['spec'] = dict()
        root['spec']['region'] = self.region
        root['spec']['profile_name'] = self.profile_name
        return root

    def __str__(self)->str:
        return yaml.dump(self.as_dict())



class InfrastructureAccount:
    """Defines an Infrastructure account

    There are a couple of types of Infrastructure accounts, and they may have a number of different configuration attributes:

    * ShellScript type accounts: These are accounts that represent a Unix type host, and can be either the localhost on which the deployment script is run, or a remote host with SSH access
    * AWS type account: Represents an AWS account (see https://docs.aws.amazon.com/organizations/latest/userguide/orgs_getting-started_concepts.html)

    ShellScript type accounts on remote hosts with SSH access requires the following values in the "authentication_config" attribute:

    * "authenticationType" (must be set to "SSH" as the only value for now)
    * "username"
    * "privateKeyLocation" (location to the private key file) OR "password" (the actual password, which can be securely obtained with the value "${EnvironmentVariables:computed:systemXyzPassword}")

    AWS type accounts requires the following values in the "authentication_config" attribute:

    * For authentication using AWS profiles:
            * useProfile - Boolean Value - OPTIONAL: Default=false assuming then that the standard AWS CLI Environment Variables are used
            * profileName - String - OPTIONAL, but required if "useProfile" is "true" - Automatically sets the environment variable "PROFILE". Used by the cloud provider code.
            * region - String - OPTIONAL, default=eu-central-1
    * For authentication using keys, used when "useProfile" is FALSE (and therefore requiring the following values to be set):
            * awsAccessKeyId - String - can be securely set with the value "${EnvironmentVariables:computed:awsAccessKeyId}"
            * awsSecretAccessKey - String - can be securely set with the value "${EnvironmentVariables:computed:awsSecretAccessKey}"

    By default there is always at least ONE InfrastructureAccount account with the following configuration:

    * account_name='deployment-host',
    * account_provider='ShellScript',
    * run_on_deployment_host=True,
    * authentication_config=dict(),
    * environments=['default',]

    Attributes:
        account_name: A string containing a unique account name that can be referenced in the deployment configuration
        environments: A list of environments for which this infrastructure account is used
    """

    def __init__(
        self,
        account_name: str='deployment-host',
        environments: list=['default',]
    ):
        self.account_name = account_name
        self.environments = environments
        self.account_provider = None

    def as_dict(self)->dict:
        root = dict()
        root['spec'] = dict()
        root['apiVersion'] = 'v1-alpha'
        root['kind'] = 'InfrastructureAccount'
        root['metadata'] = dict()
        root['metadata']['name'] = self.account_name
        return root

    def auth_id(self)->str:
        return 'no-auth'

    def __str__(self)->str:
        return yaml.dump(self.as_dict())


class UnixInfrastructureAccount(InfrastructureAccount):
    """Defines an Infrastructure account

    There are a couple of types of Infrastructure accounts, and they may have a number of different configuration attributes:

    * ShellScript type accounts: These are accounts that represent a Unix type host, and can be either the localhost on which the deployment script is run, or a remote host with SSH access
    * AWS type account: Represents an AWS account (see https://docs.aws.amazon.com/organizations/latest/userguide/orgs_getting-started_concepts.html)

    ShellScript type accounts on remote hosts with SSH access requires the following values in the "authentication_config" attribute:

    * "authenticationType" (must be set to "SSH" as the only value for now)
    * "username"
    * "privateKeyLocation" (location to the private key file) OR "password" (the actual password, which can be securely obtained with the value "${EnvironmentVariables:computed:systemXyzPassword}")

    AWS type accounts requires the following values in the "authentication_config" attribute:

    * For authentication using AWS profiles:
            * useProfile - Boolean Value - OPTIONAL: Default=false assuming then that the standard AWS CLI Environment Variables are used
            * profileName - String - OPTIONAL, but required if "useProfile" is "true" - Automatically sets the environment variable "PROFILE". Used by the cloud provider code.
            * region - String - OPTIONAL, default=eu-central-1
    * For authentication using keys, used when "useProfile" is FALSE (and therefore requiring the following values to be set):
            * awsAccessKeyId - String - can be securely set with the value "${EnvironmentVariables:computed:awsAccessKeyId}"
            * awsSecretAccessKey - String - can be securely set with the value "${EnvironmentVariables:computed:awsSecretAccessKey}"

    By default there is always at least ONE InfrastructureAccount account with the following configuration:

    * account_name='deployment-host',
    * run_on_deployment_host=True,
    * authentication_config=dict(),
    * environments=['default',]

    Attributes:
        account_name: A string containing a unique account name that can be referenced in the deployment configuration
        run_on_deployment_host: a boolean value. Only ONE InfrastructureAccount can have the value of TRUE and it must be of type "ShellScript"
        authentication_config: The authentication parameters depending on the "account_provider" type
        environments: A list of environments for which this infrastructure account is used
    """
    def __init__(
        self,
        account_name: str='deployment-host',
        run_on_deployment_host: bool=True,
        authentication_config: UnixHostAuthentication = UnixHostAuthentication(hostname='localhost'),
        environments: list=['default',]
    ):
        super().__init__(account_name, environments)
        self.account_provider = 'ShellScript'
        self.run_on_deployment_host = run_on_deployment_host
        self.authentication_config = authentication_config

    def as_dict(self)->dict:
        root = dict()
        root['spec'] = dict()
        root['apiVersion'] = 'v1-alpha'
        root['kind'] = 'UnixInfrastructureAccount'
        root['metadata'] = dict()
        root['metadata']['name'] = self.account_name
        root['spec'] = dict()
        data = dict()
        data['accountProvider'] = self.account_provider
        data['environments'] = self.environments
        if self.run_on_deployment_host is True:
            data['runOnDeploymentHost'] = True
        if self.authentication_config.authentication_type is not None and self.run_on_deployment_host is False:
            data['authentication'] = self.authentication_config.hostname
        root['spec'] = data
        return root

    def auth_id(self)->str:
        if self.authentication_config.username is None:
            return '{}'.format(self.authentication_config.hostname)
        else:
            return '{}@{}'.format(self.authentication_config.username, self.authentication_config.hostname)

    def __str__(self)->str:
        return yaml.dump(self.as_dict())


class AwsInfrastructureAccount(InfrastructureAccount):

    def __init__(
        self,
        account_name: str = 'default',
        environments: list = ['default',],
        authentication_config: AwsAuthentication = AwsAuthentication(account_reference='default'),
    ):
        super().__init__(account_name, environments)
        self.account_provider = 'AWS'
        self.authentication_config = authentication_config


class InfrastructureAccounts:
    """Keeps a collection of Unix and AWS Cloud Infrastructure Accounts
    """
    def __init__(self):    
        self.accounts = {'deployment-host': UnixInfrastructureAccount(),}
        self.host_authentication_configurations = {
            self.accounts['deployment-host'].authentication_config.hostname: self.accounts['deployment-host'].authentication_config,
        }

    def find_local_deployment_host_account_name(self)->str:
        for account_name, infrastructure_account_obj in self.accounts.items():
            if infrastructure_account_obj.run_on_deployment_host is True:
                return account_name
        raise Exception('Critical error: No account found for running on local host')

    def add_infrastructure_account(self, infrastructure_account: UnixInfrastructureAccount):
        if infrastructure_account.run_on_deployment_host is True:
            self.accounts.pop(self.find_local_deployment_host_account_name())
            infrastructure_account.authentication_config = dict()
            infrastructure_account.account_provider = 'ShellScript'
        self.accounts[infrastructure_account.account_name] = infrastructure_account
        if infrastructure_account.auth_id() not in self.host_authentication_configurations:
            self.host_authentication_configurations[infrastructure_account.auth_id()] = infrastructure_account.authentication_config

    def update_local_deployment_host_with_all_environments(self, environments: list):
        if len(environments) is None:
            raise Exception('At least one environment name must be set')
        if len(environments) == 0:
            raise Exception('At least one environment name must be set')
        self.accounts[self.find_local_deployment_host_account_name()].environments = environments

    def as_dict(self)->dict:
        accounts_list =list()
        host_authentication_configurations_list = list()

        for inf_acc_name, inf_acc_obj in self.accounts.items():
            accounts_list.append(inf_acc_obj)

        for host_auth_conf_name, host_auth_conf_obj in self.accounts.items():
            host_authentication_configurations_list.append(host_auth_conf_obj)

        return {
            'infrastructure_accounts': accounts_list,
            'host_authentication_configurations': host_authentication_configurations_list,
        }

    def __str__(self)->str:
        config_as_str = ''
        data = self.as_dict()
        for host_auth_conf_obj in data['host_authentication_configurations']:
            config_as_str = '{}\n---\n{}'.format(config_as_str, str(host_auth_conf_obj))
        for inf_acc_obj in data['infrastructure_accounts']:
            config_as_str = '{}\n---\n{}'.format(config_as_str, str(inf_acc_obj))
        return config_as_str


class StateStore:

    def __init__(
        self,
        provider: str='sqlalchemy',
        connection_url: str='sqlite:///verbacratis.db',
        logger=GenericLogger()
    )->None:
        self.provider = provider
        self.connection_url = connection_url
        self.logger = logger
        self.enable_state = False
        self.engine = None
        self.create_db_engine()

    def create_db_engine(self):
        try:
            self.engine = create_engine(url=self.connection_url, echo=True)
            self.enable_state = True
            # self.logger.info('DB Engine created to Database: {}'.format(self.engine.url))
        except:
            self.logger.error('EXCEPTION: {}'.format(traceback.format_exc()))
            self.enable_state = False
            self.logger.info('State Persistance Disabled')


class ApplicationConfiguration:

    def __init__(self, raw_global_configuration: str=DEFAULT_GLOBAL_CONFIG, logger=GenericLogger()) -> None:
        self.raw_global_configuration = raw_global_configuration
        self.parsed_configuration = dict()
        self.logger = logger
        self.state_store = StateStore(logger=self.logger)
        self.parse_global_configuration()

    def _parse_state_store_section(self, config_as_dict: dict):
        state_store_section = dict()
        if 'spec' in config_as_dict:
            if 'stateStore' in config_as_dict['spec']:
                state_store_section = config_as_dict['spec']['stateStore']
        if 'provider' in state_store_section:
            self.state_store.provider = state_store_section['provider']
        if 'dbConfig' in state_store_section:
            if 'url' in state_store_section['dbConfig']:
                self.state_store.connection_url = state_store_section['dbConfig']['url']

    def _get_spec(self, raw_config: dict):
        spec = dict()
        if 'spec' in raw_config:
            spec = raw_config['spec']
        return spec

    def _parse_state_store_config(self, spec: dict):
        provider = self.state_store.provider
        url = self.state_store.connection_url
        if 'provider' in spec:
            provider = spec['provider']
        if 'dbConfig' in spec:
            if 'url' in spec['dbConfig']:
                url = spec['dbConfig']['url']
        self.state_store = StateStore(provider=provider, connection_url=url, logger=self.logger)

    def parse_global_configuration(self):
        try:
            self.logger.info('Parsing Application Global Configuration')
            parsed_config = yaml.load_all(self.raw_global_configuration, Loader=yaml.FullLoader)
            spec = self._get_spec(raw_config=parsed_config)
            if 'stateStore' in spec:
                self._parse_state_store_config(spec=spec)
            if 'logging' in spec:
                pass
            if 'projects' in spec:
                pass
        except:
            self.logger.error('EXCEPTION: {}'.format(traceback.format_exc()))
            sys.exit(2)


class ApplicationState:

    def __init__(self, logger=GenericLogger()) -> None:
        self.environment = 'default'
        self.project = 'default'
        self.config_directory = DEFAULT_CONFIG_DIR
        self.config_file = 'config'
        self.state_db_url = DEFAULT_STATE_DB
        self.logger = logger
        self.build_id = hashlib.sha256(str(uuid.uuid1()).encode(('utf-8'))).hexdigest()
        self.application_configuration = ApplicationConfiguration(raw_global_configuration=DEFAULT_GLOBAL_CONFIG, logger=self.logger)

    def _read_global_configuration_file_content(self):
        self.application_configuration = ApplicationConfiguration(raw_global_configuration=DEFAULT_GLOBAL_CONFIG, logger=self.logger)
        if Path(self.config_directory).exists() is False:
            Path(self.config_directory).mkdir(parents=True, exist_ok=True)
        config_path = '{}{}{}'.format(
            self.config_directory,
            os.sep,
            self.config_file
        )
        if Path(config_path).exists() is False:
            with open(config_path, 'w') as f:
                f.write(DEFAULT_GLOBAL_CONFIG)
        with open(config_path, 'r') as f:
            self.application_configuration.raw_global_configuration = f.read()

    def update_config_file(self, config_file: str):
        self.config_directory = get_directory_from_path(input_path=config_file)
        self.config_file = get_file_from_path(input_path=config_file)
        self._read_global_configuration_file_content()
        self.application_configuration.parse_global_configuration()
        

