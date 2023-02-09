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


from verbacratis.verbacratis import main
from verbacratis.utils import *


class TestFunctionMain(unittest.TestCase):    # pragma: no cover

    def test_call_main_defaults(self):
        result = main(
            cli_args=[
                '--system', 'https://github.com/nicc777/verba-cratis-test-infrastructure.git',
                '-p', 'https://github.com/nicc777/verba-cratis-test-projects.git'
            ]
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)


if __name__ == '__main__':
    unittest.main()
