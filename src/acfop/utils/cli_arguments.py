"""
    Copyright (c) 2022. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/acfop/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""


import sys
import argparse
from acfop.utils import get_logger
from acfop.models.runtime import Variable, VariableStateStore


def parse_command_line_arguments(
    cli_args: list=sys.argv[1:],
    overrides: dict=dict(),
    logger=get_logger(),
    state_store: VariableStateStore=VariableStateStore()
)->VariableStateStore:
    """Helper function to parse command line arguments

    Args:
        cli_args: list of arguments as gathered from the command line
        overrides: dictionary with overrides

    Returns:
        Returns an updated :class:`VariableStateStore` object with all the parsed command line arguments
    """
    logger.debug('overrides={}'.format(overrides))
    logger.debug('cli_args={}'.format(cli_args))
    args = dict()
    args['conf'] = None
    parser = argparse.ArgumentParser(description='Processes and execute an AWS CloudFormation deployment based on the supplied configuration')
    parser.add_argument(
        '-c', '--conf',
        action='store',
        nargs='*',
        dest='config_file',
        metavar='CONFIGURATION_FILE',
        type=str, 
        help='The path and filename of the configuration file. REQUIRED'
    )
    parsed_args, unknown_args = parser.parse_known_args(cli_args)
    logger.debug('parsed_args={}'.format(parsed_args))

    if parsed_args.config_file is not None:
        args['config_file'] = parsed_args.config_file[0]
    logger.debug('args={}'.format(args))

    for k,v in overrides.items():
        args[k] = v

    logger.debug('args={}'.format(args))

    if 'config_file' not in args:
        parser.print_usage()
        sys.exit(2)

    if args['config_file'] is None:
        parser.print_usage()
        sys.exit(2)

    logger.debug('args={}'.format(args))

    for k,v in args.items():
        state_store.add_variable(
            var=Variable(
                id='args:{}'.format(k),
                initial_value=v,
                value_type=str,
                classification='build-variable'
            )
        )

    return state_store

