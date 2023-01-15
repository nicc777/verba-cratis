
- [Getting the collection of processing strings from a regular string](#getting-the-collection-of-processing-strings-from-a-regular-string)
- [Docstrings](#docstrings)
- [Validation with Cerberus](#validation-with-cerberus)
- [Current Configuration Example in JSON:](#current-configuration-example-in-json)
- [Extracting function parameters from a string](#extracting-function-parameters-from-a-string)
- [Processing a string and all it's template sub-strings to arrive at the final value](#processing-a-string-and-all-its-template-sub-strings-to-arrive-at-the-final-value)


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
  * ~~Process from LEFT to RIGHT in a string; then~~
  * ~~Process from INNER-MOST nested snippet to OUTERMOST~~ 
  * See [Processing a string and all it's template sub-strings to arrive at the final value](#processing-a-string-and-all-its-template-sub-strings-to-arrive-at-the-final-value)

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
        "tableName": "verbacratis-test-001-table"
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
          "ParameterValue": "verbacratis-test-table"
        }
      ],
      "changeSetIfExists": true,
      "preDeploymentScript": "echo \"Starting on task ${build-variable:current_task_name}\"\n",
      "postDeploymentScript": "python3 examples/example_01/scripts/create_sample_datafor_dynamodb_table.py\nsleep 60\necho \"Successfully deployed template ${ref:tasks.dynamoDbTable.template} with ${exports:dynamoDbTable.initialRecordCount} initial records\"\n",
      "taskExports": [
        {
          "ExportName": "tableArn",
          "ExportValue": "${shell:aws dynamodb describe-table --table-name verbacratis-test-table | jq '.Table.TableArn'}"
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
          "ParameterValue": "verbacratis-example-01-${func:get_username()}"
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

# Extracting function parameters from a string

Reference: https://stackoverflow.com/questions/49723047/parsing-a-string-as-a-python-argument-list

Example:

```python
import ast
def parse_args(args):
    args = 'f({})'.format(args)
    tree = ast.parse(args)
    funccall = tree.body[0].value
    args = [ast.literal_eval(arg) for arg in funccall.args]
    kwargs = {arg.arg: ast.literal_eval(arg.value) for arg in funccall.keywords}
    return args, kwargs


value = 'get_aws_identity(include_account_if_available=True, blabla=123, something="1,2")'
value = value.partition('(')[2].rpartition(')')[0]
parse_args(value)
```

The result: `([], {'include_account_if_available': True, 'blabla': 123, 'something': '1,2'})`

# Processing a string and all it's template sub-strings to arrive at the final value

Setup an experiment to refine the template processing algorithm 

Given a string like: `abc ${func:func_a(p1=${ref:aa})} and ${ref:bb} and ${func:sum(n1=${ref:dd}, n2=${func:round_up(n=${ref:cc})})} def` (see [example data file](scratch/template_line.txt))

The example template processing algorithm is in [this source](scratch/processing_snippets_to_get_final_value.py)

Example run output:

```text
001: line=abc ${func:func_a(p1=${ref:aa})} and ${ref:bb} and ${func:sum(n1=${ref:dd}, n2=${func:round_up(n=${ref:cc})})} def
002: process_line(): line=abc ${func:func_a(p1=${ref:aa})} and ${ref:bb} and ${func:sum(n1=${ref:dd}, n2=${func:round_up(n=${ref:cc})})} def   len(snippets)=0   is_snippet=False
003: process_line(): line=func:func_a(p1=${ref:aa})   len(snippets)=0   is_snippet=True
004: process_line(): line=ref:aa   len(snippets)=0   is_snippet=True
005: process_line():   Processing is_snippet "ref:aa"
006:    get_snippet_processed_result(): snippet=ref:aa
007:    get_snippet_processed_result():    parts=['ref', 'aa']
008:    get_snippet_processed_result():    variable_classification=ref   variable_value=aa
009:    get_snippet_processed_result():       Running a simulation of processing the variable and getting a result
010:    get_snippet_processed_result():    result=aaa
011: process_line():   line=aaa
012: process_line():   Merging snippet "${ref:aa}" calculated value "aaa" back into original line "func:func_a(p1=${ref:aa})"
013: process_line():   Processing is_snippet "func:func_a(p1=aaa)"
014:    get_snippet_processed_result(): snippet=func:func_a(p1=aaa)
015:    get_snippet_processed_result():    parts=['func', 'func_a(p1=aaa)']
016:    get_snippet_processed_result():    variable_classification=func   variable_value=func_a(p1=aaa)
017:    get_snippet_processed_result():       Running a simulation of processing the variable and getting a result
018:    get_snippet_processed_result():    result=AAA
019: process_line():   line=AAA
020: process_line():   Merging snippet "${func:func_a(p1=${ref:aa})}" calculated value "AAA" back into original line "abc ${func:func_a(p1=${ref:aa})} and ${ref:bb} and ${func:sum(n1=${ref:dd}, n2=${func:round_up(n=${ref:cc})})} def"
021: process_line(): line=ref:bb   len(snippets)=0   is_snippet=True
022: process_line():   Processing is_snippet "ref:bb"
023:    get_snippet_processed_result(): snippet=ref:bb
024:    get_snippet_processed_result():    parts=['ref', 'bb']
025:    get_snippet_processed_result():    variable_classification=ref   variable_value=bb
026:    get_snippet_processed_result():       Running a simulation of processing the variable and getting a result
027:    get_snippet_processed_result():    result=TEST
028: process_line():   line=TEST
029: process_line():   Merging snippet "${ref:bb}" calculated value "TEST" back into original line "abc AAA and ${ref:bb} and ${func:sum(n1=${ref:dd}, n2=${func:round_up(n=${ref:cc})})} def"
030: process_line(): line=func:sum(n1=${ref:dd}, n2=${func:round_up(n=${ref:cc})})   len(snippets)=0   is_snippet=True
031: process_line(): line=ref:dd   len(snippets)=0   is_snippet=True
032: process_line():   Processing is_snippet "ref:dd"
033:    get_snippet_processed_result(): snippet=ref:dd
034:    get_snippet_processed_result():    parts=['ref', 'dd']
035:    get_snippet_processed_result():    variable_classification=ref   variable_value=dd
036:    get_snippet_processed_result():       Running a simulation of processing the variable and getting a result
037:    get_snippet_processed_result():    result=10
038: process_line():   line=10
039: process_line():   Merging snippet "${ref:dd}" calculated value "10" back into original line "func:sum(n1=${ref:dd}, n2=${func:round_up(n=${ref:cc})})"
040: process_line(): line=func:round_up(n=${ref:cc})   len(snippets)=0   is_snippet=True
041: process_line(): line=ref:cc   len(snippets)=0   is_snippet=True
042: process_line():   Processing is_snippet "ref:cc"
043:    get_snippet_processed_result(): snippet=ref:cc
044:    get_snippet_processed_result():    parts=['ref', 'cc']
045:    get_snippet_processed_result():    variable_classification=ref   variable_value=cc
046:    get_snippet_processed_result():       Running a simulation of processing the variable and getting a result
047:    get_snippet_processed_result():    result=9.9
048: process_line():   line=9.9
049: process_line():   Merging snippet "${ref:cc}" calculated value "9.9" back into original line "func:round_up(n=${ref:cc})"
050: process_line():   Processing is_snippet "func:round_up(n=9.9)"
051:    get_snippet_processed_result(): snippet=func:round_up(n=9.9)
052:    get_snippet_processed_result():    parts=['func', 'round_up(n=9.9)']
053:    get_snippet_processed_result():    variable_classification=func   variable_value=round_up(n=9.9)
054:    get_snippet_processed_result():       Running a simulation of processing the variable and getting a result
055:    get_snippet_processed_result():    result=10
056: process_line():   line=10
057: process_line():   Merging snippet "${func:round_up(n=${ref:cc})}" calculated value "10" back into original line "func:sum(n1=10, n2=${func:round_up(n=${ref:cc})})"
058: process_line():   Processing is_snippet "func:sum(n1=10, n2=10)"
059:    get_snippet_processed_result(): snippet=func:sum(n1=10, n2=10)
060:    get_snippet_processed_result():    parts=['func', 'sum(n1=10, n2=10)']
061:    get_snippet_processed_result():    variable_classification=func   variable_value=sum(n1=10, n2=10)
062:    get_snippet_processed_result():       Running a simulation of processing the variable and getting a result
063:    get_snippet_processed_result():    result=20
064: process_line():   line=20
065: process_line():   Merging snippet "${func:sum(n1=${ref:dd}, n2=${func:round_up(n=${ref:cc})})}" calculated value "20" back into original line "abc AAA and TEST and ${func:sum(n1=${ref:dd}, n2=${func:round_up(n=${ref:cc})})} def"
066: process_line():   line=abc AAA and TEST and 20 def
067: result=abc AAA and TEST and 20 def
```
