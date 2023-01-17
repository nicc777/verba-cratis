"""
    Copyright (c) 2022. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/verbacratis/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

import traceback
import sys
import argparse
from verbacratis import ApplicationState


def _get_arg_parser(
    default_config_file: str,
    default_environment: str,
    default_project: str
)->argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Processes and execute an AWS CloudFormation deployment based on the supplied configuration')
    parser.add_argument(
        '-c', '--conf',
        action='store',
        nargs='*',
        dest='config_file',
        metavar='CONFIGURATION_FILE',
        type=str, 
        default=default_config_file,
        help='The path and filename of the configuration file. REQUIRED'
    )
    parser.add_argument(
        '-e', '--env',
        action='store',
        nargs='*',
        dest='environment',
        metavar='ENVIRONMENT_NAME',
        type=str, 
        default=default_environment,
        help='The environment name (used to identify tasks and deployments from all manifest files)'
    )
    parser.add_argument(
        '-p', '--project',
        action='store',
        nargs='*',
        dest='project',
        metavar='PROJECT_NAME',
        type=str, 
        default=default_project,
        help='The project name (used in reporting only)'
    )
    return parser


def parse_command_line_arguments(
    state:ApplicationState,
    cli_args: list=sys.argv[1:],
    overrides: dict=dict(),
)->ApplicationState:
    """Helper function to parse command line arguments

    Args:
        cli_args: list of arguments as gathered from the command line
        overrides: dictionary with overrides

    Returns:
        Returns an updated :class:`VariableStateStore` object with all the parsed command line arguments
    """
    state.logger.info('overrides={}'.format(overrides))
    state.logger.info('cli_args={}'.format(cli_args))
    args = dict()
    args['conf'] = None
    parser = _get_arg_parser(
        default_config_file=state.cli_args['config_file'],
        default_environment=state.environment,
        default_project=state.project
    )
    parsed_args, unknown_args = parser.parse_known_args(cli_args)

    if parsed_args.config_file is not None:
        args['config_file'] = parsed_args.config_file[0]

    if parsed_args.environment is not None:
        state.environment =  parsed_args.environment[0]

    if parsed_args.project is not None:
        state.environment =  parsed_args.project[0]

    for k,v in overrides.items():
        args[k] = v

    if 'config_file' not in args:
        parser.print_usage()
        sys.exit(2)

    if args['config_file'] is None:
        parser.print_usage()
        sys.exit(2)

    state.logger.info('args={}'.format(args))
    try:
        state.update_config_file(config_file=args['config_file'])
    except:
        state.logger.error('EXCEPTION: {}'.format(traceback.format_exc()))
        parser.print_usage()
        sys.exit(2)

    return state

