"""
    Copyright (c) 2022. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/acfop/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

import traceback
import os
import shutil
import tempfile


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
