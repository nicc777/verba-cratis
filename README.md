# Infrastructure Orchestration in Python 

> `verbacratis` - literally translates to "_the words of the fence_" alluding to the fact that CD tools sits "on the fence" and orchestrate deployments. In the project context it means how we define our Infrastructure-as-Code (IaC)

| Project Attribute | Value / Description |
|-------------------|---------------------|
| Start Date        | 2022-06-18          |
| Current Status    | Model Design        |

## Short Introduction

This project aims to create a command line utility that can be run against YAML configuration files (manifest format, similar to Kubernetes) that defines deployments that can handle multiple tasks. Tasks can include third party cloud definition, for example [AWS CloudFOrmation Template](https://aws.amazon.com/cloudformation/resources/templates/), or it could also be just normal Shell Scripts.

## Motivation, or, why another tool?

I became frustrated with having multiple IaC definitions for multiple technologies/backends/cloud etc. and I needed a way to orchestrate more complex deployments, updates and tear-downs across a number of third party back-ends like AWS CloudFormation. Even within AWS things can get pretty wild as we have to deal with CloudFormation, SAM Templates, Amplify and even the AWS CLI for anything not covered by any of these other three tools... It's wild! With this project I hope to coordinate these various technologies with a deployment orchestration system can can keep proper track of my deployments across various technologies.

Therefore this tool aims to be a wrapper of sorts around multiple other deployment tools and it aims to have the following general characteristics:

* Support common Infrastructure deployment tools, starting with AWS CloudFormation but later include many more tools (extensibility of tooling). I hope to add support for Kubernetes and tools like Helm charts in the future.
* Where tools are not directly supported yet, a general `ShellScript` wrapper can be used that can essentially run any command(s), for example to deploy Helm charts
* This tool needs to understand how to authenticate against hosts and cloud accounts. Initially Unix system accounts and AWS Cloud Accounts will be supported, with plans to expand this to Kubernetes cluster accounts and also other public cloud accounts.
* The actual deployment configuration, or manifest files, can live on the local machine where the tool is run, or in Git. 
* Deployment definitions include steps for rolling back when deployments fail.
* Deployment definitions also include steps for deleting deployments
* I will try to incorporate a simple "state" system to track deployments in order to detect differences from source to what was previously deployed. The "updates" or "change set" logic is also defined in steps in the deployment manifest.
* Deploying infrastructure may require some dependencies, and I have thought about how I could structure deployments in a complex hierarchy. There is also potentially scope for deploying temporary infrastructure that can be cleaned up after a deployment, for example a temporary S3 bucket to hold Lambda function artifacts which is only required during deployments or updates.
* Deployment steps does not have to target only "one account" (like an AWS account). Perhaps you are deploying infrastructure in account B that requires also some updates in Account A. For example, you may not have delegated DNS yet, so deployment of a web site in account B may require a DNS update in account A.
* The reality of daily infrastructure operations is that we have to manage on-premise and cloud infrastructure. This tool will attempt to provide sufficient wrappers to orchestrate deployments to these two worlds from a single code base.
* This tool compliments other CD tools, like ArgoCD, as it can prepare some infrastructure in domains not supported by those tools. This tool could be used as the deployment tool of ArgoCD itself, as well as it's initial configuration etc.
* The concepts of environments means that you can define your SANDBOX, TEST and PRODUCTION environments, each with different accounts (potentially) and support slightly different deployment steps. For example, some deployment steps may only be required in certain accounts within the context of a certain environment. One practical example could be to block Internet traffic to a web site in the SANDBOX and TEST accounts, which is otherwise allowed in the PRODUCTION account.

The idea is to eventually add this project to [PyPI](https://pypi.org/)

# Recent Updates of Note

| Date       | Update Description                                                                                                                                                                                    |
|------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 2023-02-18 | At startup, both system and project configurations can now be loaded from a number of sources, including URL's, local files/directories and Git sources. Added a lot of documentation.                |
| 2023-02-04 | Implemented retrieval and processing of files for deployments from URLS.                                                                                                                              |
| 2023-02-02 | Implemented Git repository cloning functions that will be key in the retrieval and processing of files for deployments.                                                                               |
| 2023-01-30 | I have redesigned the models from my initial attempt, and I am about half way through. I added the motivations and features list to this README.                                                      |
| 2023-01-15 | I renamed the project from `acfop` to `verba-cratis` as the original project was purely AWS focused. I quickly realized I need something that supports more platforms.                                |

# Testing

## Unit Tests

The following need to be installed:

* `pip3 install coverage`

All commands in this section assumes that the project root directory is the working directory.

Run Tests

```shell
sh run_tests.sh
```

Open your browser and open [the report](reports/index.html)

# Resources and References

* Python Documentation:
  * https://realpython.com/documenting-python-code/
  * https://github.com/google/styleguide/blob/gh-pages/pyguide.md#38-comments-and-docstrings
