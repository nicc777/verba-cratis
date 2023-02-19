"""
    Copyright (c) 2022-2023. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/verbacratis/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

import sys
import json
from verbacratis.utils import get_logger
from verbacratis.utils.cli_arguments import parse_command_line_arguments
from verbacratis.models.runtime_configuration import ApplicationState


def main(cli_args: list=sys.argv[1:], logger=get_logger())->dict:
    result = dict()

    ###
    ### Start the build
    ###
    state: ApplicationState = parse_command_line_arguments(state=ApplicationState(logger=logger), cli_args=cli_args)
    state.load_system_manifests()
    state.load_project_manifests()
    state.logger.info('Started with build ID {}'.format(state.build_id))
    
    ###
    ### Log and return final result
    ###
    logger.info('RESULT: {}'.format(json.dumps(result, indent=4, sort_keys=True, default=str)))
    return result


if __name__ == '__main__':  # pragma: no cover
    main(cli_args=sys.argv[1:], logger=get_logger())
