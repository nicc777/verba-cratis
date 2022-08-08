# Status at 2022-07-13

## Complete Unit Tests

Current coverage:

```text
Name                                   Stmts   Miss  Cover   Missing
--------------------------------------------------------------------
src/acfop/__init__.py                      3      0   100%
src/acfop/acfop.py                        20      0   100%
src/acfop/aws/__init__.py                  6      0   100%
src/acfop/functions/__init__.py           14      0   100%
src/acfop/functions/aws_helpers.py        18      0   100%
src/acfop/models/__init__.py               0      0   100%
src/acfop/models/runtime.py              230      6    97%   335, 348, 354, 358, 366-370
src/acfop/utils/__init__.py              192      0   100%
src/acfop/utils/cli_arguments.py          29      0   100%
src/acfop/utils/file_io.py                12      0   100%
src/acfop/utils/function_runner.py        50      0   100%
src/acfop/utils/os_integration.py         27      0   100%
src/acfop/utils/parse_config_file.py       9      0   100%
src/acfop/utils/parser.py                106      0   100%
--------------------------------------------------------------------
TOTAL                                    716      6    99%
```

## Other Tasks

Next Up tasks

* ~~Add Validation for Tasks~~
* ~~Add unit tests for task validation~~
* ~~Configure default logging~~
* ~~Create basic logging unit test with test handlers~~
* ~~Allow for logging override from configuration~~
* ~~Add unit tests for extract_handler_config() and get_logger_from_configuration()~~
* ~~Adapt existing get_logger_* functions to the passed in configuration (REFACTOR)~~
* ~~Create unique build UUID during init~~
* ~~Add logic to process a snippet to return a value~~
* ~~Add unit tests for `src/acfop/models/runtime.py`~~
* ~~Setup project for main entry point (command line utility called `acfop`)~~
* ~~Add docstring to `acfop.models.runtime` module~~
* ~~Add command line arguments parsing - and add a command line argument for the location of the configuration file~~
* Populate configuration template in variable store (classification='build-variable')
* Add logger to state_store and remove from functions receiving state_store as parameter (optimized function parameter list)
* Process Variables in logging configuration strings, like `filename` (see example 1)
* Calculate final values for `globalVariables`
* Add logic to search for local `.acfop` configuration file in absence of config file command line argument
* Add AWS profiles to support deployment to multiple accounts in one process

> Note: this list is not the complete task list. I try to look a couple of major features ahead at the moment as apposed to fully planning all the steps out up front, simply because the effort to do the latter is just to great nad there are some finer details I have yet to think about. As far as the example configuration goes - I thought about current manifests from several DevOps/SysOps tools and then thought about how something like what I want could look like. Therefore, the configuration examples may very well evolve as the application implementation progresses - and this has already happened.


