"""
    Copyright (c) 2022-2023. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/verbacratis/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

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