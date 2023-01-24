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


if __name__ == '__main__':
    unittest.main()
