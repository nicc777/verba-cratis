"""
    Copyright (c) 2022-2023. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/verbacratis/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""


# TODO this file is no longer required. remove together with unit tests


from verbacratis.utils import get_logger
from verbacratis.utils.os_integration import file_exists
from verbacratis.models.runtime import Variable, VariableStateStore


def update_state_store_from_config_file(state_store: VariableStateStore, logger=get_logger())->VariableStateStore:
    config_file = state_store.get_variable_value(id='args:config_file', skip_embedded_variable_processing=True)
    if file_exists(file_path=config_file, logger=logger):
        pass
    else:
        raise Exception('Config file not found')
    return state_store

