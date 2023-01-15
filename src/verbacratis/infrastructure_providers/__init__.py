import traceback
from verbacratis.utils import get_logger


class InfrastructureTemplateDeploymentBaseClass:

    def __init__(
        self,
        logger
    )->None:
        self.logger = logger

    def deploy(self):
        pass

    def update(self):
        pass

    def delete(self):
        pass


provider_registry = {
    'AWS-CloudFormation-Deployment': {
        'entry-point': 'TODO: Add the class name here (without quotes), to link to the class that extends InfrastructureTemplateDeploymentBaseClass'
    }
}