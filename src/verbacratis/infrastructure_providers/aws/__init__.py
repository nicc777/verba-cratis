"""
    Copyright (c) 2022-2023. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/verbacratis/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

import traceback
import boto3
from verbacratis.utils import get_logger


def get_client(client_name: str, region: str='eu-central-1', boto3_clazz=boto3, logger=get_logger):
    client = boto3_clazz.client(service_name=client_name, region_name=region)
    return client

