import traceback
import boto3
from acfop.utils import get_logger


def get_client(client_name: str, region: str='eu-central-1', boto3_clazz=boto3):
    client = boto3_clazz.client(service_name=client_name, region_name=region)
    return client

