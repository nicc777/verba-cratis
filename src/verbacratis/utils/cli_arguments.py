"""
    Copyright (c) 2022-2023. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/verbacratis/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

import traceback
import sys
import os
import argparse
from verbacratis.models.runtime_configuration import ApplicationState
from verbacratis.utils.file_io import expand_to_full_path
from verbacratis.models import DEFAULT_CONFIG_DIR


GIT_URL_HELP_TEXT2 = "Please also refer to http://bit.ly/3KkVytn"


def _get_arg_parser(
    logger,
    default_config_file: str,
    default_environment: str='default',
)->argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Processes and execute an AWS CloudFormation deployment based on the supplied configuration')
    parser.add_argument(
        '-c', '--conf',
        action='store',
        nargs='*',
        dest='config_file',
        metavar='PATH',
        type=str, 
        default=default_config_file,
        help='The path and filename of the main application configuration file'
    )
    parser.add_argument(
        '-s', '--system',
        action='append',
        nargs='*',
        dest='system_manifest_locations',
        metavar='LOCATION',
        type=str, 
        required=True,
        help='[REQUIRED] Points to where System Configuration Manifest files can be location. LOCATION is either a file path, a Git repository or a URL to a file on a web server. Repeat the argument to add multiple locations.\n\n{}'.format(GIT_URL_HELP_TEXT2)
    )
    parser.add_argument(
        '-p', '--project',
        action='append',
        nargs='*',
        dest='project_locations',
        metavar='LOCATION',
        type=str, 
        required=True,
        help='[REQUIRED] Points to where Project Manifest files can be location. LOCATION is either a file path, a Git repository or a URL to a file on a web server. Repeat the argument to add multiple locations.\n\n{}'.format(GIT_URL_HELP_TEXT2)
    )
    parser.add_argument(
        '-e', '--env',
        action='store',
        nargs='*',
        dest='environment',
        metavar='ENVIRONMENT_NAME',
        type=str, 
        default=default_environment,
        help='The environment name to target'
    )
    logger.info('Returning CLI Argument Parser')
    return parser


def parse_command_line_arguments(
    state:ApplicationState,
    cli_args: list=sys.argv[1:],
    overrides: dict=dict(),
)->ApplicationState:
    """Helper function to parse command line arguments

    Args:
        state: ApplicationState that will be updated with the supplied command line arguments and overrides
        cli_args: list of arguments as gathered from the command line
        overrides: dictionary with overrides

    Returns:
        Returns an updated :class:`ApplicationState` object with all the parsed command line arguments
    """
    state.logger.info('overrides={}'.format(overrides))
    state.logger.info('cli_args={}'.format(cli_args))
    args = dict()
    args['conf'] = None
    parser = _get_arg_parser(
        logger=state.logger,
        default_config_file='{}{}verbacratis.yaml'.format(DEFAULT_CONFIG_DIR, os.sep),
        default_environment=state.environment
    )
    parsed_args, unknown_args = parser.parse_known_args(cli_args)
    state.logger.info('Command line arguments parsed')

    # Parse config file
    if parsed_args.config_file is not None:
        if isinstance(parsed_args.config_file, list):
            args['config_file'] = expand_to_full_path(original_path=parsed_args.config_file[0])
        else:
            args['config_file'] = expand_to_full_path(original_path=parsed_args.config_file)

    # Add system configuration manifest locations to args['system_manifest_locations']
    args['system_manifest_locations'] = list()
    if parsed_args.system_manifest_locations is not None:
        for location in parsed_args.system_manifest_locations:
            if isinstance(location, list):
                for sub_location in location:
                    if sub_location.startswith('http') is True:
                        args['system_manifest_locations'].append(sub_location)
                    else:
                        args['system_manifest_locations'].append(expand_to_full_path(original_path=sub_location))
            else:   # pragma: no cover
                # TODO Consider removing this logic, as with the current implementation we never seem to reach this part
                if location.startswith('http') is True:
                    args['system_manifest_locations'].append(location)
                else:
                    args['system_manifest_locations'].append(expand_to_full_path(original_path=location))
    if len(args['system_manifest_locations']) == 0:
        state.logger.error('CRITICAL: No system manifest locations specified')
        parser.print_usage()
        sys.exit(2)
    state.system_manifest_locations = args['system_manifest_locations']

    # Add project manifest locations to args['system_manifest_locations']
    args['project_manifest_locations'] = list()
    if parsed_args.project_locations is not None:
        for location in parsed_args.project_locations:
            if isinstance(location, list):
                for sub_location in location:
                    if sub_location.startswith('http') is True:
                        args['project_manifest_locations'].append(sub_location)
                    else:
                        args['project_manifest_locations'].append(expand_to_full_path(original_path=sub_location))
            else:   # pragma: no cover
                # TODO Consider removing this logic, as with the current implementation we never seem to reach this part
                if location.startswith('http') is True:
                    args['project_manifest_locations'].append(location)
                else:
                    args['project_manifest_locations'].append(expand_to_full_path(original_path=location))
    if len(args['project_manifest_locations']) == 0:
        state.logger.error('CRITICAL: No system manifest locations specified')
        parser.print_usage()
        sys.exit(2)
    state.project_manifest_locations = args['project_manifest_locations']

    # Add environment target to state
    if parsed_args.environment is not None:
        state.environment =  parsed_args.environment[0]

    for k,v in overrides.items():
        args[k] = v

    state.logger.info('args={}'.format(args))
    try:
        state.update_config_file(config_file=args['config_file'])
    except: # pragma: no cover
        state.logger.error('EXCEPTION: {}'.format(traceback.format_exc()))
        parser.print_usage()
        sys.exit(2)

    return state

