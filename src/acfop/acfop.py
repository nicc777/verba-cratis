"""
    Copyright (c) 2022. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/acfop/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

import sys
import json
from acfop.utils import get_logger
from acfop.utils.cli_arguments import parse_command_line_arguments
from acfop import BUILD_ID
from acfop.models.runtime import Variable, VariableStateStore
from acfop.utils.parser import parse_configuration_file


def main(cli_args: list=sys.argv[1:], logger=get_logger())->dict:
    result = dict()

    ###
    ### Start the build
    ###
    # state_store = VariableStateStore()
    # state_store.add_variable(var=Variable(id='build_id', initial_value=BUILD_ID, value_type=str))
    logger.info('Started with build ID {}'.format(BUILD_ID))
    logger.debug('Started in DEBUG mode')
    
    ###
    ### Parse command line arguments (update state_store)
    ###
    #state_store = parse_command_line_arguments(cli_args=cli_args, state_store=state_store, logger=logger)
    
    ###
    ### Read and parse the configuration
    ###
    #configuration_as_dict = parse_configuration_file(file_path=state_store.get_variable_value(id='args:config_file'))

    ###
    ### Prepare the final result
    ###
    #result = dict()
    #result['BuildId'] = state_store.get_variable_value(id='build_id')
    #result['SourceConfigFile'] = state_store.get_variable_value(id='args:config_file')
    #result['RuntimeConfiguration'] = configuration_as_dict

    ###
    ### Log and return final result
    ###
    logger.info('RESULT: {}'.format(json.dumps(result, indent=4, sort_keys=True, default=str)))
    return result


if __name__ == '__main__':  # pragma: no cover
    main(cli_args=sys.argv[1:])
