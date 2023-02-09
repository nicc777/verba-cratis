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
        create_tmp_file(tmp_dir=tempfile.gettempdir(), file_name='test', data='')

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

    def test_f_append_content_to_file(self):
        append_content_to_file(file=self.temp_file, content='aaa')
        append_content_to_file(file=self.temp_file, content='bbb')
        content = get_file_contents(file=self.temp_file)
        self.assertIsNotNone(content)
        self.assertTrue('aaa' in content)
        self.assertTrue('bbb' in content)

    def test_f_create_tmp_dir_forced_exception_due_to_permission(self):
        result = create_tmp_dir(sub_dir='../this_must_fail')
        self.assertIsNone(result)
    
    def test_f_create_tmp_file_forced_exception_due_to_permission(self):
        result = create_tmp_file(tmp_dir='../this_must_file', file_name='test', data='it does not matter what we put here...')
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
