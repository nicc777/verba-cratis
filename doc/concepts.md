
- [Important Concepts](#important-concepts)
- [Infrastructure Account](#infrastructure-account)

# Important Concepts

This page will try to explain some of the concepts used in this project

# Infrastructure Account

An infrastructure account defines something you have to log into to execute deployment commands.

At the moment, the following types of Infrastructure accounts are supported:

| Type                | Class Name                   | Usage Context                                                                           |
|---------------------|------------------------------|-----------------------------------------------------------------------------------------|
| Local Account       | `InfrastructureAccount`      | This is the system this tool is running on                                              |
| Unix System Account | `UnixInfrastructureAccount`  | This is a remote Unix system which needs to be logged into in order to deploy resources |
| AWS Account         | `AwsInfrastructureAccount`   | This represents an AWS account in which you aim to deploy services                      |

> _**Note**_: A Unix account is typically a host that has a SSHD service running with the user account having a BASH compatible shell. Of course (in theory), this could also be a Windows system, but that was not really the intention.


