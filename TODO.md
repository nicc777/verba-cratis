# Status at 2022-07-09

## Complete Unit Tests

Current coverage:

```text
Name                                 Stmts   Miss  Cover   Missing
------------------------------------------------------------------
src/acfop/__init__.py                    3      0   100%
src/acfop/acfop.py                      11      0   100%
src/acfop/aws/__init__.py                6      0   100%
src/acfop/functions/__init__.py         14      0   100%
src/acfop/functions/aws_helpers.py      18      0   100%
src/acfop/models/__init__.py             0      0   100%
src/acfop/models/runtime.py            230     10    96%   280, 288-298
src/acfop/utils/__init__.py            192      0   100%
src/acfop/utils/file_io.py              12      0   100%
src/acfop/utils/parser.py              106      0   100%
------------------------------------------------------------------
TOTAL                                  592     10    98%
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
* Add logic to process a snippet to return a value
* ~~Add unit tests for `src/acfop/models/runtime.py`~~
* Add command line arguments parsing - and add a command line argument for the location of the configuration file
* Process Variables in logging configuration strings, like `filename` (see example 1)


