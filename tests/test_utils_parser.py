"""
    Copyright (c) 2022. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/acfop/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")
print('sys.path={}'.format(sys.path))

import unittest


from acfop.utils.parser import *


def mock_get_file_contents(file: str)->str: # pragma: no cover
    config = ""
    with open('examples/example_01/example_01.yaml', 'r') as f:
      config = f.read()
    return config


def mock_get_file_contents_throws_exception(file: str)->str:
    raise Exception('File Not Found')


class TestFunctionVariableSnippetExtract(unittest.TestCase):    # pragma: no cover

    def test_string_with_no_variables(self):
        line = 'hello world!'
        result = variable_snippet_extract(line=line)
        self.assertTrue(len(result) == 0)

    def test_string_with_one_variable(self):
        line = 'XXX ${var:var1} XXX'
        result = variable_snippet_extract(line=line)
        self.assertTrue(len(result) == 1)
        self.assertEqual('var:var1', result[0])

    def test_string_with_two_variables(self):
        line = 'XXX ${var:var1} XXX ${func:print_s()} XXX'
        result = variable_snippet_extract(line=line)
        self.assertTrue(len(result) == 2)
        self.assertEqual('var:var1', result[0])
        self.assertEqual('func:print_s()', result[1])

    def test_string_with_two_variables_including_nested_variable(self):
        """
            NOTE: Even in the case of nested variables, still only the first level variables are extracted.
        """
        line = 'XXX ${var:var1} XXX ${func:print_s(message="${var:var1}")} XXX'
        result = variable_snippet_extract(line=line)
        self.assertTrue(len(result) == 2)
        self.assertEqual('var:var1', result[0])
        self.assertEqual('func:print_s(message="${var:var1}")', result[1])
        result2 = variable_snippet_extract(line=result[1])
        self.assertTrue(len(result2) == 1)
        self.assertEqual('var:var1', result2[0])


class TestFunctionParseConfigurationFile(unittest.TestCase):    # pragma: no cover

    def test_parse_configuration_file_example1(self):
        configuration = parse_configuration_file(file_path='/path/to/configuration', get_file_contents_function=mock_get_file_contents)
        self.assertIsNotNone(configuration)
        self.assertIsInstance(configuration, dict)
        self.assertTrue(len(configuration) > 0)
        keys = (
            'deployments',
            'functionParameterValues',
            'globalVariables',
            'logging',
            'tasks',
        )
        for key in keys:
            self.assertTrue(key in configuration, 'Key "{}" not found in configuration'.format(key))

    def test_parse_configuration_file_example1_file_not_found(self):
        configuration = dict()
        with self.assertRaises(Exception) as context:
            configuration = parse_configuration_file(file_path='/path/to/configuration', get_file_contents_function=mock_get_file_contents_throws_exception)
        self.assertTrue('Failed to parse configuration' in str(context.exception))
        self.assertEqual(len(configuration), 0)


class TestFunctionValidateConfiguration(unittest.TestCase):    # pragma: no cover

    def test_validate_example1(self):
        configuration = parse_configuration_file(file_path='/path/to/configuration', get_file_contents_function=mock_get_file_contents)
        result = validate_configuration(configuration=configuration)
        self.assertIsInstance(result, bool)
        self.assertTrue(result)

    def test_failed_validation(self):
        configuration = {'Message': 'This config is invalid'}
        result = validate_configuration(configuration=configuration)
        self.assertIsInstance(result, bool)
        self.assertFalse(result)

    def test_force_exception_with_failed_validation_result(self):
        configuration = 123
        result = validate_configuration(configuration=configuration)
        self.assertIsInstance(result, bool)
        self.assertFalse(result)

    def test_force_deployment_schema_validation_failure(self):
        configuration = {
            'deployments': [
                {
                    'name': 'this_name_is_valid',
                    'incorrectParameter': 123,
                }
            ],
            "tasks": [
                {
                    "name": "dynamoDbTable",
                    "template": "examples/example_01/cloudformation/dynamodb_table.yaml",
                    "deployFromS3": True,
                    "stackName": "example-01-001",
                    "templateParameters": [
                        {
                          "ParameterName": "TableName",
                          "ParameterValue": "acfop-test-table"
                        }
                    ],
                    "changeSetIfExists": True,
                    "preDeploymentScript": "echo \"Starting on task ${build-variable:current_task_name}\"\n",
                    "postDeploymentScript": "python3 examples/example_01/scripts/create_sample_datafor_dynamodb_table.py\nsleep 60\necho \"Successfully deployed template ${ref:tasks.dynamoDbTable.template} with ${exports:dynamoDbTable.initialRecordCount} initial records\"\n",
                    "taskDependsOn": "None",
                    "taskExports": {
                        "tableArn": "${shell:aws dynamodb describe-table --table-name acfop-test-table | jq '.Table.TableArn'}",
                        "initialRecordCount": "${shell:aws dynamodb scan --table-name messaging --select \"COUNT\" | jq '.Count'}"
                    }
                },
                {
                    "name": "lambdaFunction",
                    "template": "examples/example_01/cloudformation/lambda_function.yaml",
                    "deployFromS3": True,
                    "stackName": "example-01-002",
                    "functionParameterValuesOverrides": {
                        "get_username": [
                            {
                              "ParameterName": "convert_case",
                              "ParameterValueType": "str",
                              "ParameterValue": "LOWER"
                            }
                        ]
                    },
                    "templateParameters": [
                        {
                            "ParameterName": "FunctionName",
                            "ParameterValue": "acfop-example-01-${func:get_username()}"
                        },
                        {
                            "ParameterName": "FunctionZipFile",
                            "ParameterValue": "${ref:globalVariables.cloudFormationS3Bucket}/example-01-lambda.zip"
                        },
                        {
                            "ParameterName": "DeploymentVersion",
                            "ParameterValue": "${build-variable:build_uuid}"
                        },
                        {
                            "ParameterName": "TableArn",
                            "ParameterValue": "${exports:dynamoDbTable.tableArn}"
                        }
                    ],
                    "changeSetIfExists": True,
                    "preDeploymentScript": "export AWS_DEFAULT_REGION=${ref:globalVariables.awsRegion}\necho \"Starting on task ${build-variable:current_task_name}\"\nexamples/example_01/lambda_function_src/build_and_package.sh --output_file=\"/tmp/example-01-lambda.zip\"\naws s3 cp /tmp/example-01-lambda.zip s3://${ref:globalVariables.cloudFormationS3Bucket}/example-01-lambda.zip\n",
                    "postDeploymentScript": "python3 examples/example_01/scripts/create_sample_datafor_dynamodb_table.py\necho \"Successfully deployed template ${ref:tasks.dynamoDbTable.template} with initial record count set to ${exports:dynamoDbTable.initialRecordCount}. Task completed at ${exports:lambdaFunction.finalFinishTimestamp}\"\n",
                    "taskDependsOn": "dynamoDbTable",
                    "taskExports": {
                        "finalFinishTimestamp": "${shell:date}"
                    }
                }
            ]
        }
        result = validate_configuration(configuration=configuration)
        self.assertIsInstance(result, bool)
        self.assertFalse(result)

    def test_force_deployment_task_name_failure(self):
        configuration = {
            "deployments": [
                {
                    "name": "sandbox-full-live",
                    "unitTestProfile": False,
                    "tasks": [
                        "lambdaFunction",
                        "nonExistingTask"
                    ],
                    "globalVariableOverrides": {
                        "logFilename": "deployment-${build-variable:build_uuid}-testing.log",
                        "logLevel": "debug"
                    },
                    "templateParametersOverrides": {
                        "tableName": "acfop-test-001-table"
                    },
                    "dependsOnProfile": [
                        "None"
                    ],
                    "preDeploymentScript": "echo \"Running unit tests on deployment ${build-variable:current_deployment_name}\"\n",
                    "postDeploymentScript": "echo \"Successfully completed unit tests for deployment ${build-variable:current_deployment_name}\"\n"
                }
            ],
            "tasks": [
                {
                    "name": "dynamoDbTable",
                    "template": "examples/example_01/cloudformation/dynamodb_table.yaml",
                    "deployFromS3": True,
                    "stackName": "example-01-001",
                    "templateParameters": [
                        {
                          "ParameterName": "TableName",
                          "ParameterValue": "acfop-test-table"
                        }
                    ],
                    "changeSetIfExists": True,
                    "preDeploymentScript": "echo \"Starting on task ${build-variable:current_task_name}\"\n",
                    "postDeploymentScript": "python3 examples/example_01/scripts/create_sample_datafor_dynamodb_table.py\nsleep 60\necho \"Successfully deployed template ${ref:tasks.dynamoDbTable.template} with ${exports:dynamoDbTable.initialRecordCount} initial records\"\n",
                    "taskDependsOn": "None",
                    "taskExports": {
                        "tableArn": "${shell:aws dynamodb describe-table --table-name acfop-test-table | jq '.Table.TableArn'}",
                        "initialRecordCount": "${shell:aws dynamodb scan --table-name messaging --select \"COUNT\" | jq '.Count'}"
                    }
                },
                {
                    "name": "lambdaFunction",
                    "template": "examples/example_01/cloudformation/lambda_function.yaml",
                    "deployFromS3": True,
                    "stackName": "example-01-002",
                    "functionParameterValuesOverrides": {
                        "get_username": [
                            {
                              "ParameterName": "convert_case",
                              "ParameterValueType": "str",
                              "ParameterValue": "LOWER"
                            }
                        ]
                    },
                    "templateParameters": [
                        {
                            "ParameterName": "FunctionName",
                            "ParameterValue": "acfop-example-01-${func:get_username()}"
                        },
                        {
                            "ParameterName": "FunctionZipFile",
                            "ParameterValue": "${ref:globalVariables.cloudFormationS3Bucket}/example-01-lambda.zip"
                        },
                        {
                            "ParameterName": "DeploymentVersion",
                            "ParameterValue": "${build-variable:build_uuid}"
                        },
                        {
                            "ParameterName": "TableArn",
                            "ParameterValue": "${exports:dynamoDbTable.tableArn}"
                        }
                    ],
                    "changeSetIfExists": True,
                    "preDeploymentScript": "export AWS_DEFAULT_REGION=${ref:globalVariables.awsRegion}\necho \"Starting on task ${build-variable:current_task_name}\"\nexamples/example_01/lambda_function_src/build_and_package.sh --output_file=\"/tmp/example-01-lambda.zip\"\naws s3 cp /tmp/example-01-lambda.zip s3://${ref:globalVariables.cloudFormationS3Bucket}/example-01-lambda.zip\n",
                    "postDeploymentScript": "python3 examples/example_01/scripts/create_sample_datafor_dynamodb_table.py\necho \"Successfully deployed template ${ref:tasks.dynamoDbTable.template} with initial record count set to ${exports:dynamoDbTable.initialRecordCount}. Task completed at ${exports:lambdaFunction.finalFinishTimestamp}\"\n",
                    "taskDependsOn": "dynamoDbTable",
                    "taskExports": {
                        "finalFinishTimestamp": "${shell:date}"
                    }
                }
            ]
        }
        result = validate_configuration(configuration=configuration)
        self.assertIsInstance(result, bool)
        self.assertFalse(result)


class TestFunctionFromConfigurationGetAllTaskNamesAsList(unittest.TestCase):    # pragma: no cover

    def test_validate_example1(self):
        configuration = parse_configuration_file(file_path='/path/to/configuration', get_file_contents_function=mock_get_file_contents)
        task_names = from_configuration_get_all_task_names_as_list(configuration=configuration)
        self.assertIsInstance(task_names, list)
        self.assertTrue(len(task_names), 2)
        self.assertTrue('dynamoDbTable' in task_names)
        self.assertTrue('lambdaFunction' in task_names)

    def test_force_Exception(self):
        task_names = from_configuration_get_all_task_names_as_list(configuration=123)
        self.assertIsInstance(task_names, list)
        self.assertEqual(len(task_names), 0)


if __name__ == '__main__':
    unittest.main()
