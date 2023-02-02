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


from verbacratis.utils.git_integration import *
from verbacratis.utils.file_io import create_tmp_dir, remove_tmp_dir_recursively


class TestAllFunctions(unittest.TestCase):  # pragma: no cover

    def setUp(self):
        self.test_repo_ssh = 'git@github.com:nicc777/verba-cratis-test-infrastructure.git'
        self.test_repo_https = 'https://github.com/nicc777/verba-cratis-test-infrastructure.git'
        self.target_dir = create_tmp_dir(sub_dir=random_word())
        print('Preparing dir: {}'.format(self.target_dir))

    def tearDown(self) -> None:
        print('CLeanup dir: {}'.format(self.target_dir))
        remove_tmp_dir_recursively(dir=self.target_dir)

    def test_random_word(self):
        word = random_word(length=10)
        self.assertIsNotNone(word)
        self.assertIsInstance(word, str)
        self.assertEqual(len(word), 10)

    def test_get_yaml_files_from_ssh_repo(self):
        print('Cloning to {}'.format(self.target_dir))
        files = git_clone_checkout_and_return_list_of_files(git_clone_url=self.test_repo_ssh, target_dir=self.target_dir)
        self.assertIsNotNone(files)
        self.assertIsInstance(files, list)
        self.assertEqual(len(files), 2) 
        found = 0
        for file in files:
            print('> Inspecting file {}'.format(file))
            if 'aws-accounts.yaml' in file or 'linux-test-accounts.yaml' in file:
                found += 1
        self.assertEqual(found, 2)

    def test_f_git_clone_to_local_defaults(self):
        remove_tmp_dir_recursively(dir=self.target_dir)
        dir = git_clone_to_local(git_clone_url=self.test_repo_ssh)
        self.target_dir = dir
        self.assertIsNotNone(dir)
        self.assertIsInstance(dir, str)
        self.assertTrue(len(dir) > 0)



if __name__ == '__main__':
    unittest.main()
