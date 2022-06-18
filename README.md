# AWS CloudFormation Orchestration in Python (acfop)

| Project Attribute | Value / Description |
|-------------------|---------------------|
| Start Date        | 2022-06-18          |
| Current Status    | Planning            |

Details about this project to follow soon...

This project aims to create a command line utility that can be run against a YAML configuration file that defines deployments that can handle multiple tasks, where each task links to an [AWS CloudFOrmation Template](https://aws.amazon.com/cloudformation/resources/templates/)

My motivation for this project came from the fact that I had to maintain a number of CloudFormation templates in various environments, each with slightly different parameters and other dependencies, and I needed a way to better orchestrate this.

This project is not a replacement or alternative to CloudFormation - it depends on it! 

The intention is to allow multiple CloudFOrmation templates to be deployed in an ordered fashion into different environment, where each environment may require different parameters and perhaps even additional steps (or templates).

The idea is to eventually add this project to [PyPI](https://pypi.org/)

At the moment, I am planning the implementation and there will probably be a number of commits happening before I update this README again.
