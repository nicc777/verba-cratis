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
    # 'func',   # TODO add support for function calls
    'other',    # When using Variable.get_value(), this type will force an exception
)
VARIABLE_IN_VARIABLE_PARSING_MAX_DEPTH = 3


class Variable:

    """
        External Dependencies:

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
        self.variables = dict()
        self.variables['build-variable'] = dict()
        self.variables['ref'] = dict()
        self.variables['exports'] = dict()
        self.variables['shell'] = dict()
        self.variables['other'] = dict()
        self.logger = logger

    def add_variable(self, var: Variable):
        self.logger.info('Added variable id "{}" with classification "{}"'.format(var.id, var.classification))
        if var.classification in self.variables:
            self.variables[var.classification][var.id] = var
            return
        raise Exception('Variable classification "{}" is not supported'.format(var.classification))

    def get_variable(self, id: str, classification: str='build-variable')->Variable:
        if classification in self.variables:
            if id in self.variables[classification]:
                return self.variables[classification][id]
        raise Exception('Variable with id "{}" with classification "{}" does not exist'.format(id, classification))

    def _gvv(self, id: str, classification: str='build-variable'):
        if classification in self.variables:
            if id in self.variables[classification]:
                return self.variables[classification][id].get_value(logger=self.logger)
        raise Exception('Variable with id "{}" with classification "{}" does not exist'.format(id, classification))

    def get_variable_value(self, id: str, classification: str='build-variable', skip_embedded_variable_processing: bool=False):
        if skip_embedded_variable_processing is True:
            return self._gvv(id=id, classification=classification, logger=logger)
        final_value = None
        iteration_number = 0
        while iteration_number < VARIABLE_IN_VARIABLE_PARSING_MAX_DEPTH:
            value = self._gvv(id=id, classification=classification, logger=logger)
            # TODO Process embedded variable references in value, for example a value containing ${ref:CCC}

            final_value = value
        return final_value
        




