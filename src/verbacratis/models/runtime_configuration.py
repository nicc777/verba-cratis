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
from verbacratis.utils.file_io import get_directory_from_path, get_file_from_path
from verbacratis.models import GenericLogger, DEFAULT_CONFIG_DIR, DEFAULT_GLOBAL_CONFIG, DEFAULT_STATE_DB
from verbacratis.models.systems_configuration import InfrastructureAccounts, InfrastructureAccount


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
        self.infrastructure_accounts = InfrastructureAccounts()
        self.projects = None

    def add_infrastructure_account(self, infrastructure_account: InfrastructureAccount):
        self.infrastructure_accounts.add_infrastructure_account(infrastructure_account=infrastructure_account)


class ApplicationState:

    def __init__(self, logger=GenericLogger()) -> None:
        self.environment = 'default'
        self.project = 'default'
        self.config_directory = DEFAULT_CONFIG_DIR
        self.config_file = 'config'
        self.state_db_url = DEFAULT_STATE_DB
        self.logger = logger
        self.build_id = hashlib.sha256(str(uuid.uuid1()).encode(('utf-8'))).hexdigest()
        self.application_configuration = ApplicationRuntimeConfiguration(raw_global_configuration=DEFAULT_GLOBAL_CONFIG, logger=self.logger)

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
        self.config_file = get_file_from_path(input_path=config_file)
        self._read_global_configuration_file_content()
        
        

