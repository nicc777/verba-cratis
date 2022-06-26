#!/bin/sh

coverage run tests/test_utils_file_io.py
coverage run -a tests/test_utils_parser.py
coverage run -a tests/test_utils.py

coverage report --omit="tests/test*" -m
