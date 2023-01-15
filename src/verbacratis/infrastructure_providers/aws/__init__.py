import traceback
import boto3
from verbacratis.utils import get_logger


def get_client(client_name: str, region: str='eu-central-1', boto3_clazz=boto3, logger=get_logger):
    client = boto3_clazz.client(service_name=client_name, region_name=region)
    return client

