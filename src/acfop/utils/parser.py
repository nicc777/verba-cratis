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


CONFIGURATION_SCHEMA = {
    'deployments': {
        'required': True,
        'type': 'list'
    },
    'functionParameterValues': {
        'required': False,
        'type': 'list'
    },
    'globalVariables': {
        'required': False,
        'type': 'dict'
    },
    'logging': {
        'required': False,
        'type': 'dict'
    },
    'tasks': {
        'required': True,
        'type': 'list'
    },
}

DEPLOYMENT_SCHEMA = {
    'name': {
        'required': True,
        'type': 'string',
    },
    'unitTestProfile': {
        'required': False,
        'type': 'boolean',
    },
    'tasks': {
        'required': True,
        'type': 'list',
        'minlength': 1,

    },
    'globalVariableOverrides': {
        'required': False,
        'type': 'dict',
    },
    'templateParametersOverrides': {
        'required': False,
        'type': 'dict',
    },
    'dependsOnProfile': {
        'required': False,
        'type': 'list',
    },
    'preDeploymentScript': {
        'required': False,
        'type': 'string',
    },
    'postDeploymentScript': {
        'required': False,
        'type': 'string',
    },
    'deployFromS3': {
        'required': False,
        'type': 'dict',
    },
}

FUNCTION_DEFINITION_SCHEMA = {
    'name': {
        'required': True,
        'type': 'string',
    },
    'parameters': {
        'required': True,
        'type': 'list',
    },
}

FUNCTION_PARAMETERS_SCHEMA = {
    'name': {
        'required': True,
        'type': 'string',
    },
    'type': {
        'required': True,
        'type': 'string',
        'regex': '^bool|str|int|float$',
    },
    'value': {
        'required': True,
        'type': 'string',
    },
}

LOGGING_SCHEMA = {
    'filename': {
        'required': False,
        'type': 'string',
    },
    'level': {
        'required': False,
        'type': 'string',
        'regex': '^warn|info|error|debug$',
    },
    'format': {
        'required': False,
        'type': 'string',
    },
    'handlers': {
        'required': True,
        'type': 'list',
    },
}

LOGGING_HANDLER_SCHEMA = {
    'name': {
        'required': True,
        'type': 'string',
        'regex': '^StreamHandler|FileHandler|TimedRotatingFileHandler|DatagramHandler|SysLogHandler&',
    },
    'parameters': {
        'required': False,
        'type': 'list',
    }
}

TASKS_SCHEMA = {
    'name': {
        'required': True,
        'type': 'string'
    },
    'template': {
        'required': False,                  # DEFAULT: Empty dictionary. If no template is supplied, only the preDeploymentScript and postDeploymentScript are run, otherwise the order is preDeploymentScript, cloudformation deployment and then postDeploymentScript
        'type': 'dict'
    },
    'functionParameterValuesOverrides': {   # DEFAULT: Empty list()
        'required': False,
        'type': 'list'
    },
    'templateParameters': {                 # DEFAULT: Empty list()
        'required': False,
        'type': 'list'
    },
    'changeSetIfExists': {                  # DEFAULT: False (skip) and only a warning message will be produced in the log
        'required': False,
        'type': 'boolean'
    },
    'preDeploymentScript': {                # DEFAULT: None
        'required': False,
        'type': 'string'
    },
    'postDeploymentScript': {               # DEFAULT: None
        'required': False,
        'type': 'string'
    },
    'taskDependsOn': {                      # DEFAULT: Empty list()
        'required': False,
        'type': 'list'
    },
    'taskExports': {                        # DEFAULT: Empty list()
        'required': False,
        'type': 'list'
    },
    'extraBucketArtifacts': {               # DEFAULT: Empty list()
        'required': False,
        'type': 'list'
    },
}

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
            if c == '$' and i < line_len-2:
                if line[i+1] == '{':
                    snippet_started = True
                    i = i+2 # Skip the next character
                else:
                    i = i+1
            else:
                i = i+1
        else:
            if line[i] == '$' and i < line_len-2:
                if line[i+1] == '{':
                    close_bracket_skip_count += 1
                    current_snippet = '{}{}'.format(current_snippet, c)
            elif c == '}' and close_bracket_skip_count == 0:
                snippet_started = False
                snippets.append(current_snippet)
                current_snippet = ""
                # current_snippet = '{}{}'.format(current_snippet, c)
            elif c == '}' and close_bracket_skip_count > 0:
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
        configuration = yaml.load(file_content, Loader=Loader)
    except:
        traceback.print_exc()
        raise Exception('Failed to parse configuration')
    return configuration


def from_configuration_get_all_task_names_as_list(configuration: dict)->list:
    task_names = list()
    try:
        for task in configuration['tasks']:
            task_names.append(task['name'])
    except:
        traceback.print_exc()
    return task_names


def validate_configuration(
    configuration: dict, 
    validation_configuration: dict={
        'CONFIGURATION_SCHEMA': CONFIGURATION_SCHEMA,
        'DEPLOYMENT_SCHEMA': DEPLOYMENT_SCHEMA,
        'FUNCTION_DEFINITION_SCHEMA': FUNCTION_DEFINITION_SCHEMA,
        'FUNCTION_PARAMETERS_SCHEMA': FUNCTION_PARAMETERS_SCHEMA,
        'LOGGING_SCHEMA': LOGGING_SCHEMA,
        'LOGGING_HANDLER_SCHEMA': LOGGING_HANDLER_SCHEMA,
        'TASKS_SCHEMA': TASKS_SCHEMA,
    }
)->bool:
    try:
        v = Validator()
        validation_result = v.validate(configuration, validation_configuration['CONFIGURATION_SCHEMA'])
        if validation_result is False:
            print('Configuration Validation Errors: {}'.format(json.dumps(v.errors, default=str)))
            return False
        task_names = from_configuration_get_all_task_names_as_list(configuration=configuration)
        for deployment in configuration['deployments']:
            validation_result = v.validate(deployment, validation_configuration['DEPLOYMENT_SCHEMA'])
            if validation_result is False:
                print('Deployment Configuration Validation Errors: {}'.format(json.dumps(v.errors, default=str)))
                return False
            for deployment_task_name in deployment['tasks']:
                if deployment_task_name not in task_names:
                    print('ERROR: Task name "{}" in deployment "{}" was not found in task definition'.format(deployment_task_name, deployment['name']))
                    return False
        if 'functionParameterValues' in configuration:
            for function_parameter in configuration['functionParameterValues']:
                validation_result = v.validate(function_parameter, validation_configuration['FUNCTION_DEFINITION_SCHEMA'])
                if validation_result is False:
                    print('Deployment Configuration Validation Errors: {}'.format(json.dumps(v.errors, default=str)))
                    return False
                for param in function_parameter['parameters']:
                    sub_validation_result = v.validate(param, validation_configuration['FUNCTION_PARAMETERS_SCHEMA'])
                    if sub_validation_result is False:
                        print('Deployment Configuration Validation Errors: {}'.format(json.dumps(v.errors, default=str)))
                        return False
        if 'logging' in configuration:
            validation_result = v.validate(configuration['logging'], validation_configuration['LOGGING_SCHEMA'])
            if validation_result is False:
                print('Configuration Validation Errors: {}'.format(json.dumps(v.errors, default=str)))
                return False
            for handler in configuration['logging']['handlers']:
                sub_validation_result = v.validate(handler, validation_configuration['LOGGING_HANDLER_SCHEMA'])
                if sub_validation_result is False:
                    print('Configuration Validation Errors: {}'.format(json.dumps(v.errors, default=str)))
                    return False
        for task in configuration['tasks']:
            validation_result = v.validate(task, validation_configuration['TASKS_SCHEMA'])
            if validation_result is False:
                print('Configuration Validation Errors: {}'.format(json.dumps(v.errors, default=str)))
                return False
    except:
        traceback.print_exc()
        return False
    return True
