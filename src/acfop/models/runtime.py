"""
    Copyright (c) 2022. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/acfop/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""


import traceback
from acfop.utils import get_logger
from acfop.utils.parser import variable_snippet_extract, validate_configuration
from acfop.utils.os_integration import exec_shell_cmd
from acfop.utils.function_runner import execute_function
from acfop.functions import user_function_factory
import subprocess, shlex
import hashlib
import tempfile
import os
import re
import ast
import random, string   # TODO temporary use - remove later


VALID_CLASSIFICATIONS = (
    'build-variable',
    'env',
    'ref',
    'exports',
    'shell',
    'func',
    'other',    # When using Variable.get_value(), this type will force an exception
)
VARIABLE_IN_VARIABLE_PARSING_MAX_DEPTH = 3
FUNCTIONS = user_function_factory()


class Variable:
    """Each unique path with a value in the configuration is stored as a Variable, as well as some other variables as required.

    The entire configuration will end up as a collection of Variable objects stored in :class:`VariableStateStore`

    TODO Add support for "exports" classification - requires a process to add exports after CloudFormation template deployment

    TODO Implement value_checksum updates when value changes. May require an update() method

    Attributes:
        id (:obj:`str`): For configuration files, represents the path of a configuration item. Otherwise, just use an identified that makes sense
        value (:obj:`object`): The current value of the variable. Some unprocessed Variables may have a string containing template directives. Once these are processed, the value should be updated to the processed value.
        value_type (:obj:`object`): The type expressed as a Python type. Consider sticking to the following primitives: str, bool, int - other will eventually be better supported.
        classification (:obj:`str`): One of ``VALID_CLASSIFICATIONS``
        value_checksum  (:obj:`str`): A calculated checksum of the :attr:`value`. Not currently used, but in future will be used to determine if a value needs re-evaluation
        extra_parameters (:obj:`dict`): Dictionary that may contain extra parameters required by the variable, depending on the ``classification``. Used mostly for ``functions``
    """
    def __init__(self, id: str, initial_value: object=None, value_type: object=str, classification: str='build-variable', extra_parameters: dict=dict()):
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
        self.extra_parameters = extra_parameters    # Used for Functions only

    def get_value(self, logger=get_logger()):
        """Gets the current ``value``

        Args:
            logger (:obj:`Logger`): A logger. Not used at the moment

        Returns:
            object: The ``value``
        """
        return self.value

    def __str__(self):
        return 'Variable: id={} classification={} >> value as string: {}'.format(self.id, self.classification, self.value)


class VariableStateStore:
    """A store for Variable objects

    Attributes:
        variables (:obj:`dict`): A dictionary of Variable objects partitioned by the Variable classification
        registered_functions (:obj:`dict`): A dictionary of functions
        logger (:obj:`Logger`): A logger object, for logging
    """

    def __init__(self, logger=get_logger(), registered_functions: dict=FUNCTIONS):
        self.variables = dict()
        self.variables['build-variable'] = dict()
        self.variables['ref'] = dict()
        self.variables['exports'] = dict()
        self.variables['shell'] = dict()
        self.variables['func'] = dict()
        self.variables['other'] = dict()
        self.variables['env'] = dict()
        self.logger = logger
        self.registered_functions = registered_functions
        self.logger.debug('registered_functions={}'.format(self.registered_functions))

    def update_variable(self, variable: Variable):
        """Updates an already stored :class:`Variable` object, replacing it with the supplied :class:`Variable` object

        Args:
            variable (:obj:`Variable`): The new :class:`Variable` object replacing the existing one (`id` and `classification` must match)
        """
        if variable.classification in self.variables:
            if variable.id in self.variables[variable.classification]:
                self.variables[variable.classification][variable.id] = variable

    def add_variable(self, var: Variable):
        """Adds a :class:`Variable` object to :attr:`variables`

        Args:
            variable (:obj:`Variable`): The :class:`Variable` object to store
        """
        self.logger.info('Added variable id "{}" with classification "{}"'.format(var.id, var.classification))
        if var.classification in self.variables:
            self.variables[var.classification][var.id] = var
            self.logger.debug('added variable: {}'.format(str(self.variables[var.classification][var.id])))
            return
        raise Exception('Variable classification "{}" is not supported'.format(var.classification))

    def get_variable(self, id: str, classification: str='build-variable')->Variable:
        """Retrieve a stored variable

        Args:
            id: The :attr:`Variable.id`
            classification: The :attr:`Variable.classification`

        Returns:
            Variable: The :class:`Variable` object matching the :attr:`Variable.id` and :attr:`Variable.classification`
        """
        if classification in self.variables:
            if id in self.variables[classification]:
                return self.variables[classification][id]
        raise Exception('Variable with id "{}" with classification "{}" does not exist'.format(id, classification))

    def _process_snippet(self, variable: Variable, function_fixed_parameters: dict=dict()):
        self.logger.debug('variable={}'.format(str(variable)))
        classification = variable.classification
        if classification == 'ref':     # this must lookup another variable (like a pointer) - must return first match from build-variable (the variable as parsed from the config - basically the keys/paths)
            return self.get_variable_value(id=variable.value, classification='build-variable')
        if classification in ('build-variable', 'exports'):
            return variable.value
        if classification in ('env'):  
            default_value = None
            if 'default_value' in function_fixed_parameters:
                default_value = function_fixed_parameters['default_value']
            value = os.getenv(variable.value, default=default_value)
            return value
        elif classification == 'shell':
            return exec_shell_cmd(cmd=variable.value, logger=self.logger)
        elif classification == 'func':
            function_exec_result = execute_function(
                function_template=variable.value,                     # Comes from Variable.value
                function_fixed_parameters=function_fixed_parameters,
                logger=self.logger,
                registered_functions=self.registered_functions
            )
            self.logger.debug('function_exec_result={}'.format(function_exec_result))
            return function_exec_result
        raise Exception('Classification "{}" not yet supported'.format(classification)) # pragma: no cover
        
    def _extract_snippets(self, value: str, level: int=0)->dict:
        self.logger.debug('level {}: processing value: {}'.format(level, value))
        new_snippets = dict()
        new_snippets[level] = list()
        if level > VARIABLE_IN_VARIABLE_PARSING_MAX_DEPTH:
            raise Exception('Maximum embedded variable parsing depth exceeded')
        
        snippets = variable_snippet_extract(line=value)
        self.logger.debug('snippets={}'.format(snippets))
        next_level_snippets = dict()
        for snippet in snippets:
            new_snippets[level].append(snippet)
        for snippet in snippets:
            self.logger.debug('extracting next level snippet: {}'.format(snippet))
            next_level_snippets = self._extract_snippets(value=snippet, level=level+1)
            self.logger.debug('next_level_snippets={}'.format(next_level_snippets))
            for deeper_level, snippet_collection in next_level_snippets.items():
                if len(snippet_collection) > 0:
                    if deeper_level not in new_snippets:
                        new_snippets[deeper_level] = list()
                    new_snippets[deeper_level] = snippet_collection
        
        return new_snippets

    def _get_variable_run_result(self, current_variable: Variable, updated_value: object=None)->str:
        self.logger.debug('Getting new temporary variable from current variable: {}'.format(str(current_variable)))
        self.logger.debug('    initial_value will be set to "{}"'.format(updated_value))
        new_variable = Variable(id=current_variable.id, initial_value=updated_value, value_type=type(updated_value), classification=current_variable.classification, extra_parameters=current_variable.extra_parameters)
        self.logger.debug('new_variable={}'.format(str(new_variable)))
        result = self._process_snippet(variable=new_variable, function_fixed_parameters=new_variable.extra_parameters)
        self.logger.debug('result={}'.format(result))
        return result

    def _process_snippet_line(self, line: str, variable: Variable=None)->str:
        self.logger.debug('line={}'.format(line))
        result = line
        if variable is not None:
            result = variable.value
        snippets = self._extract_snippets(value='{}'.format(line))
        self.logger.debug('snippets={}'.format(snippets))
        if len(snippets) > 0:
            for snippet in snippets[0]:
                template_line = '${}{}{}'.format('{', snippet, '}')
                self.logger.debug('Getting value for snippet "{}"'.format(template_line))

                next_variable = variable
                next_id = snippet.split(':', 1)[1]
                next_classification = snippet.split(':', 1)[0]
                if next_classification != 'ref':
                    self.logger.debug('next_id={}   next_classification={}'.format(next_id, next_classification))
                    next_variable = self.get_variable(id=next_id, classification=next_classification)
                    self.logger.debug('next_variable={}'.format(str(next_variable)))

                snippet_value = self._process_snippet_line(line=snippet, variable=next_variable) 
                self.logger.debug('snippet_value={}'.format(snippet_value))
                result = result.replace(template_line, '{}'.format(snippet_value))
                self.logger.debug('result={}'.format(result))

        
        result = self._get_variable_run_result(current_variable=variable, updated_value=result)
        self.logger.debug('result={}'.format(result))
        return result

    def get_variable_value(self, id: str, classification: str='build-variable', skip_embedded_variable_processing: bool=False, iteration_number: int=0):
        """Retrieve the calculated final value of a :class:`Variable` object

        Some :class:`Variable` objects may include template references to functions or shell scripts. These will be 
        executed and other template references will be parsed to obtain their respective values that will then be 
        replacing the template placeholders in order to build up the final value.

        Args:
            id: The :attr:`Variable.id`
            classification: The :attr:`Variable.classification`
            skip_embedded_variable_processing (:obj:`bool`): If set to ``True``, returns the raw value without any further processing

        Returns:
            object: The calculated value, converted to the type indicated by the :attr:`Variable.value_type`
        """
        variable = self.get_variable(id=id, classification=classification)
        if skip_embedded_variable_processing is True:
            self.logger.debug('skip_embedded_variable_processing :: returning value "{}" of type "{}"'.format(variable.value, variable.value_type))
            return variable.value  
        result = variable.value
        snippets = self._extract_snippets(value='{}'.format(variable.value))
        self.logger.debug('snippets={}'.format(snippets))
        if len(snippets) > 0:
            for snippet in snippets[0]:
                self.logger.debug('Getting value for snippet "{}"'.format(snippet))
                snippet_value = self._process_snippet_line(line=snippet, variable=variable)
                template_line = '${}{}{}'.format('{', snippet, '}')
                result = result.replace(template_line, snippet_value)
                self.logger.debug('PROGRESSION: result={}'.format(result))

        old_result = result
        try:
            result = self._get_variable_run_result(current_variable=variable, updated_value=result)
            self.logger.debug('result={}'.format(result))
        except:
            self.logger.error('EXCEPTION: {}'.format(traceback.format_exc()))
            self.logger.info('Calling _get_variable_run_result() resulted in an exception - in most cases this should not be a problem.')
            result = old_result

        self.logger.debug('variable.value_type={}'.format(variable.value_type))
        if str(variable.value_type) == '<class \'str\'>':
            if isinstance(result, str) is False:    # pragma: no cover
                result = '{}'.format(result)        # TODO Very unlikely to ever reach this scenario - so consider removing this in the future
        elif str(variable.value_type) == '<class \'bool\'>':
            if isinstance(result, str) is True:
                if result.lower().startswith('t'):  # pragma: no cover
                    result = True                   # TODO Very unlikely to ever reach this scenario - so consider removing this in the future
                elif result.lower().startswith('1'):
                    result = True
                else:
                    result = False
            elif isinstance(result, int) is True:
                result = bool(result)
            else:                                   # pragma: no cover
                result = False                      # TODO Very unlikely to ever reach this scenario - so consider removing this in the future
        elif str(variable.value_type) == '<class \'int\'>': # pragma: no cover
            if isinstance(result, str) is True:             # TODO Very unlikely to ever reach this scenario - so consider removing this in the future
                result = int(result)
            elif isinstance(result, bool) is True:
                if result is True:
                    result = 1
                else:
                    result = 0
        else:                                       # pragma: no cover
            result = '{}'.format(result)            # TODO Very unlikely to ever reach this scenario - so consider removing this in the future
        self.logger.debug('FINAL: type={} result={}'.format(type(result), result))
        return result

   
def configuration_to_variable_state_store(configuration: dict, logger=get_logger(), registered_functions: dict=FUNCTIONS)->VariableStateStore:
    vss = VariableStateStore(registered_functions=registered_functions)
    if not validate_configuration(configuration=configuration):
        raise Exception('Configuration is invalid')

    return vss
