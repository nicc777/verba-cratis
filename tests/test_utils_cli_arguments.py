"""
    Copyright (c) 2022. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/verbacratis/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")
print('sys.path={}'.format(sys.path))

import unittest


from verbacratis.utils.cli_arguments import parse_command_line_arguments
from verbacratis.models.runtime import VariableStateStore


class TestFunctionParseCommandLineArguments(unittest.TestCase):  # pragma: no cover

    def setUp(self):
        self.overrides = dict()
        self.overrides['config_file'] = 'examples/example_02/example_02.yaml'
        self.cli_args=[
            '--conf', 'examples/example_01/example_02.yaml',
        ]

    def test_basic_invocation_no_args_fail_with_exit(self):
        with self.assertRaises(SystemExit) as cm:
            parse_command_line_arguments()
        self.assertEqual(cm.exception.code, 2)

    def test_basic_invocation_args_basic(self):
        result = parse_command_line_arguments(cli_args=self.cli_args)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)

    def test_basic_invocation_invalid_overrides_fail_with_exit(self):
        with self.assertRaises(SystemExit) as cm:
            parse_command_line_arguments(overrides={'config_file': None})
        self.assertEqual(cm.exception.code, 2)


if __name__ == '__main__':
    unittest.main()
