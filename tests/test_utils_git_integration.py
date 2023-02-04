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
from pathlib import Path


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

    def test_f_git_clone_to_local_test_branch(self):
        dir = git_clone_to_local(git_clone_url=self.test_repo_ssh, branch='test-branch', target_dir=self.target_dir)
        self.assertIsNotNone(dir)
        self.assertIsInstance(dir, str)
        self.assertTrue(len(dir) > 0)
        content = ''
        with open('{}{}aws-accounts.yaml'.format(dir, os.sep), 'r') as f:
            content = f.read()
        self.assertTrue('sandbox2' in content)

    def test_f_git_clone_to_local_specify_private_key(self):
        home = str(Path.home())
        default_ssh_private_key = '{}{}.ssh/id_rsa'.format(home, os.sep)
        dir = git_clone_to_local(git_clone_url=self.test_repo_ssh, target_dir=self.target_dir, ssh_private_key_path=default_ssh_private_key)
        self.assertIsNotNone(dir)
        self.assertIsInstance(dir, str)
        self.assertTrue(len(dir) > 0)
        self.assertTrue(os.path.exists('{}{}.git'.format(dir, os.sep)))

    def test_f_git_clone_to_local_specify_https_no_verify(self):
        home = str(Path.home())
        dir = git_clone_to_local(git_clone_url=self.test_repo_https, target_dir=self.target_dir, set_no_verify_ssl=True)
        self.assertIsNotNone(dir)
        self.assertIsInstance(dir, str)
        self.assertTrue(len(dir) > 0)
        self.assertTrue(os.path.exists('{}{}.git'.format(dir, os.sep)))

    def test_f_git_clone_checkout_and_return_list_of_files_test_branch_get_file_from_specific_directory(self):
        files = git_clone_checkout_and_return_list_of_files(git_clone_url=self.test_repo_ssh, branch='test-branch', target_dir=self.target_dir, relative_start_directory='/experiment')
        self.assertIsNotNone(files)
        self.assertIsInstance(files, list)
        self.assertEqual(len(files), 1)
        found = 0
        for file in files:
            print('> Inspecting file {}'.format(file))
            if 'aws-accounts-new.yaml' in file or 'linux-test-accounts.yaml' in file:
                found += 1
        self.assertEqual(found, 1)

    def test_f_git_clone_checkout_and_return_list_of_files_test_branch_get_file_from_specific_directory_2(self):
        files = git_clone_checkout_and_return_list_of_files(git_clone_url=self.test_repo_ssh, branch='test-branch', target_dir=self.target_dir, relative_start_directory='experiment')
        self.assertIsNotNone(files)
        self.assertIsInstance(files, list)
        self.assertEqual(len(files), 1)
        found = 0
        for file in files:
            print('> Inspecting file {}'.format(file))
            if 'aws-accounts-new.yaml' in file or 'linux-test-accounts.yaml' in file:
                found += 1
        self.assertEqual(found, 1)

    def test_f_is_url_a_git_repo_valid_url_https(self):
        self.assertTrue(is_url_a_git_repo(url=self.test_repo_https))

    def test_f_is_url_a_git_repo_valid_url_ssh(self):
        self.assertTrue(is_url_a_git_repo(url=self.test_repo_ssh))

    def test_f_is_url_a_git_repo_invalid_url_https(self):
        self.assertFalse(is_url_a_git_repo(url='https://www.google.com'))

    def test_f_is_url_a_git_repo_invalid_url_ssh(self):
        self.assertFalse(is_url_a_git_repo(url='git@github.com:nopenopenope'))


if __name__ == '__main__':
    unittest.main()
