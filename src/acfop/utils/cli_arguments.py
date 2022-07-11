"""
    Copyright (c) 2022. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/acfop/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""


import sys
import argparse
from acfop.utils import get_logger


def parse_argument(overrides: dict=dict(), logger=get_logger())->dict:
    logger.debug('overrides={}'.format(overrides))
    args = dict()
    args['conf'] = None
    parser = argparse.ArgumentParser(description='Processes and execute an AWS CloudFormation deployment based on the supplied configuration')
    parser.add_argument(
        '-c', '--conf',
        action='store',
        nargs=1,
        dest='config_file',
        metavar='CONFIGURATION_FILE',
        type=str, 
        help='The path and filename of the configuration file. REQUIRED'
    )
    parsed_args = parser.parse_args()
    logger.debug('parsed_args={}'.format(parsed_args))

    if parsed_args.config_file is not None:
        args['conf'] = parsed_args.config_file[0]
    logger.debug('args={}'.format(args))

    for k,v in overrides.items():
        args[k] = v

    if args['conf'] is None:
        parser.print_usage()
        sys.exit(1)

    logger.debug('args={}'.format(args))
    return args

