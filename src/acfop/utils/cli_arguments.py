"""
    Copyright (c) 2022. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/acfop/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""


import argparse


def parse_argument():
    parser = argparse.ArgumentParser(description='Processes and execute an AWS CloudFormation deployment based on the supplied configuration')
    parser.add_argument(
        '-c', '--conf',
        action='store',
        nargs=1,
        required=True,
        dest='config_file',
        metavar='CONFIGURATION_FILE',
        type=str, 
        help='The path and filename of the configuration file. REQUIRED'
    )
    return parser.parse_args()

