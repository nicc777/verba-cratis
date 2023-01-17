"""
    Copyright (c) 2022. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/verbacratis/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

import traceback
import os
import shutil
import tempfile
from pathlib import Path


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


def remove_tmp_dir_recursively(dir: str)->bool:
    try:
        os.remove(dir)
    except:
        traceback.print_exc()
    try:
        shutil.rmtree(dir)
        return True
    except:
        traceback.print_exc()
        return False


def create_tmp_dir(script_name: str)->str:
    tmp_dir = '{}{}{}'.format(tempfile.gettempdir(), os.sep, script_name)
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


def copy_file(source_file: str, tmp_dir: str, file_name: str)->str:
    try:
        data = ''
        with open(source_file, "r") as fr:
            data = fr.read()
        target_file = create_tmp_file(tmp_dir=create_tmp_dir(script_name=file_name), file_name=file_name, data=data)
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
            raise Exception('Expected a file but got an existing directory')
    elements = input_path.split(os.sep)
    file_name = elements[-1]
    return file_name
