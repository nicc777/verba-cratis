"""
    Copyright (c) 2022. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/acfop/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")
print('sys.path={}'.format(sys.path))

import unittest


from acfop.utils.parser import *


def mock_get_file_contents(file: str)->str: # pragma: no cover
    config = ""
    with open('examples/example_01/example_01.yaml', 'r') as f:
      config = f.read()
    return config


def mock_get_file_contents_throws_exception(file: str)->str:
    raise Exception('File Not Found')


class TestFunctionVariableSnippetExtract(unittest.TestCase):    # pragma: no cover

    def test_string_with_no_variables(self):
        line = 'hello world!'
        result = variable_snippet_extract(line=line)
        self.assertTrue(len(result) == 0)

    def test_string_with_one_variable(self):
        line = 'XXX ${var:var1} XXX'
        result = variable_snippet_extract(line=line)
        self.assertTrue(len(result) == 1)
        self.assertEqual('var:var1', result[0])

    def test_string_with_two_variables(self):
        line = 'XXX ${var:var1} XXX ${func:print_s()} XXX'
        result = variable_snippet_extract(line=line)
        self.assertTrue(len(result) == 2)
        self.assertEqual('var:var1', result[0])
        self.assertEqual('func:print_s()', result[1])

    def test_string_with_two_variables_including_nested_variable(self):
        """
            NOTE: Even in the case of nested variables, still only the first level variables are extracted.
        """
        line = 'XXX ${var:var1} XXX ${func:print_s(message="${var:var1}")} XXX'
        result = variable_snippet_extract(line=line)
        self.assertTrue(len(result) == 2)
        self.assertEqual('var:var1', result[0])
        self.assertEqual('func:print_s(message="${var:var1}")', result[1])
        result2 = variable_snippet_extract(line=result[1])
        self.assertTrue(len(result2) == 1)
        self.assertEqual('var:var1', result2[0])


class TestFunctionParseConfigurationFile(unittest.TestCase):    # pragma: no cover

    def test_parse_configuration_file_example1(self):
        configuration = parse_configuration_file(file_path='/path/to/configuration', get_file_contents_function=mock_get_file_contents)
        self.assertIsNotNone(configuration)
        self.assertIsInstance(configuration, dict)
        self.assertTrue(len(configuration) > 0)
        keys = (
            'deployments',
            'functionParameterValues',
            'globalVariables',
            'logging',
            'tasks',
        )
        for key in keys:
            self.assertTrue(key in configuration, 'Key "{}" not found in configuration'.format(key))

    def test_parse_configuration_file_example1_file_not_found(self):
        configuration = dict()
        with self.assertRaises(Exception) as context:
            configuration = parse_configuration_file(file_path='/path/to/configuration', get_file_contents_function=mock_get_file_contents_throws_exception)
        self.assertTrue('Failed to parse configuration' in str(context.exception))
        self.assertEqual(len(configuration), 0)


class TestFunctionValidateConfiguration(unittest.TestCase):    # pragma: no cover

    def test_validate_example1(self):
        configuration = parse_configuration_file(file_path='/path/to/configuration', get_file_contents_function=mock_get_file_contents)
        result = validate_configuration(configuration=configuration)
        self.assertIsInstance(result, bool)
        self.assertTrue(result)

    def test_failed_validation(self):
        configuration = {'Message': 'This config is invalid'}
        result = validate_configuration(configuration=configuration)
        self.assertIsInstance(result, bool)
        self.assertFalse(result)

    def test_force_exception_with_failed_validation_result(self):
        configuration = 123
        result = validate_configuration(configuration=configuration)
        self.assertIsInstance(result, bool)
        self.assertFalse(result)

    def test_force_deployment_schema_validation_failure(self):
        configuration = parse_configuration_file(file_path='/path/to/configuration', get_file_contents_function=mock_get_file_contents)
        configuration['deployments'][0] = {
            'name': 'this_name_is_valid',
            'incorrectParameter': 123,
        }
        result = validate_configuration(configuration=configuration)
        self.assertIsInstance(result, bool)
        self.assertFalse(result)

    def test_force_deployment_task_name_failure(self):
        configuration = parse_configuration_file(file_path='/path/to/configuration', get_file_contents_function=mock_get_file_contents)
        configuration['deployments'][0]['tasks'] = [
            "lambdaFunction",
            "nonExistingTask"
        ]
        result = validate_configuration(configuration=configuration)
        self.assertIsInstance(result, bool)
        self.assertFalse(result)

    def test_force_fail_function_parameter_values(self):
        configuration = parse_configuration_file(file_path='/path/to/configuration', get_file_contents_function=mock_get_file_contents)
        configuration['functionParameterValues'] = [dict(),]
        result = validate_configuration(configuration=configuration)
        self.assertIsInstance(result, bool)
        self.assertFalse(result)


class TestFunctionFromConfigurationGetAllTaskNamesAsList(unittest.TestCase):    # pragma: no cover

    def test_validate_example1(self):
        configuration = parse_configuration_file(file_path='/path/to/configuration', get_file_contents_function=mock_get_file_contents)
        task_names = from_configuration_get_all_task_names_as_list(configuration=configuration)
        self.assertIsInstance(task_names, list)
        self.assertTrue(len(task_names), 2)
        self.assertTrue('dynamoDbTable' in task_names)
        self.assertTrue('lambdaFunction' in task_names)

    def test_force_Exception(self):
        task_names = from_configuration_get_all_task_names_as_list(configuration=123)
        self.assertIsInstance(task_names, list)
        self.assertEqual(len(task_names), 0)


if __name__ == '__main__':
    unittest.main()
