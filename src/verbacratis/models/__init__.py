"""
    Copyright (c) 2022-2023. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/verbacratis/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

from pathlib import Path
import os
import inspect


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
kind: StateStore
metadata:
  name: verbacratis-state-store
spec:
  connectionUrl: sqlite:///verbacratis.db
  provider: sqlalchemy
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
      parameterValue: '%(levelname)s - %(message)s'
""".format(DEFAULT_CONFIG_DIR, os.sep, DEFAULT_STATE_DB)


def id_caller()->list:
    result = list()
    try:
        caller_stack = inspect.stack()[2]
        result.append(caller_stack[1].split(os.sep)[-1]) # File name
        result.append(caller_stack[2]) # line number
        result.append(caller_stack[3]) # function name
    except: # pragma: no cover
      pass
    return result


class GenericLogger:

    def __init__(self, logger=None):
        self.enable_logging = False
        self.logger = None
        if logger is not None:
            self.logger = logger
            self.enable_logging = True

    def _format_msg(self, stack_data: list, message: str)->str:
        if message is not None:
            message = '{}'.format(message)
            if len(stack_data) == 3:
                message = '[{}:{}:{}] {}'.format(
                    stack_data[0],
                    stack_data[1],
                    stack_data[2],
                    message
                )
            return message
        return 'NO_INPUT_MESSAGE'

    def info(self, message_str):
        if self.enable_logging:
            try:
                self.logger.info(
                  self._format_msg(
                      stack_data=id_caller(), 
                      message=message_str
                  )
                )
                return
            except:
                self.enable_logging = False
        print('INFO: {}'.format(message_str))

    def debug(self, message_str):
        if self.enable_logging:
            try:
                self.logger.debug(
                  self._format_msg(
                      stack_data=id_caller(), 
                      message=message_str
                  )
                )
                return
            except:
                self.enable_logging = False
        print('DEBUG: {}'.format(message_str))

    def warn(self, message_str):
        if self.enable_logging:
            try:
                self.logger.warn(
                  self._format_msg(
                      stack_data=id_caller(), 
                      message=message_str
                  )
                )
                return
            except:
                self.enable_logging = False
        print('WARN: {}'.format(message_str))

    def error(self, message_str):
        if self.enable_logging:
            try:
                self.logger.error(
                  self._format_msg(
                      stack_data=id_caller(), 
                      message=message_str
                  )
                )
                return
            except:
                self.enable_logging = False
        print('ERROR: {}'.format(message_str))



