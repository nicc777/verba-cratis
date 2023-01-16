"""
    Copyright (c) 2022. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/verbacratis/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")
print('sys.path={}'.format(sys.path))

import unittest

from verbacratis.notification_providers.rest import *
from verbacratis.utils import get_logger


class TestNotificationProviderBaseClass(unittest.TestCase):    # pragma: no cover

    def test_base_implementation_basic(self):
        en = SendRestMessage(logger=get_logger())
        data = {"test": 123}

        self.assertIsNotNone(en)
        self.assertIsInstance(en, NotificationProviderBaseClass)
        self.assertIsInstance(en, SendRestMessage)

        en.set_parameter(name='URL', value='http://localhost:8089/anything')

        self.assertIsNotNone(en.parameters)
        self.assertIsInstance(en.parameters, dict)
        self.assertTrue('URL' in en.parameters)

        result = en.send_message(message='{}'.format(json.dumps(data)))

        self.assertIsNotNone(result)
        self.assertIsInstance(result, bool)


if __name__ == '__main__':
    unittest.main()
