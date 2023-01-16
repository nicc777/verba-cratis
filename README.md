# Infrastructure Orchestration in Python 

> `verbacratis` - literally translates to "_the words of the fence_", but in the project context it means how we define our Infrastructure-as-Code (IaC)

| Project Attribute | Value / Description |
|-------------------|---------------------|
| Start Date        | 2022-06-18          |
| Current Status    | Planning            |

Details about this project to follow soon...

This project aims to create a command line utility that can be run against a YAML configuration file that defines deployments that can handle multiple tasks. Tasks can include third party cloud definition, for example [AWS CloudFOrmation Template](https://aws.amazon.com/cloudformation/resources/templates/), or it could also be just normal Shell Scripts.

I became frustrated with having multiple IaC definitions for multiple technologies/backends/cloud etc. and I needed a way to orchestrate more complex deployments. updates and tear-downs across a number of third party back-ends, like AWS CloudFormation. Even within AWS things can get pretty wild as we have to deal with CloudFormation, SAM Templates, Amplify and even the AWS CLI for anything not covered by any of these other three tools... It's wild! With this project I hope to coordinate these various technologies with a deployment orchestration system can can keep proper track of my deployments across various technologies.

The idea is to eventually add this project to [PyPI](https://pypi.org/)

At the moment, I am planning the implementation and there will probably be a number of commits happening before I update this README again.

# Recent UPdates of Note

| Date       | Update Description                                                                                                                                                        |
|------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 2023-01-15 | I renamed the project from `acfop` to `verba-cratis` as the original project was purely AWS focused. I quickly realized I need something that supports more platforms.    |

# Testing

## Preparation

The following need to be installed:

* `pip3 install coverage`

All commands in this section assumes that the project root directory is the working directory.

## Basic Unit Tests

Run individual tests, for example:

```shell
python3 tests/test_utile_parser.py
```

## Coverage

Run Tests

```shell
sh run_tests.sh
```

# Resources and References

* Python Documentation:
  * https://realpython.com/documenting-python-code/
  * https://github.com/google/styleguide/blob/gh-pages/pyguide.md#38-comments-and-docstrings
