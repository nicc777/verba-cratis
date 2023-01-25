"""
    Copyright (c) 2022. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/verbacratis/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")
print('sys.path={}'.format(sys.path))

import unittest


from verbacratis.models.runtime_configuration import *
from sqlalchemy.engine import Engine


class TestClassStateStore(unittest.TestCase):    # pragma: no cover

    def test_state_store_init_with_defaults(self):
        result = StateStore()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, StateStore)

    def test_state_store_get_connection_sqlite_memory(self):
        result = StateStore(connection_url='sqlite+pysqlite:///:memory:')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, StateStore)
        result.create_db_engine()
        self.assertTrue(result.enable_state)

    def test_state_store_get_connection_sqlite_invalid_url_disables_state(self):
        result = StateStore(connection_url='not-valid')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, StateStore)
        result.create_db_engine()
        self.assertFalse(result.enable_state)


class TestApplicationConfiguration(unittest.TestCase):    # pragma: no cover

    def test_application_configuration_init_with_defaults(self):
        result = ApplicationConfiguration()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, ApplicationConfiguration)


class TestProject(unittest.TestCase):    # pragma: no cover

    def test_project_init_with_defaults(self):
        result = Project(name='test')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Project)
        self.assertTrue('default' in result.scopes)

    def test_project_init_with_defaults_dump_as_yaml(self):
        result = str(Project(name='test'))
        print('='*80)
        print('# Project YAML')
        print(result)
        print('='*80)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        self.assertTrue('name: test' in result)
        self.assertTrue('environments:' in result)
        self.assertTrue('- name: default' in result)
        self.assertTrue('includeFileRegex:' in result)
        self.assertTrue('- \'*\.yml\'' in result)
        self.assertTrue('- \'*\.yaml\'' in result)
        self.assertTrue(result.startswith('---'))

    def test_project_method_add_parent_project(self):
        project_parent = Project(name='test_parent')
        project_child1 = Project(name='test_child1')
        project_child1.add_parent_project(parent_project_name=project_parent.name)
        self.assertEqual(len(project_parent.parent_item_names), 0)
        self.assertEqual(len(project_child1.parent_item_names), 1)
        self.assertTrue('test_parent' in project_child1.parent_item_names)

    def test_project_method_add_manifest_directory(self):
        project = Project(name='test')
        project.add_manifest_directory(path='/tmp')
        
        self.assertEqual(len(project.manifest_directories), 1)
        
        directory = project.manifest_directories[0]
        self.assertIsInstance(directory, dict)
        self.assertTrue('path' in directory)
        self.assertTrue('type' in directory)
        self.assertEqual('/tmp', directory['path'])
        self.assertEqual('YAML', directory['type'])

        project.add_manifest_directory(path='/something/else', type='ABC')
        self.assertEqual(len(project.manifest_directories), 2)

        directory1 = project.manifest_directories[0]
        self.assertIsInstance(directory1, dict)
        self.assertTrue('path' in directory1)
        self.assertTrue('type' in directory1)
        self.assertEqual('/tmp', directory1['path'])
        self.assertEqual('YAML', directory1['type'])

        directory2 = project.manifest_directories[1]
        self.assertIsInstance(directory2, dict)
        self.assertTrue('path' in directory2)
        self.assertTrue('type' in directory2)
        self.assertEqual('/something/else', directory2['path'])
        self.assertEqual('ABC', directory2['type'])

    def test_project_method_override_include_file_regex(self):
        project = Project(name='test')
        project.override_include_file_regex(include_file_regex=('a', 'b', 'c'))
        self.assertIsNotNone(project.include_file_regex)
        self.assertIsInstance(project.include_file_regex, tuple)
        self.assertEqual(len(project.include_file_regex), 3)
        self.assertTrue('a' in project.include_file_regex)
        self.assertTrue('b' in project.include_file_regex)
        self.assertTrue('c' in project.include_file_regex)

    def test_project_method_add_manifest_file(self):
        project = Project(name='test')

        project.add_manifest_file(path='/tmp/file1.yaml')
        self.assertEqual(len(project.manifest_files), 1)
        file1 = project.manifest_files[0]
        self.assertIsInstance(file1, dict)
        self.assertTrue('path' in file1)
        self.assertTrue('type' in file1)
        self.assertEqual('/tmp/file1.yaml', file1['path'])
        self.assertEqual('YAML', file1['type'])

        project.add_manifest_file(path='/file2', type='ABC')
        self.assertEqual(len(project.manifest_files), 2)
        file2 = project.manifest_files[1]
        self.assertIsInstance(file2, dict)
        self.assertTrue('path' in file2)
        self.assertTrue('type' in file2)
        self.assertEqual('/file2', file2['path'])
        self.assertEqual('ABC', file2['type'])
        




if __name__ == '__main__':
    unittest.main()
