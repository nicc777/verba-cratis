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


class StsClientRaiseExceptionMock:    # pragma: no cover

    def get_caller_identity(self)->dict:
        raise Exception('An Error')


class Boto3ExceptionMock:    # pragma: no cover

    def __init__(self):
        pass

    def client(self, service_name: str, region_name: str='eu-central-1'):
        if service_name == 'sts':
            return StsClientRaiseExceptionMock()


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

    def test_call_get_aws_identity_account_and_include_account_if_available_with_default_separator(self):
        result = get_aws_identity(boto3_clazz=self.boto3_clazz, include_account_if_available=True)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        self.assertTrue('UserId' in result, 'result contained "{}"'.format(result))
        self.assertTrue('Account' in result, 'result contained "{}"'.format(result))
        self.assertFalse('Arn' in result, 'result contained "{}"'.format(result))
        self.assertEqual(result, 'UserId=AIDACCCCCCCCCCCCCCCCC,Account=123456789012', 'result contained "{}"'.format(result))

    def test_call_get_aws_identity_account_and_all_options_with_pipe_separator(self):
        result = get_aws_identity(boto3_clazz=self.boto3_clazz, include_account_if_available=True, include_arn_if_available=True, delimiter_char='|')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        self.assertTrue('UserId' in result, 'result contained "{}"'.format(result))
        self.assertTrue('Account' in result, 'result contained "{}"'.format(result))
        self.assertTrue('Arn' in result, 'result contained "{}"'.format(result))
        self.assertEqual(result, 'UserId=AIDACCCCCCCCCCCCCCCCC|Account=123456789012|Arn=arn:aws:iam::214483558614:user/my-user', 'result contained "{}"'.format(result))

    def test_call_get_aws_identity_force_exception(self):
        result = get_aws_identity(boto3_clazz=Boto3ExceptionMock())
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        self.assertEqual(result, '')


if __name__ == '__main__':
    unittest.main()
