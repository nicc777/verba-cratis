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
)->logging.FileHandler:
    try:
        h = logging.handlers.SysLogHandler(
            address=(
                host,
                port
            ),
            facility=LOG_USER,
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
):
    logger = logging.getLogger()
    for h in logger.handlers:
        logger.removeHandler(h)
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
        h = get_logging_datagram_handler(
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

