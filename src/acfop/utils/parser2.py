"""
    Copyright (c) 2022. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/acfop/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

import traceback
from acfop.utils.file_io import get_file_contents
import yaml
try:    # pragma: no cover
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError: # pragma: no cover
    from yaml import Loader, Dumper
from cerberus import Validator
import json
from acfop.utils import get_logger


def parse_configuration_file(file_path: str, get_file_contents_function: object=get_file_contents, logger=get_logger())->dict:
    """Parse a configuration file

    Reads the file content from ``file_path`` and attempts to parse it with the YAML parser

    Args:
        file_path (str): The full path to the configuration file
        get_file_contents_function (object): A function used mainly for unit testing to mock the File IO functions

    Returns:
        dict: The parsed configuration, not validated (any valid YAML will be parsed and returned as a dict)

    """
    configuration = dict()
    current_part = 0
    try:
        file_content = get_file_contents_function(file=file_path)
        # configuration = yaml.load(file_content, Loader=Loader)
        for data in yaml.load_all(file_content, Loader=Loader):
            current_part += 1
            configuration['part_{}'.format(current_part)] = data
        logger.debug('configuration={}'.format(configuration))
    except:
        traceback.print_exc()
        raise Exception('Failed to parse configuration')
    return configuration


