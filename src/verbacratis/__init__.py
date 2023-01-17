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


class ApplicationState:

    def __init__(self) -> None:
        self.environment = 'default'
        self.project = 'default'
        self.config_directory = '{}{}{}'.format(
            str(Path.home()),
            os.sep,
            '.verbacratis'
        )
        self.config_file = 'config'
        self.state_db_url = 'sqlite:///{}{}db1.db'.format(
            self.config_directory,
            os.sep
        )
        self.logger = self.set_custom_logger(logger=get_logger())
        self.cli_args = {
            'config_file': '{}{}{}{}config'.format(
                str(Path.home()),
                os.sep,
                '.verbacratis',
                os.sep
            )
        }
        self.build_id = hashlib.sha256(str(uuid.uuid1()).encode(('utf-8'))).hexdigest()

    def get_db_connection(self):
        return create_engine(url=self.state_db_url)

    def set_custom_logger(self, logger=get_logger()):
        self.logger = logger

    def update_config_file(self, config_file: str):
        self.config_directory = get_directory_from_path(input_path=config_file)
        self.config_file = get_file_from_path(input_path=config_file)
        self.cli_args['config_file'] = config_file
        


