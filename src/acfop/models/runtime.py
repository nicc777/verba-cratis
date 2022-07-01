"""
    Copyright (c) 2022. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/acfop/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""


import traceback
from acfop.utils import get_logger
from acfop.utils.parser import variable_snippet_extract
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
        elif self.classification == 'func':
            # TODO implement function calling
            return 'function-not-executed'
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

    def _gvv(self, id: str, classification: str='build-variable'):
        if classification in self.variables:
            if id in self.variables[classification]:
                return self.variables[classification][id].get_value(logger=self.logger)
        raise Exception('Variable with id "{}" with classification "{}" does not exist'.format(id, classification))

    def _random_string(self, chars=string.ascii_uppercase + string.digits, N=10)->str:  # TODO  remove after temporary use is done.
        return ''.join(random.choice(chars) for _ in range(N))

    def _process_snippet(self, snippet:str)->str:
        result = None
        self.logger.info('Processing Snippet: {}'.format(snippet))
        
        # TODO - process snippets
        result = self._random_string(N=7)

        self.logger.debug('result={}'.format(result))
        return result

    def _extract_snippets(self, value: str, level: int=0)->dict:
        self.logger.debug('level {}: processing value: {}'.format(level, value))
        new_snippets = dict()
        new_snippets[level] = list()
        if level > VARIABLE_IN_VARIABLE_PARSING_MAX_DEPTH:
            raise Exception('Maximum embedded variable parsing depth exceeded')
        try:
            snippets = variable_snippet_extract(line=value)
            self.logger.debug('snippets={}'.format(snippets))
            next_level_snippets = dict()
            for snippet in snippets:
                self.logger.debug('extracting next level snippet: {}'.format(snippet))
                next_level_snippets = self._extract_snippets(value=snippet, level=level+1)
                new_snippets[level].append(snippet)
            for deeper_level, snippet_collection in next_level_snippets.items():
                if len(snippet_collection) > 0:
                    if deeper_level not in new_snippets:
                        new_snippets[deeper_level] = list()
                    new_snippets[deeper_level] = snippet_collection
        except:
            self.logger.error('EXCEPTION: {}'.format(traceback.format_exc()))
        return new_snippets

    def get_variable_value(self, id: str, classification: str='build-variable', skip_embedded_variable_processing: bool=False, iteration_number: int=0):
        line = self.get_variable(id=id, classification=classification).value
        self.logger.debug('line={}'.format(line))
        value = self._gvv(id=id, classification=classification)
        self.logger.debug('Initial Value: {}'.format(value))
        if skip_embedded_variable_processing is True:
            return value      
        final_value = value
        snippets = self._extract_snippets(value='{}'.format(line))
        self.logger.debug('snippets={}'.format(snippets))
        snippets_levels = list(snippets.keys())
        snippets_levels.sort(reverse=True)
        self.logger.debug('snippets_levels={}'.format(snippets_levels))
        for snippet_level in  snippets_levels:
            snippets_collection = snippets[snippet_level]
            self.logger.debug('Processing level {}'.format(snippet_level))
            self.logger.debug('snippets_collection={}'.format(snippets_collection))
            for snippet in snippets_collection:
                self.logger.debug('Final processing for snippet: {}'.format(snippet))
                processed_value = self._process_snippet(snippet=snippet)
                final_value = final_value.replace(snippet, '{}'.format(processed_value))


        # snippets = variable_snippet_extract(line=value)
        # if len(snippets) > 0:
        #     for snippet in snippets:
        #         snippet_cs = hashlib.sha256(str(snippet).encode(('utf-8'))).hexdigest()
        #         snippet_place_holder_string = '{}{}{}{}'.format(
        #             '$', '{', snippet, '}'
        #         )
        #         value = value.replace(snippet_place_holder_string, snippet_cs)
        #         next_classification, next_id = snippet.split(':', 1)
        #         value = value.replace(
        #             snippet_cs,
        #             self.get_variable_value(id=next_id, classification=next_classification, skip_embedded_variable_processing=skip_embedded_variable_processing, iteration_number=next_iteration_number)
        #         )
        # final_value = value

        self.logger.info('final_value={}'.format(final_value))
        return final_value
        




