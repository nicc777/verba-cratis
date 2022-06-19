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

This I still need to sort out:

* I may need a way to track where the variables are, as when they are processed into values, this values need to be placed in the string position. So, my thinking is to record also the start and end positions of the variable snippet and track that
* Inner variable snippets need to be extracted and processed (nested variables). Something to consider as how many levels of nesting should be sufficient? I'm leaning towards 3 or 4 levels for my particular use case for this project.


