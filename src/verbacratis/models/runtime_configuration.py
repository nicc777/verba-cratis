"""
    Copyright (c) 2022-2023. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/verbacratis/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

import traceback
import hashlib
import uuid
from pathlib import Path
import os
import sys
from sqlalchemy import create_engine
import yaml
from urllib.parse import urlparse
import urllib
from verbacratis.utils.file_io import get_directory_from_path, get_file_from_path, init_application_dir
from verbacratis.models import GenericLogger, DEFAULT_CONFIG_DIR, DEFAULT_GLOBAL_CONFIG, DEFAULT_STATE_DB
from verbacratis.models.systems_configuration import SystemConfigurations, InfrastructureAccount, get_yaml_configuration_from_git, get_yaml_configuration_from_url, get_system_configuration_from_files
from verbacratis.utils.git_integration import is_url_a_git_repo


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

    def as_dict(self):
        root = dict()
        root['spec'] = dict()
        root['apiVersion'] = 'v1-alpha'
        root['kind'] = 'StateStore'
        root['metadata'] = dict()
        root['metadata']['name'] = 'verbacratis-state-store'
        root['spec'] = dict()
        root['spec']['provider'] = self.provider
        root['spec']['connectionUrl'] = self.connection_url
        return root

    def __str__(self):
        return yaml.dump(self.as_dict())


class ApplicationRuntimeConfiguration:

    # TODO There is a lot to fix here in order to align with the other classes...
    #
    # This should only contain the logging information and the name of the StateStore to use
    #
    # TODO We need to be able to locate InfrastructureAccounts (collection of manifest files) and Projects which can be hosted locally in a directory or on Git. Consider how to authenticate to Git... Technically it could also just point to URLS

    def __init__(self, raw_global_configuration: str=DEFAULT_GLOBAL_CONFIG, logger=GenericLogger()) -> None:
        self.raw_global_configuration = raw_global_configuration
        self.parsed_configuration = dict()
        self.logger = logger
        self.state_store = StateStore(logger=self.logger)
        self.system_configurations = SystemConfigurations()
        self.projects = None

    def add_infrastructure_account(self, infrastructure_account: InfrastructureAccount):
        self.system_configurations.add_configuration(item=infrastructure_account)


class ApplicationState:

    def __init__(self, logger=GenericLogger()) -> None:
        self.environment = 'default'
        self.project = 'default'
        self.config_directory = DEFAULT_CONFIG_DIR
        self.config_file = 'verbacratis.yaml'
        self.state_db_url = DEFAULT_STATE_DB
        self.logger = logger
        self.build_id = hashlib.sha256(str(uuid.uuid1()).encode(('utf-8'))).hexdigest()
        self.application_configuration = ApplicationRuntimeConfiguration(raw_global_configuration=DEFAULT_GLOBAL_CONFIG, logger=self.logger)
        self.system_manifest_locations = list()

    def _read_global_configuration_file_content(self):
        self.application_configuration = ApplicationRuntimeConfiguration(raw_global_configuration=DEFAULT_GLOBAL_CONFIG, logger=self.logger)
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
        init_application_dir(dir=self.config_directory)
        self.config_file = get_file_from_path(input_path=config_file)
        self._read_global_configuration_file_content()

    def load_system_manifests(self):
        for location in self.system_manifest_locations:
            if location.startswith('http'):
                if is_url_a_git_repo(url=location) is True:
                    branch = 'main'
                    relative_start_directory = '/'
                    ssh_private_key_path = None
                    set_no_verify_ssl = False
                    if '%00' in location:
                        for item in urllib.parse.unquote_to_bytes(location).decode('utf-8').split('\x00'):
                            if '=' in item:
                                k, v = item.split('=')
                                if k.lower() == 'branch':
                                    branch = v
                                elif k.lower() == 'relative_start_directory':
                                    relative_start_directory = v
                                elif k.lower() == 'ssh_private_key_path':
                                    ssh_private_key_path = v
                                elif k.lower() == 'set_no_verify_ssl':
                                    if v.lower().startswith('t'):
                                        set_no_verify_ssl = True
                    self.application_configuration.system_configurations = get_yaml_configuration_from_git(
                        git_clone_url=location,
                        system_configurations=self.application_configuration.system_configurations,
                        branch=branch,
                        relative_start_directory=relative_start_directory,
                        ssh_private_key_path=ssh_private_key_path,
                        set_no_verify_ssl=set_no_verify_ssl
                    )
                else:
                    self.application_configuration.system_configurations = get_yaml_configuration_from_url(urls=[location,], system_configurations=self.application_configuration.system_configurations)
            else:
                self.application_configuration.system_configurations = get_system_configuration_from_files(files=[location,], system_configurations=self.application_configuration.system_configurations)
        
        

