# Getting the collection of processing strings from a regular string

Example String (complex example, with nesting):

> some string with a variable value ${var:var1} and a function that generated the following result: ${func:print_s(message="${var:var1}")}

Expecting the following snippets:

* `${var:var1}`
* `${func:print_s(message="${var:var1}")}` which contains a nested snippet:
  * `${var:var1}` and this must be resolved first

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
                snippet=func:print_s(message="${var:var1}")
```

This I still need to sort out:

* I may need a way to track where the variables are, as when they are processed into values, this values need to be placed in the string position. So, my thinking is to record also the start and end positions of the variable snippet and track that
* Inner variable snippets need to be extracted and processed (nested variables). Something to consider as how many levels of nesting should be sufficient? I'm leaning towards 3 or 4 levels for my particular use case for this project.
* While processing, build up a table of function executions and set all their processing flags to false. After the string has been completely parsed (with all the nested variable snippets also extracted), this processing map can now be processed. However, since we have nesting, there is an hierarchy or order in which the processing need to happen. I'm leaning towards:
  * Process from LEFT to RIGHT in a string; then
  * Process from INNER-MOST nested snippet to OUTERMOST

Positioning Notes:

* String: `v ${var:var1} : ${func:print_s(message="${var:var1}")}` (positions are relative to this...)
  * Snippet 1: `${var:var1}`
    * START POS: 2
    * END POS: 12
  * Snippet 2a: `${func:print_s(message="${var:var1}")}`
    * START POS: 16
    * END POS: 53
  * Snippet 2b: `${var:var1}`
    * START POS: 40
    * END POS: 50

Therefor the processing map has to resemble something like the following:

```json
{
    "v ${var:var1} : ${func:print_s(message=${var:var1})}": [
        {
            "${var:var1}": {                                <-- EXECUTE FIRST
                "Checksum": "",
                "Processed": false,
                "ResultType": null,
                "ResultValue": null,
                "Children": [],
                "StartPos": 2,
                "EndPos": 12,
                "PlaceHolderVariable": "__A__XXXXX_"
            }
        },
        {
            "${func:print_s(message=\"${var:var1}\")}": {       <-- EXECUTE THIRD
                "Checksum": "",
                "Processed": false,
                "ResultType": null,
                "ResultValue": null,
                "Children": [                               <-- So basically children are processed first...
                    {
                        "${var:var1}": {                    <-- EXECUTE SECOND
                            "Checksum": "",
                            "Processed": false,
                            "ResultType": null,
                            "ResultValue": null,
                            "Children": [],
                            "StartPos": 40,
                            "EndPos": 50,
                            "PlaceHolderVariable": "__B__XXXXX_"
                        }
                    }
                ],
                "StartPos": 16,
                "EndPos": 53,
                "PlaceHolderVariable": "__C__XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX_"
            }
        }
    ]
}
```

A cache for processing can look something like this:

```json
{
    "checksum-for-${var:var1}": {
        "ResultType": "str",
        "ResultValue": "ABC",
    },
    "checksum-for-${func:print_s(message=\"${var:var1}\")}": {
        "ResultType": null,
        "ResultValue": null,
    }
}
```

In the above example, only the first one was resolved.