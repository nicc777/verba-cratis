"""
    Copyright (c) 2022. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/acfop/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""


import traceback
from acfop.utils import get_logger
from acfop.utils.parser import variable_snippet_extract
from acfop.functions import user_function_factory
import subprocess, shlex
import hashlib
import tempfile
import os
import random, string   # TODO temporary use - remove later


VALID_CLASSIFICATIONS = (
    'build-variable',
    'ref',
    'exports',
    'shell',
    'func',     # TODO add support for function calls
    'other',    # When using Variable.get_value(), this type will force an exception
)
VARIABLE_IN_VARIABLE_PARSING_MAX_DEPTH = 3
FUNCTIONS = user_function_factory()


class Variable:

    """
        External Dependencies:

            TODO Add support for "ref" classification - requires a configuration to variable reference processing function

            TODO Ass support for "exports" classification - requires a process to add exports after CloudFormation template deployment
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
        return self.value

    def __str__(self):
        return 'Variable: id={} classification={} >> value as string: {}'.format(self.id, self.classification, self.value)


class VariableStateStore:

    def __init__(self, logger=get_logger()):
        self.variables = dict()
        self.variables['build-variable'] = dict()
        self.variables['ref'] = dict()
        self.variables['exports'] = dict()
        self.variables['shell'] = dict()
        self.variables['func'] = dict()
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

    def _process_snippet(self, value: str, classification: str='build-variable', function_fixed_parameters: dict=dict()):
        self.logger.debug('value={}'.format(value))
        if classification in ('build-variable', 'ref', 'exports'):
            return value
        elif classification == 'shell':
            td = tempfile.gettempdir()
            value_checksum = hashlib.sha256(str(value).encode(('utf-8'))).hexdigest()
            fn = '{}{}{}'.format(td, os.sep, value_checksum)
            self.logger.debug('Created temp file {}'.format(fn))
            with open(fn, 'w') as f:
                f.write(value)
            result = subprocess.run(['/bin/sh', fn], stdout=subprocess.PIPE).stdout.decode('utf-8')
            self.logger.info('[{}] Command: {}'.format(value_checksum, value))
            self.logger.info('[{}] Command Result: {}'.format(value_checksum, result))
            return result
        elif classification == 'func':
            # Note: Initial parameters is in function_fixed_parameters
            # TODO implement function calling

            if '(' in value:
                function_name = value.split('(')[0]
                if ':' in function_name:
                    function_name = function_name.split(':')[1]
                self.logger.debug('function_name={}'.format(function_name))
                if function_name not in FUNCTIONS:
                    raise Exception('Function "{}" is not a recognized function.'.format(function_name))
            else:
                raise Exception('Value does not appear to contain a function call')
            return 'function-not-executed'
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
            for deeper_level, snippet_collection in next_level_snippets.items():
                if len(snippet_collection) > 0:
                    if deeper_level not in new_snippets:
                        new_snippets[deeper_level] = list()
                    new_snippets[deeper_level] = snippet_collection
        
        return new_snippets

    def get_variable_value(self, id: str, classification: str='build-variable', skip_embedded_variable_processing: bool=False, iteration_number: int=0):
        variable = self.get_variable(id=id, classification=classification)
        line = variable.value
        self.logger.debug('line={}'.format(line))
        if skip_embedded_variable_processing is True:
            return line      
        final_value = None
        
        snippets = self._extract_snippets(value='{}'.format(line))
        self.logger.debug('snippets={}'.format(snippets))
        snippets_levels = list(snippets.keys())
        snippets_levels.sort(reverse=True)
        self.logger.debug('snippets_levels={}'.format(snippets_levels))

        while len(snippets_levels) > 1:
            snippet_level = snippets_levels[0]
            snippets_collection = snippets[snippet_level]
            self.logger.debug('Processing level {}'.format(snippet_level))
            self.logger.debug('snippets_collection={}'.format(snippets_collection))
            for snippet in snippets_collection:
                self.logger.debug('Final processing for snippet: {}'.format(snippet))
                classification, value = snippet.split(':', 1)
                processed_value = self._process_snippet(value=value, classification=classification, function_fixed_parameters=variable.extra_parameters)
                line = line.replace('${}{}{}'.format('{', snippet, '}'), '{}'.format(processed_value))
                self.logger.debug('line={}'.format(final_value))
                snippets = self._extract_snippets(value='{}'.format(line))                
                self.logger.debug('snippets={}'.format(snippets))
                snippets_levels = list(snippets.keys())
                snippets_levels.sort(reverse=True)
                self.logger.debug('snippets_levels={}'.format(snippets_levels))

        snippets_collection = snippets[0]
        self.logger.debug('snippets_collection={}'.format(snippets_collection))
        if len(snippets_collection) > 0:
            for snippet in snippets_collection:
                self.logger.debug('Final processing for snippet: {}'.format(snippet))
                classification, value = snippet.split(':', 1)
                processed_value = self._process_snippet(value=value, classification=classification)
                final_value = line.replace('${}{}{}'.format('{', snippet, '}'), '{}'.format(processed_value))
                self.logger.debug('final_value={}'.format(final_value))
        else:
            final_value = self._process_snippet(value=line, classification=classification)
            self.logger.debug('final_value={}'.format(final_value))
        self.logger.info('final_value={}'.format(final_value))
        return final_value
        
