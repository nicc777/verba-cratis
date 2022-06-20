"""
    Copyright (c) 2022. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/acfop/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

def variable_snippet_extract(line: str)->list:
    snippets = list()
    current_snippet = ""
    snippet_started = False
    close_bracket_skip_count = 0
    line_len = len(line)
    i = 0
    while(i < line_len):
        c = line[i]
        if snippet_started is False:
            if line[i] == '$' and i < line_len-2:
                if line[i+1] == '{':
                    snippet_started = True
                    i = i+2 # Skip the next character
            else:
                i = i+1
        else:
            if line[i] == '$' and i < line_len-2:
                if line[i+1] == '{':
                    close_bracket_skip_count += 1
                    current_snippet = '{}{}'.format(current_snippet, c)
            elif line[i] == '}' and close_bracket_skip_count == 0:
                snippet_started = False
                snippets.append(current_snippet)
                current_snippet = ""
            elif line[i] == '}' and close_bracket_skip_count > 0:
                close_bracket_skip_count -= 1
                current_snippet = '{}{}'.format(current_snippet, c)
            else:
                current_snippet = '{}{}'.format(current_snippet, c)
            i = i+1
    return snippets
