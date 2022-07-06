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
import re
import ast
import random, string   # TODO temporary use - remove later


VALID_CLASSIFICATIONS = (   # TODO add env variable type
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
            self.logger.debug('added variable: {}'.format(str(self.variables[var.classification][var.id])))
            return
        raise Exception('Variable classification "{}" is not supported'.format(var.classification))

    def get_variable(self, id: str, classification: str='build-variable')->Variable:
        if classification in self.variables:
            if id in self.variables[classification]:
                return self.variables[classification][id]
        raise Exception('Variable with id "{}" with classification "{}" does not exist'.format(id, classification))

    def _get_function_parameters(self, function_name: str, function_fixed_parameters: dict=dict(), template_parameters: dict=dict())->dict:
        parameters = dict()
        self.logger.debug('function_fixed_parameters={}'.format(function_fixed_parameters))
        function_default_parameters = FUNCTIONS[function_name]['fixed_parameters']
        self.logger.debug('function_default_parameters={}'.format(function_default_parameters))
        for k, v in function_default_parameters.items():
            parameters[k] = v
        for k, v in function_fixed_parameters.items():
            parameters[k] = v
        for k, v in template_parameters.items():
            parameters[k] = v
        return parameters

    def _extract_function_parameters(self, value: str)->dict:
        # value: value = 'get_aws_identity(include_account_if_available="hh", blabla=True, something="1,2")'
        parameters = dict()
        try:
            value = value.strip()
            value = value.partition('(')[2].rpartition(')')[0]  # 'include_account_if_available="hh", blabla=True, something="1,2"'
            self.logger.debug('value={}'.format(value))

            # Following 5 line from https://stackoverflow.com/questions/49723047/parsing-a-string-as-a-python-argument-list
            args = 'f({})'.format(value)
            tree = ast.parse(args)
            funccall = tree.body[0].value
            args = [ast.literal_eval(arg) for arg in funccall.args]
            kwargs = {arg.arg: ast.literal_eval(arg.value) for arg in funccall.keywords}

            # For now, we only support kwargs... 
            parameters = kwargs

        except:
            self.logger.error('EXCEPTION: {}'.format(traceback.format_exc()))
        self.logger.debug('parameters={}'.format(parameters))
        return parameters

    def _process_snippet(self, variable: Variable, classification: str='build-variable', function_fixed_parameters: dict=dict()):
        self.logger.debug('variable={}'.format(str(variable)))
        if classification == 'ref':     # FIXME this is not working
            return variable.value
        if classification in ('build-variable', 'exports'):  # TODO add support for env
            return variable.value
        elif classification == 'shell':
            td = tempfile.gettempdir()
            value_checksum = hashlib.sha256(str(variable.value).encode(('utf-8'))).hexdigest()
            fn = '{}{}{}'.format(td, os.sep, value_checksum)
            self.logger.debug('Created temp file {}'.format(fn))
            with open(fn, 'w') as f:
                f.write(variable.value)
            result = subprocess.run(['/bin/sh', fn], stdout=subprocess.PIPE).stdout.decode('utf-8')
            self.logger.info('[{}] Command: {}'.format(value_checksum, variable.value))
            self.logger.info('[{}] Command Result: {}'.format(value_checksum, result))
            return result
        elif classification == 'func':
            function_exec_result = ''
            if '(' in variable.value:
                function_name = variable.value.split('(')[0]
                if ':' in function_name:
                    function_name = function_name.split(':')[1]
                self.logger.debug('function_name={}'.format(function_name))
                if function_name not in FUNCTIONS:
                    raise Exception('Function "{}" is not a recognized function.'.format(function_name))
                parameters = self._get_function_parameters(
                    function_name=function_name,
                    function_fixed_parameters=function_fixed_parameters,
                    template_parameters=self._extract_function_parameters(value=variable.value)
                )
                #                                      get_aws_identity(include_account_if_available=hh)
                # TODO Fix the Variable replacement..................................................^^
                self.logger.debug('parameters={}'.format(parameters))
                try:
                    function_exec_result = FUNCTIONS[function_name]['f'](**parameters)
                    self.logger.debug('EXEC RESULT :: function_exec_result={}'.format(function_exec_result))
                except:
                    self.logger.error('EXCEPTION: {}'.format(traceback.format_exc()))
            else:
                raise Exception('Value does not appear to contain a function call')
            self.logger.debug('function_exec_result={}'.format(function_exec_result))
            return function_exec_result
        raise Exception('Classification "{}" not yet supported'.format(classification)) # pragma: no cover
        
    def _extract_snippets_OLD(self, value: str, level: int=0)->dict:
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

    def get_variable_value(self, id: str, classification: str='build-variable', skip_embedded_variable_processing: bool=False, iteration_number: int=0):
        variable = self.get_variable(id=id, classification=classification)
        if skip_embedded_variable_processing is True:
            self.logger.debug('skip_embedded_variable_processing :: returning value "{}" of type "{}"'.format(variable.value, variable.value_type))
            return variable.value  
        snippets = self._extract_snippets(value='{}'.format(variable.value))
        self.logger.debug('snippets={}'.format(snippets))
        if len(snippets) > 0:
            level_idx = len(snippets) - 1
            while level_idx > 0:
                snippets_on_this_level = snippets[level_idx]
                self.logger.debug('Processing IDX {}   -> qty of snippets_on_this_level={}'.format(level_idx, len(snippets_on_this_level)))
                self.logger.debug('  snippets={}'.format(snippets))
                for snippet in snippets_on_this_level:
                    
                    snippet_template_placeholder = '${}{}{}'.format('{',snippet,'}')
                    self.logger.debug('  snippet_template_placeholder={}'.format(snippet_template_placeholder))

                    next_id = snippet.split(':')[1]
                    next_classification = snippet.split(':')[0]
                    self.logger.debug('    next_id={}   next_classification={}'.format(next_id, next_classification))
                    snippet_calculated_value = self.get_variable_value(id=next_id, classification=next_classification, skip_embedded_variable_processing=True)
                    self.logger.debug('      snippet_calculated_value={}'.format(snippet_calculated_value))

                    # Replace all lower level snippet templates with the calculated values
                    snippets_lower_level = snippets[level_idx-1]
                    new_lower_snippets = list()
                    for snippet_on_lower_level in snippets_lower_level:
                        self.logger.debug('        Processing template replacements for lower level snippet:{}'.format(snippet_on_lower_level))
                        self.logger.debug('        snippet_template_placeholder={}'.format(snippet_template_placeholder))
                        self.logger.debug('        snippet_calculated_value={}'.format(snippet_calculated_value))
                        new_line = snippet_on_lower_level.replace('{}'.format(snippet_template_placeholder), '{}'.format(snippet_calculated_value))
                        self.logger.debug('        new_line={}'.format(new_line))
                        new_lower_snippets.append(new_line)
                    snippets[level_idx-1] = new_lower_snippets
                    self.logger.debug('      snippets={}'.format(snippets))
                

                level_idx -= 1
        
        processed_value = self._process_snippet(variable=variable, classification=classification, function_fixed_parameters=variable.extra_parameters)
        self.logger.debug('processed_value={}'.format(processed_value))

        return 'INVALID VALUE'

    def get_variable_value_OLD(self, id: str, classification: str='build-variable', skip_embedded_variable_processing: bool=False, iteration_number: int=0):
        variable = self.get_variable(id=id, classification=classification)
        line = variable.value
        self.logger.debug('line={}'.format(line))
        if skip_embedded_variable_processing is True:
            return line      
        final_value = None
        
        snippets = self._extract_snippets(value='{}'.format(line))
        if len(snippets) > 0:
            self.logger.debug('snippets={}'.format(snippets))
            snippets_levels = list(snippets.keys())
            snippets_levels.sort(reverse=True)
            self.logger.debug('snippets_levels={}'.format(snippets_levels))

            idx = len(snippets_levels) -1
            while idx > 0:              # Level 1
                idx_lower = idx - 1     # Level 0

                processed_value = self._process_snippet(variable=next_variable, value=value, classification=classification, function_fixed_parameters=variable.extra_parameters)

                idx -= 1








        while len(snippets_levels) > 1:
            snippet_level = snippets_levels[0]
            snippets_collection = snippets[snippet_level]
            self.logger.debug('Processing level {}'.format(snippet_level))
            self.logger.debug('snippets_collection={}'.format(snippets_collection))
            for snippet in snippets_collection:
                self.logger.debug('Final processing for snippet: {}'.format(snippet))

                next_id = snippet.split(':')[1]
                next_classification = snippet.split(':')[0]
                self.logger.debug('next_id={}   next_classification={}'.format(next_id, next_classification))
                next_variable = self.get_variable_value(id=next_id, classification=next_classification)
                self.logger.debug('next_variable={}'.format(next_variable))

                if ':' in next_variable:
                    classification, value = snippet.split(':', 1)
                    processed_value = self._process_snippet(variable=next_variable, value=value, classification=classification, function_fixed_parameters=variable.extra_parameters)
                    self.logger.debug('processed_value={}'.format(processed_value))
                    line = line.replace('${}{}{}'.format('{', snippet, '}'), '{}'.format(processed_value))
                    self.logger.debug('line={}'.format(line))
                    # snippets = self._extract_snippets(value='{}'.format(line))                
                    # self.logger.debug('snippets={}'.format(snippets))
                    # snippets_levels = list(snippets.keys())
                    # snippets_levels.sort(reverse=True)
                    # self.logger.debug('snippets_levels={}'.format(snippets_levels))

        if len(snippets) > 0:
            snippets_collection = snippets[0]
            self.logger.debug('snippets_collection={}'.format(snippets_collection))
            if len(snippets_collection) > 0:
                for snippet in snippets_collection:
                    self.logger.debug('Final processing for snippet: {}'.format(snippet))
                    classification, value = snippet.split(':', 1)
                    processed_value = self._process_snippet(variable=variable, value=value, classification=classification, function_fixed_parameters=variable.extra_parameters)
                    final_value = line.replace('${}{}{}'.format('{', snippet, '}'), '{}'.format(processed_value))
                    self.logger.debug('final_value={}'.format(final_value))
            else:
                final_value = self._process_snippet(variable=variable, value=line, classification=classification, function_fixed_parameters=variable.extra_parameters)
                self.logger.debug('final_value={}'.format(final_value))
        self.logger.info('final_value={}'.format(final_value))
        return final_value
        
