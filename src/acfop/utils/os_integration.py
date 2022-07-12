"""
    Copyright (c) 2022. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/acfop/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""


import subprocess, shlex
import hashlib
import tempfile
import os
import os.path
import traceback
from acfop.utils import get_logger


def exec_shell_cmd(cmd: str, logger=get_logger()):
    td = tempfile.gettempdir()
    value_checksum = hashlib.sha256(str(cmd).encode(('utf-8'))).hexdigest()
    fn = '{}{}{}'.format(td, os.sep, value_checksum)
    logger.debug('Created temp file {}'.format(fn))
    with open(fn, 'w') as f:
        f.write(cmd)
    result = subprocess.run(['/bin/sh', fn], stdout=subprocess.PIPE).stdout.decode('utf-8')
    logger.info('[{}] Command: {}'.format(value_checksum, cmd))
    logger.info('[{}] Command Result: {}'.format(value_checksum, result))
    return result


def file_exists(file_path: str, logger=get_logger())->bool:
    logger.debug('Checking if file "{}" exists'.format(file_path))
    exists = False
    try:
        exists = os.path.isfile(file_path) 
    except:
        logger.error('EXCEPTION: {}'.format(traceback.format_exc()))
    logger.info('file "{}" exists: {}'.format(file_path, exists))
    return exists
