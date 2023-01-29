"""
    Copyright (c) 2022-2023. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/verbacratis/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""


import traceback
import logging
import logging.handlers
import socket
import sys
import copy
import os
from verbacratis.models import GenericLogger


DEFAULT_LOGGING_HANDLER_CONFIG = {  
    'StreamHandler': {
        'level': logging.INFO,
        'format': '%(funcName)s:%(lineno)d -  %(levelname)s - %(message)s',
    },
    'FileHandler': {
        'filename': 'verbacratis.log',
        'level': logging.INFO,
        'format': '%(funcName)s:%(lineno)d -  %(levelname)s - %(message)s',
    },
    'TimedRotatingFileHandler': {
        'filename': 'verbacratis.log',
        'when': 'D',
        'interval': 1,
        'backupCount': 5,
        'level': logging.INFO,
        'format': '%(funcName)s:%(lineno)d -  %(levelname)s - %(message)s',
    },
    'DatagramHandler': {
        'host': 'localhost',
        'port': '514',
        'level': logging.INFO,
        'format': '%(funcName)s:%(lineno)d -  %(levelname)s - %(message)s',
    },
    'SysLogHandler': {
        'host': 'localhost',
        'port': '514',
        'socktype': socket.SOCK_DGRAM,
        'level': logging.INFO,
        'format': '%(funcName)s:%(lineno)d -  %(levelname)s - %(message)s',
    },
}


def get_logging_file_handler(
    filename: str='verbacratis.log',
    level=logging.INFO,
    formatter: logging.Formatter=logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
)->logging.FileHandler:
    try:
        h = logging.FileHandler(filename=filename)
        h.setLevel(level)    
        h.setFormatter(formatter)
        return h
    except:
        traceback.print_exc()
    return None


def get_timed_rotating_file_handler(    # See: https://docs.python.org/3/library/logging.handlers.html#timedrotatingfilehandler
    filename: str='verbacratis.log',
    when: str='D',
    interval: int=1,
    backupCount: int= 5,
    level=logging.INFO,
    formatter: logging.Formatter=logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
)->logging.handlers.TimedRotatingFileHandler:
    try:
        h = logging.handlers.TimedRotatingFileHandler(filename=filename, when=when, interval=interval, backupCount=backupCount, utc=True)
        h.setLevel(level)    
        h.setFormatter(formatter)
        return h
    except:
        traceback.print_exc()
    return None


def get_logging_stream_handler(
    level=logging.INFO,
    formatter: logging.Formatter=logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
)->logging.StreamHandler:
    try:
        h = logging.StreamHandler(sys.stdout)
        h.setLevel(level)    
        h.setFormatter(formatter)
        return h
    except:
        traceback.print_exc()
    return None


def get_logging_datagram_handler(
    host: str='localhost',
    port: int=514,
    level=logging.INFO,
    formatter: logging.Formatter=logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
)->logging.handlers.DatagramHandler:
    try:
        h = logging.handlers.DatagramHandler(host=host, port=port)
        h.setLevel(level)    
        h.setFormatter(formatter)
        return h
    except:
        traceback.print_exc()
    return None


def get_logging_syslog_handler(
    host: str='localhost',
    port: int=514,
    socktype: object=socket.SOCK_DGRAM,
    level=logging.INFO,
    formatter: logging.Formatter=logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
)->logging.handlers.SysLogHandler:
    try:
        h = logging.handlers.SysLogHandler(
            address=(
                host,
                port
            ),
            facility='LOG_USER',
            socktype=socktype
        )
        h.setLevel(level)    
        h.setFormatter(formatter)
        return h
    except:
        traceback.print_exc()
    return None


def is_debug_set_in_environment()->bool:
    try:
        env_debug = os.getenv('DEBUG', '0').lower()
        if env_debug in ('1','true','t','enabled'):
            return True
    except:
        pass
    return False


def get_logger(
    level=logging.INFO,
    include_logging_file_handler: bool=False,
    include_logging_stream_handler: bool=True,
    include_logging_timed_rotating_file_handler: bool=False,
    include_logging_datagram_handler: bool=False,
    include_logging_syslog_handler: bool=False,
    extra_parameters: dict=dict(),
    log_format: str='%(funcName)s:%(lineno)d -  %(levelname)s - %(message)s'
)->logging.Logger:

    if is_debug_set_in_environment() is True:
        level = logging.DEBUG

    logger = logging.getLogger()
    logger.handlers = []
    formatter = logging.Formatter(log_format)
    
    qty_handlers_included = 0

    if include_logging_file_handler is True and 'filename' in extra_parameters:
        h = get_logging_file_handler(
            filename=extra_parameters['filename'],
            level=level,
            formatter=formatter
        )
        if h is not None:
            logger.addHandler(h)
            qty_handlers_included += 1

    if include_logging_stream_handler is True:
        h = get_logging_stream_handler(
            level=level,
            formatter=formatter
        )
        if h is not None:
            logger.addHandler(h)
            qty_handlers_included += 1

    if include_logging_timed_rotating_file_handler is True and 'filename' in extra_parameters:
        params = dict()
        params['filename'] = extra_parameters['filename']
        params['when'] = 'D'
        params['interval'] = 1
        params['backupCount'] = 5
        if 'when' in extra_parameters:
            params['when'] = extra_parameters['when']
        if 'interval' in extra_parameters:
            params['interval'] = extra_parameters['interval']
        if 'backupCount' in extra_parameters:
            params['backupCount'] = extra_parameters['backupCount']
        h = get_timed_rotating_file_handler(    # See: https://docs.python.org/3/library/logging.handlers.html#timedrotatingfilehandler
            filename=params['filename'],
            when=params['when'],
            interval=params['interval'],
            backupCount=params['backupCount'],
            level=level,
            formatter=formatter
        )
        if h is not None:
            logger.addHandler(h)
            qty_handlers_included += 1

    if include_logging_datagram_handler is True and 'host' in extra_parameters and 'port' in extra_parameters:
        h = get_logging_datagram_handler(
            host=extra_parameters['host'],
            port=extra_parameters['port'],
            level=level,
            formatter=formatter
        )
        if h is not None:
            logger.addHandler(h)
            qty_handlers_included += 1

    if include_logging_syslog_handler is True and 'host' in extra_parameters and 'port' in extra_parameters:
        socktype = socket.SOCK_DGRAM
        if 'socktype' in extra_parameters:
            socktype = extra_parameters['socktype']
        h = get_logging_syslog_handler(
            host=extra_parameters['host'],
            port=extra_parameters['port'],
            socktype=socktype,
            level=level,
            formatter=formatter
        )
        if h is not None:
            logger.addHandler(h)
            qty_handlers_included += 1

    if qty_handlers_included == 0:
        logger.addHandler(get_logging_stream_handler())
    
    logger.setLevel(level)
    return GenericLogger(logger=logger)


def get_logging_level_from_string(level: str):
    try:
        accepted_levels = ('warn', 'info', 'error', 'debug')
        working_level = level
        if level.lower().startswith('logging.'):
            working_level = level.lower().split('.')[1]
        if working_level in accepted_levels:
            if working_level.startswith('warn'):
                return logging.WARN
            if working_level.startswith('info'):
                return logging.INFO
            if working_level.startswith('err'):
                return logging.ERROR
            if working_level.startswith('deb'):
                return logging.DEBUG
    except:
        traceback.print_exc()
    return logging.INFO


def extract_handler_config(handler_config: dict, handler_name: str, extra_parameters: dict=dict())->dict:
    adapted_extra_parameters = copy.deepcopy(extra_parameters)
    if 'level' not in extra_parameters:
        adapted_extra_parameters['level'] = get_logging_level_from_string(level='info')
    else:
        adapted_extra_parameters['level'] = get_logging_level_from_string(level=extra_parameters['level'])
    if 'format' not in extra_parameters:
        adapted_extra_parameters['format'] = '%(funcName)s:%(lineno)d -  %(levelname)s - %(message)s'
    else:
        adapted_extra_parameters['format'] = extra_parameters['format']
    try:
        adapted_extra_parameters[handler_name] = copy.deepcopy(DEFAULT_LOGGING_HANDLER_CONFIG[handler_name])    # Get defaults...
        if 'parameters' in handler_config:
            for param_item in handler_config['parameters']:
                if 'parameterName' in param_item and 'parameterValue' in param_item and 'parameterType' in param_item:
                    parameter_name = param_item['parameterName']
                    parameter_value = param_item['parameterValue']
                    parameter_type = param_item['parameterType']
                    if parameter_name in adapted_extra_parameters[handler_name] and parameter_name != 'level':
                        if parameter_type.lower().startswith('str') is True:
                            adapted_extra_parameters[handler_name][parameter_name] = '{}'.format(parameter_value)
                        elif parameter_type.lower().startswith('int') is True:
                            adapted_extra_parameters[handler_name][parameter_name] = int('{}'.format(parameter_value))
                        elif parameter_type == 'socket.SOCK_DGRAM':
                            adapted_extra_parameters[handler_name][parameter_name] = socket.SOCK_DGRAM
                        elif parameter_type == 'socket.SOCK_STREAM':
                            adapted_extra_parameters[handler_name][parameter_name] = socket.SOCK_STREAM
                    if parameter_name in adapted_extra_parameters[handler_name] and parameter_name == 'level':
                        adapted_extra_parameters[handler_name][parameter_name] = get_logging_level_from_string(level=parameter_value)
    except:
        traceback.print_exc()
    return adapted_extra_parameters



def get_logger_from_configuration(configuration: dict)->logging.Logger:
    if configuration is None:
        return get_logger()
    if isinstance(configuration, dict) is False:
        return get_logger()
    if 'logging' not in configuration:
        return get_logger()
    if 'handlers' not in configuration['logging']:
        return get_logger()
    if isinstance(configuration['logging']['handlers'], list) is False:
        return get_logger()
    if len(configuration['logging']['handlers']) == 0:
        return get_logger()
    extra_parameters = dict()
    extra_parameters['level'] = 'info'
    extra_parameters['format'] = '%(funcName)s:%(lineno)d -  %(levelname)s - %(message)s'
    if 'level' in configuration['logging']:
        extra_parameters['level'] = configuration['logging']['level']
    if 'format' in configuration['logging']:
        extra_parameters['level'] = configuration['logging']['format']
    include_logging_file_handler=False
    include_logging_stream_handler=False
    include_logging_timed_rotating_file_handler=False
    include_logging_datagram_handler=False
    include_logging_syslog_handler=False
    for handler_config in configuration['logging']['handlers']:
        if 'name' in handler_config:
            if handler_config['name'] in ('StreamHandler', 'FileHandler', 'TimedRotatingFileHandler', 'DatagramHandler', 'SysLogHandler'):
                
                if handler_config['name'] == 'StreamHandler':
                    include_logging_stream_handler = True
                if handler_config['name'] == 'FileHandler':
                    include_logging_file_handler = True
                if handler_config['name'] == 'TimedRotatingFileHandler':
                    include_logging_timed_rotating_file_handler = True
                if handler_config['name'] == 'DatagramHandler':
                    include_logging_datagram_handler = True
                if handler_config['name'] == 'SysLogHandler':
                    include_logging_syslog_handler = True

                extra_parameters[handler_config['name']] = extract_handler_config(
                    handler_config=handler_config,
                    handler_name=handler_config['name'],
                    extra_parameters=extra_parameters
                )
    try:
        get_logger(
            level=extra_parameters['level'],
            include_logging_file_handler=include_logging_file_handler,
            include_logging_stream_handler=include_logging_stream_handler,
            include_logging_timed_rotating_file_handler=include_logging_timed_rotating_file_handler,
            include_logging_datagram_handler=include_logging_datagram_handler,
            include_logging_syslog_handler=include_logging_syslog_handler,
            extra_parameters=extra_parameters
        )
    except:
        traceback.print_exc()
        return get_logger()

