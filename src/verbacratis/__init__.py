"""
    Copyright (c) 2022. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/verbacratis/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

import hashlib
import uuid
from pathlib import Path
import os
from sqlalchemy import create_engine
from verbacratis.utils import get_logger
from verbacratis.utils.file_io import get_directory_from_path, get_file_from_path


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


class ApplicationState:

    def __init__(self) -> None:
        self.environment = 'default'
        self.project = 'default'
        self.config_directory = DEFAULT_CONFIG_DIR
        self.config_file = 'config'
        self.state_db_url = DEFAULT_STATE_DB
        self.logger = self.set_custom_logger(logger=get_logger())
        self.build_id = hashlib.sha256(str(uuid.uuid1()).encode(('utf-8'))).hexdigest()
        self.raw_global_configuration = DEFAULT_GLOBAL_CONFIG

    def get_db_connection(self):
        return create_engine(url=self.state_db_url)

    def set_custom_logger(self, logger=get_logger()):
        self.logger = logger

    def _read_global_configuration_file_content(self):
        self.raw_global_configuration = DEFAULT_GLOBAL_CONFIG
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
            self.raw_global_configuration = f.read()
        

    def update_config_file(self, config_file: str):
        self.config_directory = get_directory_from_path(input_path=config_file)
        self.config_file = get_file_from_path(input_path=config_file)
        self._read_global_configuration_file_content()    

