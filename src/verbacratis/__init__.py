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
import traceback
from sqlalchemy import create_engine
from verbacratis.utils import get_logger


def get_directory_from_path(input_path: str)->str:
    """Returns the directory portion of a path
    
    The function first tests if the path exists. If it does not exist, the assumption is that the path consists of a directory and filename.

    If the path does exist, it will be determined if it is a directory or a normal file. Only the directory portion will be returned.

        Args:
            path: (required) String of a full path (directory and/or filename)

        Returns:
            A STRING with the calculated directory portion of the input path
    """
    p = Path(input_path)
    if p.exists() is True:
        if p.is_dir() is True:
            input_path = '{}{}dummy'.format(
                input_path,
                os.sep
            )
    elements = input_path.split(os.sep)
    if len(elements) > 0:
        elements.pop(0)
    if len(elements) == 1:
        return '/'
    final_path = '{}'.format(os.sep).join(elements[:-1])
    final_path = '{}{}'.format(
        os.sep,
        final_path
    )
    return final_path


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


