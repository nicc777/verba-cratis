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
import sys
import copy
from sqlalchemy import create_engine
import yaml
from verbacratis.utils import get_logger
from verbacratis.utils.file_io import get_directory_from_path, get_file_from_path
from verbacratis.models import GenericLogger
from verbacratis.models.ordering import Item, Items, get_ordered_item_list_for_named_scope


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

DEFAULT_GLOBAL_CONFIG = """apiVersion: v1-alpha
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
  projects:
  - name: default
    locations:
    - type: ListOfFiles
      files:
      - path: {}{}/default_project.yaml
        type: YAML
    environments:
    - name: default
""".format(DEFAULT_STATE_DB, DEFAULT_CONFIG_DIR, os.sep)


class Project(Item):

    def __init__(self, name: str, logger: GenericLogger = GenericLogger(), use_default_scope: bool = True):
        super().__init__(name, logger, use_default_scope)
        self.environments = list()
        self.manifest_directories = list()
        self.manifest_files = list()
        self.include_file_regex = ('*\.yml', '*\.yaml')
        self.parent_project_names = list()
        self.project_effective_manifest = None      # The manifest for the particular scopes
        self.previous_project_checksum = dict()     # Checksum of the previous effective manifest, per environment (scope)
        self.current_project_checksum = None        # The current checksum of the project_effective_manifest

    def add_environment(self, environment_name: str):
        self.add_scope(scope_name=environment_name)
        # self.environments.append(environment_name)

    def add_parent_project(self, parent_project_name: str):
        self.add_parent_item_name(parent_item_name=parent_project_name)

    def add_manifest_directory(self, directory: str):
        self.manifest_directories.append(directory)

    def override_include_file_regex(self, include_file_regex: tuple):
        self.include_file_regex = include_file_regex

    def add_manifest_file(self, file: str):
        self.manifest_files.append(file)


class Projects(Items):

    def __init__(self, logger: GenericLogger = GenericLogger()):
        super().__init__(logger)
        self.project_names_per_environment = dict()

    def add_project(self, project: Project):
        self.add_item(item=project)


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
        account_provider: A string contaINING Either "ShellScript" or "AWS" (more providers may be supported in the future)
        run_on_deployment_host: a boolean value. Only ONE InfrastructureAccount can have the value of TRUE and it must be of type "ShellScript"
        authentication_config: The authentication parameters depending on the "account_provider" type
        environments: A list of environments for which this infrastructure account is used
    """

    def __init__(
        self,
        account_name: str='deployment-host',
        account_provider: str='ShellScript',
        run_on_deployment_host: bool=True,
        authentication_config: dict=dict(),
        environments: list=['default',]
    ):
        self.account_name = account_name
        self.account_provider = account_provider
        self.run_on_deployment_host = run_on_deployment_host
        self.authentication_config = authentication_config
        self.environments = environments


class InfrastructureAccounts:

    def __init__(self):
        self.accounts = {'deployment-host': InfrastructureAccount()}

    def find_local_deployment_host_account_name(self):
        for account_name, infrastructure_account_obj in self.accounts.items():
            if infrastructure_account_obj.run_on_deployment_host is True:
                return account_name
        raise Exception('Critical error: No account found for running on local host')

    def add_infrastructure_account(self, infrastructure_account: InfrastructureAccount):
        if infrastructure_account.run_on_deployment_host is True:
            self.accounts.pop(self.find_local_deployment_host_account_name())
            infrastructure_account.authentication_config = dict()
            infrastructure_account.account_provider = 'ShellScript'
        self.accounts[infrastructure_account.account_name] = infrastructure_account

    def update_local_deployment_host_with_all_environments(self, environments: list):
        if len(environments) is None:
            raise Exception('At least one environment name must be set')
        if len(environments) == 0:
            raise Exception('At least one environment name must be set')
        self.accounts[self.find_local_deployment_host_account_name()].environments = environments


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
        

