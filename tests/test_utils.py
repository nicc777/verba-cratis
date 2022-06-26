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


from acfop.utils import *

class TestFunctionGetLoggingFileHandler(unittest.TestCase):    # pragma: no cover

    def test_call_get_logging_file_handler_with_defaults(self):
        result = get_logging_file_handler(filename='test.log')
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()
