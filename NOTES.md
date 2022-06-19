# Getting the collection of processing strings from a regular string

Very Basic Example:

```python
▶ python3
Python 3.8.10 (default, Mar 15 2022, 12:22:08) 
[GCC 9.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> s = "some string with a variable value ${var:var1} and a function that generated the following result: ${func:print_s()}"
>>> s
'some string with a variable value ${var:var1} and a function that generated the following result: ${func:print_s()}'
>>> import re
>>> re.findall(r'\$\{[\w|-]+\:[\w|\-|\s|\,|\=|\"|\'|\(|\)]+\}', s)
['${var:var1}', '${func:print_s()}']
```

Expanding on this idea, I started experimenting with some code in the file `scratch/processing_variables_in_strings.py` that yielded the following results:

```shell
$ python3 scratch/processing_variables_in_strings.py 
----------------------------------------------------------------------------------------------------------------------------------------------------------------
Experiment
        Processing: string: some string with a variable value ${var:var1} and a function that generated the following result: ${func:print_s()}
                snippet=var:var1
                snippet=func:print_s()


----------------------------------------------------------------------------------------------------------------------------------------------------------------
Experiment
        Processing: string: some string with a variable value ${var:var1} and a function that generated the following result: ${func:print_s(message=${var:var1})}
                snippet=var:var1
                snippet=func:print_s(message=${var:var1})
```
