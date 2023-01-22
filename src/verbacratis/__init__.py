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
""".format(DEFAULT_STATE_DB)


class Project:

    def __init__(self, name: str):
        self.name = name
        self.environments = list()
        self.manifest_directories = list()
        self.manifest_files = list()
        self.include_file_regex = ('*\.yml', '*\.yaml')
        self.parent_project_names = list()

    def add_environment(self, environment_name: str):
        self.environments.append(environment_name)

    def add_parent_project(self, environment_name: str, parent_project_name: str):
        if environment_name not in self.parent_project_names:
            self.parent_project_names[environment_name] = list()
        self.parent_project_names.append(parent_project_name)

    def add_manifest_directory(self, directory: str):
        self.manifest_directories.append(directory)

    def override_include_file_regex(self, include_file_regex: tuple):
        self.include_file_regex = include_file_regex

    def add_manifest_file(self, file: str):
        self.manifest_files.append(file)


def _get_parent_projects(environment_name: str, projects: dict, project: Project, ordered_project_names: list=list())->list:
    current_project_index_position = ordered_project_names.index(project.name)
    for parent_project_name in project.environment_specific_parent_project_names[environment_name]:
        ordered_project_names.insert(current_project_index_position, parent_project_name)
        current_project_index_position = ordered_project_names.index(project.name)
        if parent_project_name in projects:
            ordered_project_names = _get_parent_projects(
                environment_name=environment_name,
                projects=projects,
                project=projects[parent_project_name],
                ordered_project_names=copy.deepcopy(ordered_project_names)
            )
    return ordered_project_names


class Projects:

    def __init__(self):
        self.projects = dict()
        self.projects_per_environment = dict()

    def add_project(self, project: Project):
        if project.name not in self.projects:
            self.projects[project.name] = project
            environments = project.environments
            if len(environments) == 0:
                environments = ['default', ]
            for env in environments:
                if env not in self.projects_per_environment:
                    self.projects_per_environment[env] = list()
                self.projects_per_environment[env].append(project.name)
        else:
            raise Exception('Project "{}" Already Defined'.format(project.name))

    def get_ordered_projects_for_environment(self, environment_name: str)->list:
        ordered_project_names = list()
        if environment_name in self.projects_per_environment:
            copied_project_classes_per_environment = dict()
            for project_name in self.projects_per_environment[environment_name]:
                ordered_project_names.append(project_name)
                copied_project_classes_per_environment[project_name] = self.projects[project_name]
            for project_name in copy.deepcopy(ordered_project_names):
                ordered_project_names = _get_parent_projects(
                    environment_name=environment_name,
                    projects=copied_project_classes_per_environment,
                    project=self.projects[project_name],
                    ordered_project_names=ordered_project_names
                )
        return ordered_project_names


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
        

