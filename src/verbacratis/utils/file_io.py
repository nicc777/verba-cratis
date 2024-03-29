"""
    Copyright (c) 2022-2023. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/verbacratis/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

import traceback
import os
import shutil
import tempfile
from pathlib import Path
import re
from verbacratis.models import DEFAULT_CONFIG_DIR
import hashlib


class PathTypes:
    DIRECTORY = 1
    FILE = 2
    UNKNOWN = None


def get_file_contents(file: str)->str:
    content = ""
    with open(file, 'r') as f:
        content = f.read()
    return content


def write_content_to_file(file: str, content: str):
    with open(file, 'w') as f:
        f.write(content)


def append_content_to_file(file: str, content: str):
    with open(file, 'a') as f:
        f.write(content)


def does_file_exists(data_value)->bool:
    try:
        if os.path.exists(data_value) is True:
            return os.path.isfile(data_value)
    except:
        pass
    return False


def identify_local_path_type(path: str):
    try:
        if os.path.exists(path) is True:
            if os.path.isdir(path):
                return PathTypes.DIRECTORY
            if os.path.isfile(path):
                return PathTypes.FILE
    except:
        pass
    return PathTypes.UNKNOWN


def remove_tmp_dir_recursively(dir: str)->bool:
    try:
        os.remove(dir)
        return True
    except:
        traceback.print_exc()
    try:
        shutil.rmtree(dir)
        return True
    except:
        traceback.print_exc()
        return False


def create_tmp_dir(sub_dir: str)->str:
    tmp_dir = '{}{}{}'.format(tempfile.gettempdir(), os.sep, sub_dir)
    try:
        remove_tmp_dir_recursively(dir=tmp_dir)
        os.mkdir(tmp_dir)
    except:
        traceback.print_exc()
        return None
    return tmp_dir


def create_tmp_file(tmp_dir: str, file_name: str, data:str)->str:
    try:
        target_file = '{}{}{}'.format(tmp_dir, os.sep, file_name)
        with open(target_file, "w") as f:
            f.write('{}'.format(data))
    except:
        traceback.print_exc()
        return None
    return target_file


def copy_file(source_file: str, file_name: str, tmp_dir: str=None)->str:
    try:
        if tmp_dir is None:
            tmp_dir = create_tmp_dir(sub_dir=file_name)
        with open(source_file, "r") as fr:
            target_file = create_tmp_file(tmp_dir=tmp_dir, file_name=file_name, data=fr.read())
    except:
        traceback.print_exc()
        return None
    return target_file


def get_directory_from_path(input_path: str)->str:
    """Returns the directory portion of a path
    
    The function first tests if the path exists. If it does not exist, the assumption is that the path consists of a 
    directory and filename.

    If the path does exist, it will be determined if it is a directory or a normal file. Only the directory portion will
    be returned.

    Args:
        path: (required) String of a full path (directory and/or filename)

    Returns:
        A STRING with the calculated directory portion of the input path
    """
    p = Path(input_path)
    if p.exists() is True:
        if p.is_dir() is True:
            input_path = '{}{}dummy'.format(
                input_path,
                os.sep
            )
    elements = input_path.split(os.sep)
    if len(elements) > 0:
        elements.pop(0)
    if len(elements) == 1:
        return '/'
    final_path = '{}'.format(os.sep).join(elements[:-1])
    final_path = '{}{}'.format(
        os.sep,
        final_path
    )
    return final_path


def get_file_from_path(input_path: str)->str:
    """Returns the filename portion of a path
    
    The function first tests if the path exists. If it does exist, and it is found to be an existing directory, an 
    exception will be thrown

    Args:
            path: (required) String of a full path (directory and filename)

    Returns:
            A STRING with the calculated file name portion of the input path

    Raises:
        Exception: If the path exists but is found to be a directory
    """
    p = Path(input_path)
    if p.exists() is True:
        if p.is_dir() is True:
            raise Exception('Expected a file but got an existing directory when parsing "{}"'.format(input_path))
    elements = input_path.split(os.sep)
    file_name = elements[-1]
    return file_name


def expand_to_full_path(original_path: str)->str:
    if original_path.startswith(os.sep):
        return original_path
    return '{}{}{}'.format(
        os.getcwd(),
        os.sep,
        original_path
    )

def find_matching_files(start_dir:str, pattern: str='.*')->list:
    files_found = list()
    regex = re.compile(pattern)
    for root, dirs, files in os.walk(start_dir):
        for file in files:
            if regex.match(file):
                full_file_path = '{}{}{}'.format(root, os.sep, file)
                full_file_path = full_file_path.replace('{}{}'.format(os.sep, os.sep), '{}'.format(os.sep))
                files_found.append(full_file_path)
    return files_found


def init_application_dir(dir: str=DEFAULT_CONFIG_DIR)->str:
    if os.path.exists(dir):
        if os.path.isdir(dir):
            return dir
        else:
            raise Exception('Default application home directory "{}" is not a directory'.format(dir))
    os.makedirs(dir, exist_ok=True)


def file_checksum(path: str)->str:
    checksum = None
    with open(path, 'r') as f:
        checksum = hashlib.sha256(open(path,'rb').read()).hexdigest()
    return checksum
