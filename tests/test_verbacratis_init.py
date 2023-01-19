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


from verbacratis import *
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
        conn = result.get_db_connection()
        self.assertIsNotNone(conn)
        self.assertIsInstance(conn, Engine)
        self.assertTrue(result.enable_state)

    def test_state_store_get_connection_sqlite_invalid_url_disables_state(self):
        result = StateStore(connection_url='not-valid')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, StateStore)
        conn = result.get_db_connection()
        self.assertFalse(result.enable_state)


class TestApplicationConfiguration(unittest.TestCase):    # pragma: no cover

    def test_application_configuration_init_with_defaults(self):
        result = ApplicationConfiguration(raw_global_configuration=DEFAULT_GLOBAL_CONFIG, logger=get_logger())
        self.assertIsNotNone(result)
        self.assertIsInstance(result, ApplicationConfiguration)


if __name__ == '__main__':
    unittest.main()
