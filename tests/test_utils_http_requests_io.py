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


from verbacratis.utils.http_requests_io import *
from verbacratis.utils.file_io import create_tmp_dir, create_tmp_file, remove_tmp_dir_recursively


class TestAllFunctions(unittest.TestCase):  # pragma: no cover

    def setUp(self):
        self.temp_dir = create_tmp_dir(sub_dir='unit_testing')
        print('Created {}'.format(self.temp_dir))
        self.urls_main_branch = [
            'https://raw.githubusercontent.com/nicc777/verba-cratis-test-infrastructure/main/aws-accounts.yaml',
            'https://raw.githubusercontent.com/nicc777/verba-cratis-test-infrastructure/main/linux-test-accounts.yaml'
        ]
        self.urls_test_branch = [
            'https://raw.githubusercontent.com/nicc777/verba-cratis-test-infrastructure/test-branch/aws-accounts.yaml',
            'https://raw.githubusercontent.com/nicc777/verba-cratis-test-infrastructure/test-branch/linux-test-accounts.yaml'
        ]

    def tearDown(self):
        print('Removing {}'.format(self.temp_dir))
        remove_tmp_dir_recursively(dir=self.temp_dir)

    def test_download_files_one_url_from_main_branch(self):
        files = download_files(urls=[self.urls_main_branch[0],], target_dir=self.temp_dir)
        self.assertIsNotNone(files)
        self.assertIsInstance(files, list)
        self.assertEqual(len(files), 1)
        for file in files:
            self.assertTrue(self.temp_dir in file)
            self.assertTrue(len(file) > len(self.temp_dir))

    def test_download_files_all_urls_from_main_branch(self):
        files = download_files(urls=self.urls_main_branch, target_dir=self.temp_dir)
        self.assertIsNotNone(files)
        self.assertIsInstance(files, list)
        self.assertEqual(len(files), 2)
        for file in files:
            self.assertTrue(self.temp_dir in file)
            self.assertTrue(len(file) > len(self.temp_dir))


if __name__ == '__main__':
    unittest.main()
