"""
    Copyright (c) 2022-2023. All rights reserved. NS Coetzee <nicc777@gmail.com>

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
from verbacratis.models import GenericLogger
from verbacratis.models.runtime import VariableStateStore
from verbacratis.models.runtime_configuration import ApplicationState
from verbacratis.utils.file_io import remove_tmp_dir_recursively
from verbacratis.utils.file_io import remove_tmp_dir_recursively, create_tmp_dir
from verbacratis.utils import get_logger


class TestFunctionParseCommandLineArguments(unittest.TestCase):  # pragma: no cover

    def setUp(self):
        self.cli_args_basic=[
            '-s', 'https://github.com/nicc777/verba-cratis-test-infrastructure.git',
            '-p', 'https://github.com/nicc777/verba-cratis-test-projects.git',
            '-e', 'default'
        ]
        self.cli_args_complex=[
            '-s', 'https://github.com/nicc777/verba-cratis-test-infrastructure.git%00branch%3Dtest-branch%00relative_start_directory%3D/experiment%00set_no_verify_ssl%3Dtrue',
            '-p', 'https://github.com/nicc777/verba-cratis-test-projects.git%00branch%3Dmain',
            '-e', 'default'
        ]
        self.cli_args_help=['-h',]
        self.config_dir = create_tmp_dir(sub_dir='TestApplicationState')
        self.cli_args_basic.append('--conf')
        self.cli_args_basic.append('{}{}test_config_file.yaml'.format(self.config_dir, os.sep))
        self.cli_args_complex.append('--conf')
        self.cli_args_complex.append('{}{}test_config_file.yaml'.format(self.config_dir, os.sep))
    
    def tearDown(self):
        if self.config_dir is not None:
            print('CLEANUP: Removing directory recursively: {}'.format(self.config_dir))
            remove_tmp_dir_recursively(dir=self.config_dir)

    def test_basic_invocation_no_args_fail_with_exit(self):
        with self.assertRaises(SystemExit) as cm:
            parse_command_line_arguments(state=ApplicationState())
        self.assertEqual(cm.exception.code, 2)

    def test_basic_invocation_args_basic(self):
        result = parse_command_line_arguments(state=ApplicationState(logger=get_logger()), cli_args=self.cli_args_basic)
        self.config_dir = result.config_directory
        self.assertIsNotNone(result)
        self.assertIsInstance(result, ApplicationState)
        self.assertIsNotNone(result.logger)
        self.assertIsInstance(result.logger, GenericLogger)
        self.assertIsNotNone(result.logger.logger)

    def test_basic_invocation_invalid_overrides_fail_with_exit(self):
        with self.assertRaises(SystemExit) as cm:
            parse_command_line_arguments(state=ApplicationState(logger=get_logger()), overrides={'config_file': None})
        self.assertEqual(cm.exception.code, 2)

    def test_basic_invocation_help(self):
        with self.assertRaises(SystemExit) as cm:
            parse_command_line_arguments(state=ApplicationState(logger=get_logger()), cli_args=self.cli_args_help)
        self.assertEqual(cm.exception.code, 2)

    def test_basic_invocation_args_complex_git_location(self):
        result = parse_command_line_arguments(state=ApplicationState(logger=get_logger()), cli_args=self.cli_args_complex)
        result.load_system_manifests()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, ApplicationState)
        infrastructure_accounts = result.application_configuration.system_configurations.get_infrastructure_account_auth_config(infrastructure_account_name='sandbox-account3')
        self.assertIsNotNone(infrastructure_accounts)
        self.assertIsInstance(infrastructure_accounts, list)
        self.assertEqual(len(infrastructure_accounts), 1)


if __name__ == '__main__':
    unittest.main()
