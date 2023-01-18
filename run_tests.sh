#!/bin/sh

# cd tests/

rm -frR ~/.verbacratis
rm -frR ./verbacratis.db
docker run --name echo_server -d -p 8089:80 kennethreitz/httpbin

# For the OpenAPI UI, visit http://localhost:8089/#/Anything/post_anything__anything_ when using the above docker image
# References: 
#   https://httpbin.org/#/Anything/post_anything__anything_
#   https://github.com/postmanlabs/httpbin

coverage run -a tests/test_notification_providers_init.py
coverage run -a tests/test_notification_providers_rest_init.py
# coverage run tests/test_utils_file_io.py
# coverage run -a tests/test_utils_parser.py
coverage run -a tests/test_utils_parser2.py
# coverage run -a tests/test_utils.py
coverage run -a tests/test_verbacratis.py
coverage run -a tests/test_verbacratis_init.py
# coverage run -a tests/test_models_runtime.py
# coverage run -a tests/test_aws.py
# coverage run -a tests/test_functions.py
# coverage run -a tests/test_functions_aws_helpers.py
# coverage run -a tests/test_utils_cli_arguments.py
# coverage run -a tests/test_utils_parse_config_file.py

coverage report --omit="tests/test*" -m

docker container stop echo_server
docker container rm echo_server
