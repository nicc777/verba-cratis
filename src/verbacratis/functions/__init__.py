"""
    Copyright (c) 2022-2023. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/verbacratis/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

import traceback
import boto3
from verbacratis.infrastructure_providers.aws import get_client
from verbacratis.utils import get_logger

# USER FUNCTIONS
from verbacratis.infrastructure_providers.aws.aws_helpers import get_aws_identity

def user_function_factory(
    boto3_clazz: object=boto3,
    logger=get_logger()
)->dict:
    result = dict()

    logger.debug('Adding user function "get_aws_identity"')
    result['get_aws_identity'] = dict()
    result['get_aws_identity']['f'] = get_aws_identity
    result['get_aws_identity']['fixed_parameters'] = dict()
    result['get_aws_identity']['fixed_parameters']['boto3_clazz'] = boto3_clazz
    result['get_aws_identity']['fixed_parameters']['logger'] = logger

    return result

