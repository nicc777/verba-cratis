#!/bin/sh

# cd tests/

docker run --name echo_server -d -p 8089:80 kennethreitz/httpbin

# coverage run tests/test_utils_file_io.py
# coverage run -a tests/test_utils_parser.py
coverage run -a tests/test_utils_parser2.py
# coverage run -a tests/test_utils.py
# coverage run -a tests/test_verbacratis.py
# coverage run -a tests/test_models_runtime.py
# coverage run -a tests/test_aws.py
# coverage run -a tests/test_functions.py
# coverage run -a tests/test_functions_aws_helpers.py
# coverage run -a tests/test_utils_cli_arguments.py
# coverage run -a tests/test_utils_parse_config_file.py

coverage report --omit="tests/test*" -m

docker container stop echo_server
docker container rm echo_server
