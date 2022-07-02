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


from acfop.functions import user_function_factory


class TestFunctionUserFunctionFactory(unittest.TestCase):    # pragma: no cover

    def test_call_user_function_factory_defaults(self):
        result = user_function_factory()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertTrue('get_aws_identity' in result)


if __name__ == '__main__':
    unittest.main()
