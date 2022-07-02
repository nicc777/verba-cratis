"""
    Copyright (c) 2022. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/acfop/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")
print('sys.path={}'.format(sys.path))

import unittest


from acfop.functions.aws_helpers import get_aws_identity
from acfop.utils import *


class StsClientMock:    # pragma: no cover

    def get_caller_identity(self)->dict:
        return {
            "UserId": "AIDACCCCCCCCCCCCCCCCC",
            "Account": "123456789012",
            "Arn": "arn:aws:iam::214483558614:user/my-user",
        }


class Boto3Mock:    # pragma: no cover

    def __init__(self):
        pass

    def client(self, service_name: str, region_name: str='eu-central-1'):
        if service_name == 'sts':
            return StsClientMock()


class TestFunctionGetAwsIdentity(unittest.TestCase):    # pragma: no cover

    def setUp(self):
        self.boto3_clazz = Boto3Mock()

    def test_call_get_aws_identity_defaults(self):
        result = get_aws_identity(boto3_clazz=self.boto3_clazz)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        self.assertTrue('UserId' in result, 'result contained "{}"'.format(result))
        self.assertFalse('Account' in result, 'result contained "{}"'.format(result))
        self.assertFalse('Arn' in result, 'result contained "{}"'.format(result))
        self.assertEqual(result, 'UserId=AIDACCCCCCCCCCCCCCCCC', 'result contained "{}"'.format(result))


if __name__ == '__main__':
    unittest.main()
