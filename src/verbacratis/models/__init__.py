"""
    Copyright (c) 2022-2023. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/verbacratis/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

from pathlib import Path
import os


AWS_REGIONS = (
    "af-south-1",
    "ap-south-1",
    "eu-north-1",
    "eu-west-3",
    "eu-west-2",
    "eu-west-1",
    "ap-northeast-3",
    "ap-northeast-2",
    "ap-northeast-1",
    "ca-central-1",
    "sa-east-1",
    "ap-southeast-1",
    "ap-southeast-2",
    "eu-central-1",
    "us-east-1",
    "us-east-2",
    "us-west-1",
    "us-west-2",
)


DEFAULT_CONFIG_DIR = '{}{}{}'.format(
    str(Path.home()),
    os.sep,
    '.verbacratis'
)

DEFAULT_STATE_DB = 'sqlite:///{}{}{}'.format(
    DEFAULT_CONFIG_DIR,
    os.sep,
    '.verbacratis.db'
)

DEFAULT_GLOBAL_CONFIG = """---
apiVersion: v1-alpha
kind: UnixHostAuthentication
metadata:
  name: localhost
---
apiVersion: v1-alpha
kind: InfrastructureAccount
metadata:
  name: deployment-host
spec:
  authenticationHostname: localhost
  provider: ShellScript
---
apiVersion: v1-alpha
kind: Project
metadata:
  name: test
spec:
  environments:
  - name: default
  includeFileRegex:
  - '*\.yml'
  - '*\.yaml'
  locations:
    files:
    - path: {}{}/default_project.yaml
      type: YAML
---
apiVersion: v1-alpha
kind: GlobalConfiguration
metadata:
  name: verbacratis
spec:
  stateStore:
    provider: sqlalchemy
    dbConfig:
      url: "{}"
  logging:
    handlers:
    - name: StreamHandler
      parameters:
    - parameterName: format
      parameterType: str
      parameterValue: '%(funcName)s:%(lineno)d -  %(levelname)s - %(message)s'
""".format(DEFAULT_CONFIG_DIR, os.sep, DEFAULT_STATE_DB)


class GenericLogger:

    def __init__(self, logger=None):
        self.enable_logging = False
        self.logger = None
        if logger is not None:
            self.logger = logger
            self.enable_logging = True

    def info(self, message_str):
        if self.enable_logging:
            try:
                self.logger.info(message_str)
                return
            except:
                self.enable_logging = False
        print('INFO: {}'.format(message_str))

    def debug(self, message_str):
        if self.enable_logging:
            try:
                self.logger.debug(message_str)
                return
            except:
                self.enable_logging = False
        print('DEBUG: {}'.format(message_str))

    def warn(self, message_str):
        if self.enable_logging:
            try:
                self.logger.warn(message_str)
                return
            except:
                self.enable_logging = False
        print('WARN: {}'.format(message_str))

    def error(self, message_str):
        if self.enable_logging:
            try:
                self.logger.error(message_str)
                return
            except:
                self.enable_logging = False
        print('ERROR: {}'.format(message_str))



