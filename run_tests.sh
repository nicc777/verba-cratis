#!/bin/sh

coverage run tests/test_utils_file_io.py
coverage run -a tests/test_utils_parser.py
coverage run -a tests/test_utils.py
coverage run -a tests/test_acfop.py
coverage run -a tests/test_models_runtime.py

coverage report --omit="tests/test*" -m
