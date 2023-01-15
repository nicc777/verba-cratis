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

