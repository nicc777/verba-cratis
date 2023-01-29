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
import tempfile


from verbacratis.utils.file_io import *


class TestAllFunctions(unittest.TestCase):  # pragma: no cover

    def setUp(self):
        self.temp_file = '{}{}test'.format(tempfile.gettempdir(), os.sep)

    def test_all_in_one_file_io(self):
        content1 = "aaa"
        self.assertIsNone(write_content_to_file(file=self.temp_file, content=content1))
        content2 = ""
        content2 = get_file_contents(file=self.temp_file)
        self.assertEqual(content1, content2)
        content3 = '{}{}'.format(content1, content2)
        self.assertIsNone(append_content_to_file(file=self.temp_file, content=content2))
        content4 = ""
        content4 = get_file_contents(file=self.temp_file)
        self.assertEqual(content4, content3)


if __name__ == '__main__':
    unittest.main()
