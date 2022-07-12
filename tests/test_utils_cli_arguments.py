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


from acfop.utils.cli_arguments import parse_command_line_arguments
from acfop.models.runtime import VariableStateStore


class TestFunctionParseCommandLineArguments(unittest.TestCase):  # pragma: no cover

    def setUp(self):
        self.overrides = dict()
        self.overrides['config_file'] = 'examples/example_02/example_02.yaml'
        self.cli_args=[
            '--conf', 'examples/example_01/example_01.yaml',
        ]

    def test_basic_invocation_no_args_fail_with_exit(self):
        with self.assertRaises(SystemExit) as cm:
            parse_command_line_arguments()
        self.assertEqual(cm.exception.code, 2)

    def test_basic_invocation_args_basic(self):
        result = parse_command_line_arguments(cli_args=self.cli_args)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, VariableStateStore)
        value = result.get_variable_value(id='args:config_file', skip_embedded_variable_processing=True)
        self.assertIsNotNone(value)
        self.assertIsInstance(value, str)
        self.assertTrue(len(value) > 0)
        self.assertTrue('example_01' in value)

    def test_basic_invocation_args_overrides_only(self):
        result = parse_command_line_arguments(overrides=self.overrides)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, VariableStateStore)
        value = result.get_variable_value(id='args:config_file', skip_embedded_variable_processing=True)
        self.assertIsNotNone(value)
        self.assertIsInstance(value, str)
        self.assertTrue(len(value) > 0)
        self.assertTrue('example_02' in value)

    def test_basic_invocation_args_cli_provided_and_overrides(self):
        result = parse_command_line_arguments(cli_args=self.cli_args, overrides=self.overrides)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, VariableStateStore)
        value = result.get_variable_value(id='args:config_file', skip_embedded_variable_processing=True)
        self.assertIsNotNone(value)
        self.assertIsInstance(value, str)
        self.assertTrue(len(value) > 0)
        self.assertTrue('example_02' in value)

    def test_basic_invocation_invalid_overrides_fail_with_exit(self):
        with self.assertRaises(SystemExit) as cm:
            parse_command_line_arguments(overrides={'config_file': None})
        self.assertEqual(cm.exception.code, 2)


if __name__ == '__main__':
    unittest.main()
