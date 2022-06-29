"""
    Copyright (c) 2022. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/acfop/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""


import traceback
from acfop.utils import get_logger
import subprocess, shlex
import hashlib
import tempfile
import os


VALID_CLASSIFICATIONS = (
    'build-variable',
    'ref',
    'exports',
    'shell',
    'other',    # When using Variable.get_value(), this type will force an exception
)


class Variable:

    """
        TODO Add support for "ref" classification - requires a configuration to variable reference processing function

        TODO Ass support for "exports" classification - requires a process to add exports after CloudFormation template deployment
    """
    def __init__(self, id: str, initial_value: object=None, value_type: object=str, classification: str='build-variable'):
        if classification not in VALID_CLASSIFICATIONS:
            raise Exception('Invalid Classification')
        if initial_value is not None:
            if isinstance(initial_value, value_type) is False:
                raise Exception('Initial value must match value_type or None')
        self.id = id
        self.value = initial_value
        self.value_type = value_type
        self.classification = classification
        self.value_checksum = hashlib.sha256(str(initial_value).encode(('utf-8'))).hexdigest()

    def get_value(self, logger=get_logger()):
        if self.classification in ('build-variable', 'ref', 'exports'):
            return self.value
        elif self.classification == 'shell':
            td = tempfile.gettempdir()
            fn = '{}{}{}'.format(td, os.sep, self.value_checksum)
            logger.debug('Created temp file {}'.format(fn))
            with open(fn, 'w') as f:
                f.write(self.value)
            result = subprocess.run(['/bin/sh', fn], stdout=subprocess.PIPE).stdout.decode('utf-8')
            logger.info('[{}] Command: {}'.format(self.value_checksum, self.value))
            logger.info('[{}] Command Result: {}'.format(self.value_checksum, result))
            return result
        raise Exception('Classification "{}" not yet supported'.format(self.classification))

    def __str__(self):
        return 'Variable: id={} classification={} >> value as string: {}'.format(self.id, self.classification, self.value)


class VariableStateStore:

    def __init__(self, logger=get_logger()):
        self.build_variables = dict()
        self.logger = logger

    def add_variable(self, var: Variable):
        self.logger.info('Added variable id "{}" with classification "{}"'.format(var.id, var.classification))
        if var.classification == 'build-variable':
            self.build_variables[var.id] = var
            return
        raise Exception('Variable classification "{}" is not supported'.format(var.classification))

    def get_variable(self, id: str, classification: str='build-variable')->Variable:
        if classification == 'build-variable':
            if id in self.build_variables:
                return self.build_variables[id]
        raise Exception('Variable with id "{}" with classification "{}" does not exist'.format(id, classification))

    def get_variable_value(self, id: str, classification: str='build-variable')->Variable:
        if classification == 'build-variable':
            if id in self.build_variables:
                return self.build_variables[id].get_value()
        raise Exception('Variable with id "{}" with classification "{}" does not exist'.format(id, classification))
        




