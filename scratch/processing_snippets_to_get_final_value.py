from copy import deepcopy

CURRENT_LINE = 0

def print_progress(msg: str):
    global CURRENT_LINE
    CURRENT_LINE += 1
    ln = str(CURRENT_LINE).zfill(3)
    print('{}: {}'.format(ln, msg))

line = ''
with open('scratch/template_line.txt', 'r') as f:
    line = f.read()
    line = line.strip()
print_progress('line={}'.format(line))

def extract_snippets(line: str):
    snippets = list()
    current_snippet = ""
    snippet_started = False
    close_bracket_skip_count = 0
    s_len = len(line)
    i = 0
    while(i < s_len):
        c = line[i]
        if snippet_started is False:
            if line[i] == '$' and i < s_len-2:
                if line[i+1] == '{':
                    snippet_started = True
                    i = i+2 # Skip the next character
            else:
                i = i+1
        else:
            if line[i] == '$' and i < s_len-2:
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


def templatize_str(input: str)->str:
    return '${}{}{}'.format('{',input,'}')


VALUES = {
    'func': {
        'round_up': '10',
        'sum': '20',
        'func_a': 'AAA',
    },
    'ref': {
        'aa': 'aaa',
        'bb': 'TEST',
        'cc': '9.9',
        'dd': '10',
    }
}


def get_snippet_processed_result(snippet: str)->str:
    result = ''

    print_progress('   get_snippet_processed_result(): snippet={}'.format(snippet))

    parts = snippet.split(':', 1)
    print_progress('   get_snippet_processed_result():    parts={}'.format(parts))

    variable_classification = parts[0]
    variable_value = parts[1]
    print_progress('   get_snippet_processed_result():    variable_classification={}   variable_value={}'.format(variable_classification, variable_value))

    print_progress('   get_snippet_processed_result():       Running a simulation of processing the variable and getting a result')
    classes = VALUES[variable_classification]
    for n, v in classes.items():
        if variable_value.startswith(n):
            result = v
    
    print_progress('   get_snippet_processed_result():    result={}'.format(result))

    return result


def process_line(line: str, snippets: list=list(), is_snippet: bool=False)->str:
    print_progress('process_line(): line={}   len(snippets)={}   is_snippet={}'.format(line, len(snippets), is_snippet))
    if len(snippets) == 0:
        snippets = extract_snippets(line=line)
    for snippet in snippets:
        snippet_result = process_line(line=snippet, is_snippet=True)
        snippet_template = templatize_str(input=snippet)
        print_progress('process_line():   Merging snippet "{}" calculated value "{}" back into original line "{}"'.format(snippet_template, snippet_result, line))
        line = line.replace(snippet_template, snippet_result)
    if is_snippet:
        print_progress('process_line():   Processing is_snippet "{}"'.format(line))
        line = get_snippet_processed_result(snippet=line)
    print_progress('process_line():   line={}'.format(line))
    return line


result = process_line(line=line)
print_progress('result={}'.format(result))
