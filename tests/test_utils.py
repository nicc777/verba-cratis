"""
    Copyright (c) 2022. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/acfop/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")
print('sys.path={}'.format(sys.path))

import unittest


from acfop.utils import *
import logging
import logging.handlers
import socket


import yaml
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


def mock_get_file_contents(file: str)->str: # pragma: no cover
    config = ""
    with open('examples/example_01/example_01.yaml', 'r') as f:
      config = f.read()
    return yaml.load(config, Loader=Loader)


class TestFunctionGetLoggingFileHandler(unittest.TestCase):    # pragma: no cover

    def test_call_get_logging_file_handler_with_defaults(self):
        result = get_logging_file_handler(filename='test.log')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, logging.FileHandler)

    def test_call_get_logging_file_handler_with_defaults_force_exception(self):
        result = get_logging_file_handler(filename=123)
        self.assertIsNone(result)


class TestFunctionGetTimedRotatingFileHandler(unittest.TestCase):    # pragma: no cover

    def test_call_get_timed_rotating_file_handler_with_defaults(self):
        result = get_timed_rotating_file_handler(filename='test.log')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, logging.handlers.TimedRotatingFileHandler)

    def test_call_get_timed_rotating_file_handler_with_defaults_force_exception(self):
        result = get_timed_rotating_file_handler(filename=123)
        self.assertIsNone(result)


class TestFunctionGetLoggingStreamHandler(unittest.TestCase):    # pragma: no cover

    def test_call_get_logging_stream_handler_with_defaults(self):
        result = get_logging_stream_handler()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, logging.StreamHandler)

    def test_call_get_logging_stream_handler_with_defaults_force_exception(self):
        result = get_logging_stream_handler(level=None)
        self.assertIsNone(result)


class TestFunctionGetLoggingDatagramHandler(unittest.TestCase):    # pragma: no cover

    def test_call_get_logging_datagram_handler_with_defaults(self):
        result = get_logging_datagram_handler()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, logging.handlers.DatagramHandler)

    def test_call_get_logging_datagram_handler_with_defaults_force_exception(self):
        result = get_logging_datagram_handler(level=None)
        self.assertIsNone(result)


class TestFunctionGetLoggingSyslogHandler(unittest.TestCase):    # pragma: no cover

    def test_call_get_logging_datagram_handler_with_defaults(self):
        result = get_logging_syslog_handler()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, logging.handlers.SysLogHandler)

    def test_call_get_logging_datagram_handler_with_defaults_force_exception(self):
        result = get_logging_syslog_handler(level=None)
        self.assertIsNone(result)


class TestFunctionGetLogger(unittest.TestCase):    # pragma: no cover

    def test_call_get_logger_with_defaults(self):
        result = get_logger()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, logging.Logger)
        qty = 0
        for h in result.handlers:
            qty += 1
        self.assertEqual(qty, 1)


    def test_call_get_logger_with_all_log_handlers_enabled(self):
        extra_parameters = {
            'filename': 'test.log',
            'host': 'localhost',
            'port': 514,
        }
        result = get_logger(
            include_logging_file_handler=True,
            include_logging_stream_handler=True,
            include_logging_timed_rotating_file_handler=True,
            include_logging_datagram_handler=True,
            include_logging_syslog_handler=True,
            extra_parameters=extra_parameters
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, logging.Logger)
        qty = 0
        for h in result.handlers:
            qty += 1
        self.assertEqual(qty, 5)

    def test_call_get_logger_with_rotating_handler_with_all_parameters_provided(self):
        extra_parameters = {
            'filename': 'test.log',
            'when': 'H',
            'interval': 1,
            'backupCount': 10,
        }
        result = get_logger(
            include_logging_file_handler=False,
            include_logging_stream_handler=False,
            include_logging_timed_rotating_file_handler=True,
            include_logging_datagram_handler=False,
            include_logging_syslog_handler=False,
            extra_parameters=extra_parameters
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, logging.Logger)
        qty = 0
        for h in result.handlers:
            qty += 1
        self.assertEqual(qty, 1)

    def test_call_get_logger_with_syslog_handler_with_all_parameters_provided(self):
        extra_parameters = {
            'host': 'localhost',
            'port': 514,
            'socktype': socket.SOCK_DGRAM,
        }
        result = get_logger(
            include_logging_file_handler=False,
            include_logging_stream_handler=False,
            include_logging_timed_rotating_file_handler=False,
            include_logging_datagram_handler=False,
            include_logging_syslog_handler=True,
            extra_parameters=extra_parameters
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, logging.Logger)
        qty = 0
        for h in result.handlers:
            qty += 1
        self.assertEqual(qty, 1)

    def test_call_get_logger_with_no_handlers_requested_get_default(self):
        result = get_logger(
            include_logging_file_handler=False,
            include_logging_stream_handler=False,
            include_logging_timed_rotating_file_handler=False,
            include_logging_datagram_handler=False,
            include_logging_syslog_handler=False
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, logging.Logger)
        qty = 0
        for h in result.handlers:
            qty += 1
        self.assertEqual(qty, 1)


class TestGetLoggingLevelFromString(unittest.TestCase):    # pragma: no cover

    def test_call_get_logging_level_from_string_with_info(self):
        result = get_logging_level_from_string(level='info')
        self.assertIsNotNone(result)
        self.assertEqual(result, logging.INFO)

    def test_call_get_logging_level_from_string_with_warn(self):
        result = get_logging_level_from_string(level='warn')
        self.assertIsNotNone(result)
        self.assertEqual(result, logging.WARN)

    def test_call_get_logging_level_from_string_with_debug(self):
        result = get_logging_level_from_string(level='debug')
        self.assertIsNotNone(result)
        self.assertEqual(result, logging.DEBUG)

    def test_call_get_logging_level_from_string_with_error(self):
        result = get_logging_level_from_string(level='error')
        self.assertIsNotNone(result)
        self.assertEqual(result, logging.ERROR)

    def test_call_get_logging_level_from_string_with_defaults(self):
        result = get_logging_level_from_string(level=None)
        self.assertIsNotNone(result)
        self.assertEqual(result, logging.INFO)

    
class TestExtractHandlerConfig(unittest.TestCase):    # pragma: no cover

    def setUp(self):
        self.extra_parameters = dict()
        self.extra_parameters['level'] = logging.INFO
        self.extra_parameters['format'] = '%(funcName)s:%(lineno)d -  %(levelname)s - %(message)s'

    def test_call_extract_handler_config_with_basic_extra_parameters(self):
        configuration = mock_get_file_contents(file='')
        result = extract_handler_config(
            handler_config=configuration['logging']['handlers'][0],
            handler_name='TimedRotatingFileHandler',
            extra_parameters=self.extra_parameters
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        for key in ('level', 'format', 'TimedRotatingFileHandler',):
            self.assertTrue(key in result, 'Key "{}" expected but not present'.format(key))
        for key in ('filename', 'when', 'interval', 'backupCount'):
            self.assertTrue(key in result['TimedRotatingFileHandler'], 'Key "{}" expected but not present'.format(key))

    def test_call_extract_handler_config_with_no_extra_parameters(self):
        configuration = mock_get_file_contents(file='')
        result = extract_handler_config(
            handler_config=configuration['logging']['handlers'][0],
            handler_name='TimedRotatingFileHandler',
            extra_parameters=dict()
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        for key in ('level', 'format', 'TimedRotatingFileHandler',):
            self.assertTrue(key in result, 'Key "{}" expected but not present'.format(key))
        for key in ('filename', 'when', 'interval', 'backupCount'):
            self.assertTrue(key in result['TimedRotatingFileHandler'], 'Key "{}" expected but not present'.format(key))
        

if __name__ == '__main__':
    unittest.main()
