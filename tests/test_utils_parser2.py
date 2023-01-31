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


from verbacratis.utils.parser2 import *


def mock_get_file_contents(file: str)->str: # pragma: no cover
    config = ""
    with open('examples/example_01/example_02.yaml', 'r') as f:
      config = f.read()
    return config


def mock_get_file_contents_throws_exception(file: str)->str:
    raise Exception('File Not Found')


class TestFunctionParseConfigurationFile(unittest.TestCase):    # pragma: no cover

    def test_parse_configuration_file_example1(self):
        configuration = parse_yaml_file(file_path='/path/to/configuration', get_file_contents_function=mock_get_file_contents)
        self.assertIsNotNone(configuration)
        self.assertIsInstance(configuration, dict)
        self.assertTrue(len(configuration) > 0)

    def test_parse_configuration_file_example1_file_not_found(self):
        configuration = dict()
        with self.assertRaises(Exception) as context:
            configuration = parse_yaml_file(file_path='/path/to/configuration', get_file_contents_function=mock_get_file_contents_throws_exception)
        self.assertTrue('Failed to parse configuration' in str(context.exception))
        self.assertEqual(len(configuration), 0)


if __name__ == '__main__':
    unittest.main()
