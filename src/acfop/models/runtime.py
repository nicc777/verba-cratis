"""
    Copyright (c) 2022. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/acfop/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""


from acfop.utils import get_logger


class Variable:

    def __init__(self, id: str, initial_value: object=None, value_type: object=str):
        self.id = id
        self.value = initial_value
        self.value_type = value_type

    def __str__(self):
        return '{}'.format(self.value)


class VariableStateStore:

    def __init__(self, logger=get_logger()):
        self.variables = dict()
        self.logger = logger

    def add_variable(self, var: Variable):
        self.logger.info('Added variable: {}'.format(var.id))
        self.variables[var.id] = var

    def get_variable(self, id: str)->Variable:
        if id in self.variables:
            return self.variables[id]
        raise Exception('Variable with id "{}" does not exist'.format(id))

    def get_variable_value(self, id: str)->Variable:
        if id in self.variables:
            return self.variables[id].value
        raise Exception('Variable with id "{}" does not exist'.format(id))
        




