"""
    Copyright (c) 2022. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/acfop/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

import traceback


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

