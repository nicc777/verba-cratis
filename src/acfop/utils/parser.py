"""
    Copyright (c) 2022. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/acfop/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

import traceback
from acfop.utils.file_io import get_file_contents


def variable_snippet_extract(line: str)->list:
    """Extracts the variables embedded in a string and return as a list

    Each line in the configuration file could contain one or more variable strings that need further processing in 
    order to replace that variable with the processed value.

    An example (snippet) from one of the example configurations are listed below:

    .. code-block:: yaml

        globalVariables:
            awsRegion: eu-central-1
            awsAccountId: ${env:AWS_REGION}
            cloudFormationS3Bucket: test-deployments-${func:get_username()}-${func:get_aws_account_id()} 

    In the above example, the ``awsAccountId`` string that will be parsed is ``${env:AWS_REGION}`` and will return:
    ``['env:AWS_REGION']``

    In the above example, the ``cloudFormationS3Bucket`` string that will be parsed is 
    ``test-deployments-${func:get_username()}-${func:get_aws_account_id()}`` and will return:
    ``['func:get_username()', 'func:get_aws_account_id()']``

    Args:
        line (str): The line to be parsed

    Returns:
        list: All variables extracted from the string

    """
    snippets = list()
    current_snippet = ""
    snippet_started = False
    close_bracket_skip_count = 0
    line_len = len(line)
    i = 0
    while(i < line_len):
        c = line[i]
        if snippet_started is False:
            if line[i] == '$' and i < line_len-2:
                if line[i+1] == '{':
                    snippet_started = True
                    i = i+2 # Skip the next character
            else:
                i = i+1
        else:
            if line[i] == '$' and i < line_len-2:
                if line[i+1] == '{':
                    close_bracket_skip_count += 1
                    current_snippet = '{}{}'.format(current_snippet, c)
            elif line[i] == '}' and close_bracket_skip_count == 0:
                snippet_started = False
                snippets.append(current_snippet)
                current_snippet = ""
            elif line[i] == '}' and close_bracket_skip_count > 0:
                close_bracket_skip_count -= 1
                current_snippet = '{}{}'.format(current_snippet, c)
            else:
                current_snippet = '{}{}'.format(current_snippet, c)
            i = i+1
    return snippets


def parse_configuration_file(file_path: str, get_file_contents_function: object=get_file_contents)->dict:
    """Parse a configuration file

    Reads the file content from ``file_path`` and attempts to parse it with the YAML parser

    Args:
        file_path (str): The full path to the configuration file
        get_file_contents_function (object): A function used mainly for unit testing to mock the File IO functions

    Returns:
        dict: The parsed configuration, not validated (any valid YAML will be parsed and returned as a dict)

    """
    configuration = dict()
    try:
        file_content = get_file_contents_function(file=file_path)
        # TODO Implement python yaml parser
    except:
        traceback.print_exc()
        raise Exception('Failed to parse configuration')
    return configuration
