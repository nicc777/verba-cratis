"""
    Copyright (c) 2022-2023. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/verbacratis/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

# import sys
# import os
# sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")
# print('sys.path={}'.format(sys.path))


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

