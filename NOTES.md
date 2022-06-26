# Getting the collection of processing strings from a regular string

Example String (complex example, with nesting):

> some string with a variable value ${var:var1} and a function that generated the following result: ${func:print_s(message="${var:var1}")}

Expecting the following snippets:

* `${var:var1}`
* `${func:print_s(message="${var:var1}")}` which contains a nested snippet:
  * `${var:var1}` and this must be resolved first

Very Basic Example:

```python
▶ python3
Python 3.8.10 (default, Mar 15 2022, 12:22:08) 
[GCC 9.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> s = "some string with a variable value ${var:var1} and a function that generated the following result: ${func:print_s()}"
>>> s
'some string with a variable value ${var:var1} and a function that generated the following result: ${func:print_s()}'
>>> import re
>>> re.findall(r'\$\{[\w|-]+\:[\w|\-|\s|\,|\=|\"|\'|\(|\)]+\}', s)
['${var:var1}', '${func:print_s()}']
```

Expanding on this idea, I started experimenting with some code in the file `scratch/processing_variables_in_strings.py` that yielded the following results:

```shell
$ python3 scratch/processing_variables_in_strings.py 
----------------------------------------------------------------------------------------------------------------------------------------------------------------
Experiment
        Processing: string: some string with a variable value ${var:var1} and a function that generated the following result: ${func:print_s()}
                snippet=var:var1
                snippet=func:print_s()


----------------------------------------------------------------------------------------------------------------------------------------------------------------
Experiment
        Processing: string: some string with a variable value ${var:var1} and a function that generated the following result: ${func:print_s(message=${var:var1})}
                snippet=var:var1
                snippet=func:print_s(message="${var:var1}")
```

This I still need to sort out:

* I may need a way to track where the variables are, as when they are processed into values, this values need to be placed in the string position. So, my thinking is to record also the start and end positions of the variable snippet and track that
* Inner variable snippets need to be extracted and processed (nested variables). Something to consider as how many levels of nesting should be sufficient? I'm leaning towards 3 or 4 levels for my particular use case for this project.
* While processing, build up a table of function executions and set all their processing flags to false. After the string has been completely parsed (with all the nested variable snippets also extracted), this processing map can now be processed. However, since we have nesting, there is an hierarchy or order in which the processing need to happen. I'm leaning towards:
  * Process from LEFT to RIGHT in a string; then
  * Process from INNER-MOST nested snippet to OUTERMOST

Positioning Notes:

* String: `v ${var:var1} : ${func:print_s(message="${var:var1}")}` (positions are relative to this...)
  * Snippet 1: `${var:var1}`
    * START POS: 2
    * END POS: 12
  * Snippet 2a: `${func:print_s(message="${var:var1}")}`
    * START POS: 16
    * END POS: 53
  * Snippet 2b: `${var:var1}`
    * START POS: 40
    * END POS: 50

Therefor the processing map has to resemble something like the following:

```json
{
    "v ${var:var1} : ${func:print_s(message=${var:var1})}": [
        {
            "${var:var1}": {                                <-- EXECUTE FIRST
                "Class": "var",
                "ClassReference": "var1",
                "Parameters": null,
                "Checksum": "",
                "Processed": false,
                "ResultType": null,
                "ResultValue": null,
                "Children": [],
                "StartPos": 2,
                "EndPos": 12,
                "PlaceHolderVariable": "__A__XXXXX_"
            }
        },
        {
            "${func:print_s(message=\"${var:var1}\")}": {   <-- EXECUTE THIRD
                "Class": "func",
                "ClassReference": "print_s",
                "Parameters": [                             <-- Functions can have parameters...
                    {
                        "ParameterName": "message", 
                        "ParameterValue": "${var:var1}"     <-- TODO Still need to figure out how I'm going to deal with this, 
                                                             -- especially when the string contains one or more template variables 
                                                             -- or contains a string with embedded template variables.
                                                             -- And how do I get the calculated values back in?
                    }
                ],
                "Checksum": "",
                "Processed": false,
                "ResultType": null,
                "ResultValue": null,
                "Children": [                               <-- So basically children are processed first...
                    {
                        "${var:var1}": {                    <-- EXECUTE SECOND
                            "Class": "var",
                            "ClassReference": "var1",
                            "Parameters": null,
                            "Checksum": "",
                            "Processed": false,
                            "ResultType": null,
                            "ResultValue": null,
                            "Children": [],
                            "StartPos": 40,
                            "EndPos": 50,
                            "PlaceHolderVariable": "__B__XXXXX_"
                        }
                    }
                ],
                "StartPos": 16,
                "EndPos": 53,
                "PlaceHolderVariable": "__C__XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX_"
            }
        }
    ]
}
```

A cache for processing can look something like this:

```json
{
    "checksum-for-${var:var1}": {
        "ResultType": "str",
        "ResultValue": "ABC",
    },
    "checksum-for-${func:print_s(message=\"${var:var1}\")}": {
        "ResultType": null,
        "ResultValue": null,
    }
}
```

In the above example, only the first one was resolved.

# Docstrings

References:

* https://peps.python.org/pep-0257/
* https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html
* https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
* https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-code-block
* https://github.com/docascode/sphinx-docfx-yaml/blob/master/docs/How_to_Document_Python_API.md

# Validation with Cerberus

Rules Documentation: https://docs.python-cerberus.org/en/stable/validation-rules.html

At the moment I am rethinking the configuration schema to make parsing with cerberus a little easier and straightforward.

Breaking up schema validation in smaller sections - basically a validation schema per "level". This should allow changes in any section of the schema to be a little easier with less impact on testing and other code bits.

# Current Configuration Example in JSON:

Configuration:

```json
{
  "deployments": [
    {
      "name": "sandbox-full-live",
      "unitTestProfile": false,
      "tasks": [
        "lambdaFunction"
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
      "preDeploymentScript": "echo \"Running unit tests on deployment ${build-variable:current_deployment_name}\"\necho \"You can also perform other tasks here such as AWS EKS kubectl config download, AWS ECR login (required for pushing container images) etc.\"\n",
      "postDeploymentScript": "echo \"Successfully completed unit tests for deployment ${build-variable:current_deployment_name}\"\n",
      "deployFromS3": {
        "bucketName": "my-deployments"
      }
    }
  ],
  "functionParameterValues": [
    {
      "name": "get_username",
      "parameters": [
        {
          "name": "convert_case",
          "type": "str",
          "value": "UPPER"
        }
      ]
    }
  ],
  "globalVariables": {
    "awsRegion": "eu-central-1",
    "awsAccountId": "${env:AWS_REGION}"
  },
  "logging": {
    "filename": "deployment-${build-variable:build_uuid}.log",
    "level": "warn",
    "handlers": [
      {
        "name": "TimedRotatingFileHandler",
        "parameters": [
          {
            "parameterName": "filename",
            "parameterType": "string",
            "parameterValue": "out.log"
          },
          {
            "parameterName": "when",
            "parameterType": "string",
            "parameterValue": "H"
          },
          {
            "parameterName": "interval",
            "parameterType": "int",
            "parameterValue": 6
          },
          {
            "parameterName": "backupCount",
            "parameterType": "int",
            "parameterValue": 120
          }
        ]
      },
      {
        "name": "StreamHandler"
      }
    ],
    "format": "%(asctime)s %(levelname)s - %(filename)s %(funcName)s:%(lineno)d %(message)s"
  },
  "tasks": [
    {
      "name": "dynamoDbTable",
      "template": {
        "sourceFile": "examples/example_01/cloudformation/dynamodb_table.yaml",
        "stackName": "example-01-001"
      },
      "templateParameters": [
        {
          "ParameterName": "TableName",
          "ParameterValue": "acfop-test-table"
        }
      ],
      "changeSetIfExists": true,
      "preDeploymentScript": "echo \"Starting on task ${build-variable:current_task_name}\"\n",
      "postDeploymentScript": "python3 examples/example_01/scripts/create_sample_datafor_dynamodb_table.py\nsleep 60\necho \"Successfully deployed template ${ref:tasks.dynamoDbTable.template} with ${exports:dynamoDbTable.initialRecordCount} initial records\"\n",
      "taskExports": [
        {
          "ExportName": "tableArn",
          "ExportValue": "${shell:aws dynamodb describe-table --table-name acfop-test-table | jq '.Table.TableArn'}"
        },
        {
          "ExportName": "initialRecordCount",
          "ExportValue": "${shell:aws dynamodb scan --table-name messaging --select \"COUNT\" | jq '.Count'}"
        }
      ]
    },
    {
      "name": "lambdaFunction",
      "template": {
        "sourceFile": "examples/example_01/cloudformation/lambda_function.yaml",
        "stackName": "example-01-002"
      },
      "functionParameterValuesOverrides": [
        {
          "FunctionName": "get_username",
          "ParameterName": "convert_case",
          "ParameterValueType": "str",
          "ParameterValue": "LOWER"
        }
      ],
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
      "changeSetIfExists": true,
      "preDeploymentScript": "export AWS_DEFAULT_REGION=${ref:globalVariables.awsRegion}\necho \"Starting on task ${build-variable:current_task_name}\"\nexamples/example_01/lambda_function_src/build_and_package.sh --output_file=\"/tmp/example-01-lambda.zip\"\n",
      "postDeploymentScript": "python3 examples/example_01/scripts/create_sample_datafor_dynamodb_table.py\necho \"Successfully deployed template ${ref:tasks.dynamoDbTable.template} with initial record count set to ${exports:dynamoDbTable.initialRecordCount}. Task completed at ${exports:lambdaFunction.finalFinishTimestamp}\"\n",
      "extraBucketArtifacts": [
        "/tmp/example-01-lambda.zip"
      ],
      "taskDependsOn": [
        "dynamoDbTable"
      ],
      "taskExports": [
        {
          "ExportName": "finalFinishTimestamp",
          "ExportValue": "${shell:date}"
        }
      ]
    }
  ]
}
```
