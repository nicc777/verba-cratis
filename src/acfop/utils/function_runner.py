"""
    Copyright (c) 2022. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/acfop/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""


import traceback
import ast
from acfop.utils import get_logger


def _get_function_parameters(
    function_name: str,
    function_fixed_parameters: dict=dict(),
    template_parameters: dict=dict(), 
    registered_functions: dict=dict(),
    logger=get_logger()
)->dict:
        parameters = dict()
        logger.debug('function_fixed_parameters={}'.format(function_fixed_parameters))
        function_default_parameters = registered_functions[function_name]['fixed_parameters']
        logger.debug('function_default_parameters={}'.format(function_default_parameters))
        for k, v in function_default_parameters.items():
            parameters[k] = v
        for k, v in function_fixed_parameters.items():
            parameters[k] = v
        for k, v in template_parameters.items():
            parameters[k] = v
        return parameters


def _extract_function_parameters(value: str, logger=get_logger())->dict:
        parameters = dict()
        try:
            value = value.strip()
            value = value.partition('(')[2].rpartition(')')[0]  # 'include_account_if_available="hh", blabla=True, something="1,2"'
            logger.debug('value={}'.format(value))
            args = 'f({})'.format(value)
            tree = ast.parse(args)
            funccall = tree.body[0].value
            args = [ast.literal_eval(arg) for arg in funccall.args]
            kwargs = {arg.arg: ast.literal_eval(arg.value) for arg in funccall.keywords}
            parameters = kwargs # For now, we only support kwargs... 
        except:
            logger.error('EXCEPTION: {}'.format(traceback.format_exc()))
        logger.debug('parameters={}'.format(parameters))
        return parameters


def execute_function(
    function_template: str,                     # Comes from Variable.value
    function_fixed_parameters: dict=dict(),
    logger=get_logger(),
    registered_functions: dict=dict()
):
    function_exec_result = ''
    if '(' in function_template:
        function_name = function_template.split('(')[0]
        if ':' in function_name:
            function_name = function_name.split(':')[1]
        logger.debug('function_name={}'.format(function_name))
        if function_name not in registered_functions:
            raise Exception('Function "{}" is not a recognized function.'.format(function_name))
        parameters = _get_function_parameters(
            function_name=function_name,
            function_fixed_parameters=function_fixed_parameters,
            template_parameters=_extract_function_parameters(value=function_template),
            registered_functions=registered_functions
        )
        logger.debug('parameters={}'.format(parameters))
        try:
            function_exec_result = registered_functions[function_name]['f'](**parameters)
            logger.debug('EXEC RESULT :: function_exec_result={}'.format(function_exec_result))
        except:
            logger.error('EXCEPTION: {}'.format(traceback.format_exc()))
    else:
        raise Exception('Value does not appear to contain a function call')
    logger.debug('function_exec_result={}'.format(function_exec_result))
    return function_exec_result

