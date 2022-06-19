import re

variables = dict()
variables['var1'] = 'ABC'

def print_s(message: str=None)->str:
    if message is None:
        message = "some random string"
    return message.capitalize()


functions = dict()
functions['print_s'] = print_s

s1 = 'some string with a variable value ${var:var1} and a function that generated the following result: ${func:print_s()}'
# s1 = 'v ${var:var1} : ${func:print_s()}'
s2 = 'some string with a variable value ${var:var1} and a function that generated the following result: ${func:print_s(message=${var:var1})}'
# s2 = 'v ${var:var1} : ${func:print_s(message=${var:var1})}'

strings = list()
# strings.append(s1)
strings.append(s2)

for s in strings:
    print('-'*160)

    print('Experiment')
    print('\tProcessing: string: {}'.format(s))
    snippets = list()
    current_snippet = ""
    snippet_started = False
    close_bracket_skip_count = 0
    sub_snippet_counter = 0
    s_len = len(s)
    i = 0
    while(i < s_len):
        c = s[i]
        if snippet_started is False:
            if s[i] == '$' and i < s_len-2:
                if s[i+1] == '{':
                    snippet_started = True
                    i = i+2 # Skip the next character
            else:
                i = i+1
        else:
            if s[i] == '$' and i < s_len-2:
                if s[i+1] == '{':
                    close_bracket_skip_count += 1
                    current_snippet = '{}{}'.format(current_snippet, c)
            elif s[i] == '}' and close_bracket_skip_count == 0:
                snippet_started = False
                snippets.append(current_snippet)
                current_snippet = ""
            elif s[i] == '}' and close_bracket_skip_count > 0:
                close_bracket_skip_count -= 1
                current_snippet = '{}{}'.format(current_snippet, c)
            else:
                current_snippet = '{}{}'.format(current_snippet, c)
            i = i+1
    for snippet in snippets:
        print('\t\tsnippet={}'.format(snippet))

    print()
    print()
    

    

