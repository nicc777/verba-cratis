# Status at 2022-06-22

## Complete Unit Tests

Current coverage:

```text
Name                          Stmts   Miss  Cover   Missing
-----------------------------------------------------------
src/acfop/__init__.py             0      0   100%
src/acfop/utils/__init__.py     192     49    74%   273-276, 279-280, 286-342
src/acfop/utils/file_io.py       12      0   100%
src/acfop/utils/parser.py       105      0   100%
-----------------------------------------------------------
TOTAL                           309     49    84%
```

## Other Tasks

Next Up tasks

* ~~Add Validation for Tasks~~
* ~~Add unit tests for task validation~~
* ~~Configure default logging~~
* ~~Create basic logging unit test with test handlers~~
* ~~Allow for logging override from configuration~~
* Add unit tests for extract_handler_config() and get_logger_from_configuration()
* Adapt existing get_logger_* functions to the passed in configuration


