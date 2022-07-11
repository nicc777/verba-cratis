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


from acfop.utils.cli_arguments import parse_argument


class TestFunctionParseArgument(unittest.TestCase):  # pragma: no cover

    def setUp(self):
        self.overrides = dict()
        self.overrides['config_file'] = 'examples/example_01/example_01.yaml'

    def test_basic_invocation(self):
        with self.assertRaises(SystemExit) as cm:
            parse_argument()
        self.assertEqual(cm.exception.code, 2)


if __name__ == '__main__':
    unittest.main()
