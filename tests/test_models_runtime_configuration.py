"""
    Copyright (c) 2022-2023. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/verbacratis/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

import sys
import os
import tempfile
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

    def test_state_store_dump_yaml(self):
        result = StateStore()
        state_store_yaml = str(result)
        self.assertIsNotNone(state_store_yaml)
        self.assertIsInstance(state_store_yaml, str)
        self.assertTrue(len(state_store_yaml) > 10)
        print('='*80)
        print('# StateStore YAML')
        print(state_store_yaml)
        print('='*80)


class TestApplicationConfiguration(unittest.TestCase):    # pragma: no cover

    def test_application_configuration_init_with_defaults(self):
        result = ApplicationRuntimeConfiguration()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, ApplicationRuntimeConfiguration)


if __name__ == '__main__':
    unittest.main()
