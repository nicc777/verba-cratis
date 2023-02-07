#!/bin/sh

# cd tests/

rm -frR ~/.verbacratis
rm -frR ./verbacratis.db
rm -frR reports
mkdir reports


docker container stop echo_server
docker container rm echo_server
docker run --name echo_server -d -p 8089:80 kennethreitz/httpbin

# For SSHD Access Testing - password based access - root password: root (see: https://hub.docker.com/r/rastasheep/ubuntu-sshd/#!)
docker container stop test_sshd
docker container rm test_sshd
docker run -d -p 8022:22 --name test_sshd rastasheep/ubuntu-sshd

# For the OpenAPI UI, visit http://localhost:8089/#/Anything/post_anything__anything_ when using the above docker image
# References: 
#   https://httpbin.org/#/Anything/post_anything__anything_
#   https://github.com/postmanlabs/httpbin

echo ; echo ; echo "########################################################################################################################"
coverage run -a tests/test_notification_providers_init.py

echo ; echo ; echo "########################################################################################################################"
coverage run -a tests/test_notification_providers_rest_init.py

echo ; echo ; echo "########################################################################################################################"
coverage run -a tests/test_models_ordering.py

echo ; echo ; echo "########################################################################################################################"
coverage run -a tests/test_models_runtime_configuration.py

echo ; echo ; echo "########################################################################################################################"
coverage run -a tests/test_models_systems_configuration.py

echo ; echo ; echo "########################################################################################################################"
coverage run -a tests/test_models_deployments_configuration.py

echo ; echo ; echo "########################################################################################################################"
coverage run -a tests/test_utils_parser2.py

echo ; echo ; echo "########################################################################################################################"
coverage run -a tests/test_verbacratis.py

echo ; echo ; echo "########################################################################################################################"
coverage run -a tests/test_utils_cli_arguments.py

echo ; echo ; echo "########################################################################################################################"
coverage run -a tests/test_utils_git_integration.py

echo ; echo ; echo "########################################################################################################################"
coverage run -a tests/test_utils_http_requests_io.py

echo ; echo ; echo "########################################################################################################################"
coverage report --omit="tests/test*" -m
coverage html -d reports --omit="tests/test*"
echo "Report available in file://$PWD/reports/index.html"


# coverage run -a tests/test_utils_parse_config_file.py
# coverage run -a tests/test_verbacratis_init.py
# coverage run -a tests/test_models_runtime.py
# coverage run -a tests/test_aws.py
# coverage run -a tests/test_functions.py
# coverage run -a tests/test_functions_aws_helpers.py
# coverage run tests/test_utils_file_io.py
# coverage run -a tests/test_utils_parser.py
# coverage run -a tests/test_utils.py

docker container stop echo_server
docker container rm echo_server

docker container stop test_sshd
docker container rm test_sshd
