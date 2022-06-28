"""
    Copyright (c) 2022. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/acfop/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""


from acfop.utils import get_logger


class Variable:

    """
        TODO If the classification is something like "shell", then each time the value is retrieved the shell script must be executed
    """
    def __init__(self, id: str, initial_value: object=None, value_type: object=str, classification: str='build-variable'):
        self.id = id
        self.value = initial_value
        self.value_type = value_type
        self.classification = classification

    def get_value(self):
        if self.classification == 'build-variable':
            return self.value
        raise Exception('Classification "{}" not yet supported'.format(self.classification))

    def __str__(self):
        return 'Variable: id={} classification={} >> value as string: {}'.format(self.value)


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
        




