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

from verbacratis.notification_providers import *


class EchoNotifier(NotificationProviderBaseClass):
    def __init__(self, logger=None)->None:
        super().__init__(logger)

    def _send_message_implementation(self, message: str, parameter_overrides: dict)->bool:
        print(message)
        return True


class TestNotificationProviderBaseClass(unittest.TestCase):    # pragma: no cover

    def test_base_implementation_basic(self):
        en = EchoNotifier(logger=get_logger())

        self.assertIsNotNone(en)
        self.assertIsInstance(en, NotificationProviderBaseClass)
        self.assertIsInstance(en, EchoNotifier)

        en.set_parameter(name='URL', value='http://localhost:8089/anything')

        self.assertIsNotNone(en.parameters)
        self.assertIsInstance(en.parameters, dict)
        self.assertTrue('URL' in en.parameters)

        result = en.send_message(message='test')

        self.assertIsNotNone(result)
        self.assertIsInstance(result, bool)
        self.assertTrue(result)

    def test_base_implementation_duplicate_parameter_raises_exception(self):
        en = EchoNotifier(logger=get_logger())
        en.set_parameter(name='URL', value='http://localhost:8089/anything')
        with self.assertRaises(Exception) as context:
            en.set_parameter(name='URL', value='https://google.com')
        self.assertTrue('Parameter already defined' in str(context.exception))

    def test_base_implementation_get_parameter_that_was_set(self):
        en = EchoNotifier(logger=get_logger())
        en.set_parameter(name='test', value='test-value')
        result = en.get_parameter_value(name='test')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        self.assertEqual('test-value', result)

    def test_base_implementation_get_parameter_that_was_not_set_returns_none(self):
        en = EchoNotifier(logger=get_logger())
        result = en.get_parameter_value(name='test')
        self.assertIsNone(result)

    def test_base_implementation_parameter_override(self):
        en = EchoNotifier(logger=get_logger())
        en.set_parameter(name='test', value='test-value')
        result = en._get_final_parameters(parameter_overrides={'test': 'new-value'})
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertEqual('new-value', result['test'])


if __name__ == '__main__':
    unittest.main()
