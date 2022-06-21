# Contributing Overview

Contributing at the moment is limited to opening new Issues or Pull Requests. There is only one primary reviewer at this stage, and turn-around times may be slow (a couple of days before a reaction should be considered normal).

# Implementation Principles and Guidelines

## Principle: Do not re-invent the wheel

As far as possible make use of third party libraries to fulfil various key functions. Logic in this application is around orchestration of CloudFormation deployment tasks with some additional complexity in that the orchestration must have some limited scripting support (template variables).

Thus far the following Libraries have been selected:

* [PyYAML](https://pyyaml.org/) for YAML parsing
* [Cerberus](https://docs.python-cerberus.org/en/stable/index.html) for configuration validation

# Source Code Guidelines

## Shell Scripts

All shell scripts must be compatible with BASH.

## Python

### Docstrings

Each Method containing more than half a dozen or so lines which involves several steps, should include a docstring (see [PEP 257](https://peps.python.org/pep-0257/)).

A general template for method docstrings are found below:

```python
def function_name(parameter1: str, parameter2: bool=False)->dict:
    """An example function

    This function only serves as an example for docstrings

    If ``parameter2`` is set to True, nothing special will happen

    Example return value:

    .. code-block:: python

        {
            'Result': True
        }

    Args:
        parameter1 (str): A required named parameter that should contain a string
        parameter2 (bool): An optional boolean parameter with a default value of False

    Returns:
        dict: After processing, results will be stored and returned in a dict

    """
    result = dict()
    if parameter2 is True:
        # Do some complex processing below when parameter2 is true
        pass
    # Do some more processing ...
    result['Result'] = True
    return result
```

More docstring references:

* https://peps.python.org/pep-0257/
* https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html
* https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
* https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-code-block
* https://github.com/docascode/sphinx-docfx-yaml/blob/master/docs/How_to_Document_Python_API.md

# Final Word

More contribution guidelines will follow in the near future.
