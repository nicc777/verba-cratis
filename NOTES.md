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

