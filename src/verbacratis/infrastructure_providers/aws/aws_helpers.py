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


def get_aws_identity(
    boto3_clazz: object=boto3,
    region: str='eu-central-1',
    logger=get_logger(),
    include_account_if_available: bool=False,
    include_arn_if_available: bool=False,
    delimiter_char: str=','
):
    """Return the current AWS identity information

    This function can be helpful in determining the current identity used to obtain AWS credentials, especially when
    troubleshooting permission problems during deployments.

    The function essentially executes the following AWS CLI command equivalent:

    .. code-block:: shell

        $ aws sts get-caller-identity

    By default only the ``UserId`` will be returned.

    Examples:

    .. code-block:: python

        >>> get_aws_identity()
        >>> 'AIDACCCCCCCCCCCCCCCCC'

        >>> get_aws_identity()
        >>> 'AIDACCCCCCCCCCCCCCCCC'

        >>> get_aws_identity(include_account_if_available=True)
        >>> 'AIDACCCCCCCCCCCCCCCCC,123456789012'

        >>> get_aws_identity(include_account_if_available=True, include_arn_if_available=True, delimiter_char='|')
        >>> 'AIDACCCCCCCCCCCCCCCCC|123456789012|arn:aws:iam::123456789012:user/my-user'

    Args:
        boto3_clazz (boto3): The boto3 class. This parameter will only be set during unit testing and has no other real relevance
        region (str): The AWS region to target, if applicable. This parameter will be set by the deployer
        logger (logging.Logger): The logger function to call for logging events. This parameter will be set by the deployer
        include_account_if_available(bool): USER_PARAMETER: Boolean to indicate if the Account ID must be included
        include_arn_if_available(bool): USER_PARAMETER: Boolean to indicate if the Account ID must be included
        delimiter_char(str): USER_PARAMETER: If ``either include_account_if_available`` or ``include_arn_if_available`` is set, this value is the delimiter to use when concatenating all values in a CSV style string. DEFAULT: ``,``

    Returns:
        str: A CSV style string with the requested fields. 

    """
    result = ''
    try:
        client = get_client(client_name='sts', region=region, boto3_clazz=boto3_clazz)
        response = client.get_caller_identity()
        if 'UserId' in response:
            result = 'UserId={}'.format(response['UserId'])
        if 'Account' in response and include_account_if_available is True:
            result = '{}{}Account={}'.format(result, delimiter_char, response['Account'])
        if 'Arn' in response and include_arn_if_available is True:
            result = '{}{}Arn={}'.format(result, delimiter_char, response['Arn'])
    except:
        logger.error('EXCEPTION: {}'.format(traceback.format_exc()))
    return result
