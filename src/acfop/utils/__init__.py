"""
    Copyright (c) 2022. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/acfop/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""


import traceback
import logging
import logging.handlers
import socket
import sys
import copy


DEFAULT_LOGGING_HANDLER_CONFIG = {  
    'StreamHandler': {
        'level': 'info',
        'format': '%(funcName)s:%(lineno)d -  %(levelname)s - %(message)s',
    },
    'FileHandler': {
        'filename': 'acfop.log',
        'level': 'info',
        'format': '%(funcName)s:%(lineno)d -  %(levelname)s - %(message)s',
    },
    'TimedRotatingFileHandler': {
        'filename': 'acfop.log',
        'when': 'D',
        'interval': '1',
        'backupCount': '5',
        'level': 'info',
        'format': '%(funcName)s:%(lineno)d -  %(levelname)s - %(message)s',
    },
    'DatagramHandler': {
        'hostname': 'localhost',
        'port': '514',
        'level': 'info',
        'format': '%(funcName)s:%(lineno)d -  %(levelname)s - %(message)s',
    },
    'SysLogHandler': {
        'hostname': 'localhost',
        'port': '514',
        'socktype': 'SOCK_DGRAM',
        'level': 'info',
        'format': '%(funcName)s:%(lineno)d -  %(levelname)s - %(message)s',
    },
}


def get_logging_file_handler(
    filename: str='acfop.log',
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
    filename: str='acfop.log',
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


def get_logger(
    level=logging.INFO,
    include_logging_file_handler: bool=False,
    include_logging_stream_handler: bool=True,
    include_logging_timed_rotating_file_handler: bool=False,
    include_logging_datagram_handler: bool=False,
    include_logging_syslog_handler: bool=False,
    extra_parameters: dict=dict()
)->logging.Logger:
    logger = logging.getLogger()
    logger.handlers = []
    formatter = logging.Formatter('%(funcName)s:%(lineno)d -  %(levelname)s - %(message)s')
    
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
    return logger


def extract_handler_config(handler_config: dict, handler_name: str, extra_parameters: dict=dict())->dict:
    adapted_extra_parameters = copy.deepcopy(extra_parameters)
    if 'level' not in extra_parameters:
        adapted_extra_parameters['level'] = 'info'
    if 'format' not in extra_parameters:
        adapted_extra_parameters['format'] = '%(funcName)s:%(lineno)d -  %(levelname)s - %(message)s'
    try:
        adapted_extra_parameters[handler_name] = copy.deepcopy(DEFAULT_LOGGING_HANDLER_CONFIG[handler_name])    # Get defaults...
        if 'parameters' in handler_config:
            for param_item in handler_config['parameters']:
                parameter_name = param_item['parameterName']
                if parameter_name in adapted_extra_parameters[handler_name]:
                    ptype = 'string'
                    if 'parameterType' in param_item:
                        ptype = param_item['parameterType']
                    value = 'not-set'
                    if ptype.lower().startswith('str') is True:
                        adapted_extra_parameters[handler_name][parameter_name] = '{}'.format(param_item['parameterValue'])
                    if ptype.lower().startswith('int') is True:
                        adapted_extra_parameters[handler_name][parameter_name] = int('{}'.format(param_item['parameterValue']))
                    if ptype == 'socket.SOCK_DGRAM':
                        adapted_extra_parameters[handler_name][parameter_name] = socket.SOCK_DGRAM
                    elif ptype == 'socket.SOCK_STREAM':
                        adapted_extra_parameters[handler_name][parameter_name] = socket.SOCK_STREAM
                    if ptype.lower().startswith('logging.'):
                        logging_type = ptype.lower().split('.')[1]
                        if logging_type == 'warn':
                            adapted_extra_parameters[handler_name][parameter_name] = logging.WARN
                        elif logging_type == 'info':
                            adapted_extra_parameters[handler_name][parameter_name] = logging.INFO
                        elif logging_type == 'error':
                            adapted_extra_parameters[handler_name][parameter_name] = logging.ERROR
                        elif logging_type == 'debug':
                            adapted_extra_parameters[handler_name][parameter_name] = logging.DEBUG
                        else:
                            adapted_extra_parameters[handler_name][parameter_name] = extra_parameters['level']
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
    if 'handlers' not in configuration:
        return get_logger()
    if isinstance(configuration['logging']['handlers'], list) is False:
        return get_logger()
    if len(configuration['logging']['handlers']) == 0:
        return get_logger()
    extra_parameters = dict()
    extra_parameters['level'] = logging.INFO
    extra_parameters['format'] = '%(funcName)s:%(lineno)d -  %(levelname)s - %(message)s'
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

