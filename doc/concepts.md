
- [Important Concepts](#important-concepts)
- [General Overview - What does this tool actually do?](#general-overview---what-does-this-tool-actually-do)
- [Accounts and Authentication](#accounts-and-authentication)
  - [Infrastructure Accounts](#infrastructure-accounts)
  - [Authentication to Infrastructure](#authentication-to-infrastructure)

# Important Concepts

This page will try to explain some of the concepts used in this project

# General Overview - What does this tool actually do?

The general idea is to orchestrate Infrastructure Deployments in complex environments that may rely of numerous different tools and technologies.

Today we have several teams/individuals going by various titles such as DevOps engineers or just Infrastructure support engineers. However, their role all involves looking after some aspect of infrastructure and often their duties will include maintaining a repository with Infrastructure-as-Code artifacts. These artifacts form the definition of what needs to be provisioned and/or deployed given some additional data, like what, where etc. 

Sometimes it can be "easy" and only resources in a single public cloud environment like AWS have to be maintained. In these cases, tools like CloudFormation or even Terraform works really well.

But more often, it's a lot more complex and any one or more of the following may apply for which this tool aims to help out:

* Maintaining multiple types of public cloud accounts (AWS, MS Azure, Google etc.)
* Maintaining diverse technologies in one or more public cloud platform, like AWS core with Serverless (SAM) and AWS Amplify - each with their own quirks and where tools like Terraform may not be fully suited to deal with all the nuances.
* A mix of on-premise, edge and cloud environments, each using different technologies
* Require conditional deployment of resources in various accounts as part of a single deployment

But is this not the domain of Terraform or similar tools? At it most basic, there is an argument that tools like Terraform has the same general aim, but the difference with this tool is to fill any remaining gaps that tools like Terraform may not be able to fill. Therefore, Terraform, CloudFormation and all other similar tools can still be used within this tool. 

In fact, some complex or evolving organizations may very well have a mix of these tools and teams may struggle to coordinate deployments and maintenance of their infrastructure across all these tools.

This tool can be used to mix and match existing tools like Terraform and CloudFormation together with existing custom scripts and other tools as a wrapper that will orchestrate the running of these tools across different cloud providers, on-site and edge infrastructure and at the same time track changes in the code base to assist keeping infrastructure up to date.

At the most fundamental level, this tool wraps a number of tasks (shell scripts or other supported technologies) in a organized set of instructions with conditions and options for rollback/recovery in the case of errors.

# Accounts and Authentication

## Infrastructure Accounts

Infrastructure is classified along a base class of a `InfrastructureAccount` from which the following other classes are defined:

* `UnixInfrastructureAccount`
* `AwsInfrastructureAccount`

> **Note**
> More of these target Infrastructure types are planned for the future including for Kubernetes and other public cloud providers.

Each Infrastructure account also needs some kind of authentication, assuming the deployment will mostly be done on remote hosts. The base class of `Authentication` will be used to extend other classes like:

| Manifest `Kind` [documentation](manifests/infrastructure_accounts.md) | Description                                                                                                                                                                                                                                                                           |
|-----------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `UnixHostAuthentication`                                              | A base class extending `Authentication` for use with Unix like hosts.                                                                                                                                                                                                                 |
| `SshHostBasedAuthenticationConfig`                                    | Extends `UnixHostAuthentication`. Using this kind of authentication implies that the local SSH configuration (usually in `~/.ssh/config`) already defines the keys and other aspects around authenticating against a host which does not require any additional password/passphrases. |
| `SshCredentialsBasedAuthenticationConfig`                             | Extends `SshHostBasedAuthenticationConfig` but for hosts requiring a username and password (no keys).                                                                                                                                                                                 |
| `SshPrivateKeyBasedAuthenticationConfig`                              | Extends `SshHostBasedAuthenticationConfig` using private keys but with no entries in the SSH config file.                                                                                                                                                                             |

> **Warning**
> When using any for of authentication that require a password/passphrase, never include such a piece of sensitive information in the manifest file. Later examples will demonstrate how to use environment variables to obtain sensitive credential information from an external source like an environment variable.

## Authentication to Infrastructure

Each type on [Infrastructure Account](#infrastructure-account) also require some form of authentication. The following authentication types are supported:

| Authentication and Target Type Mix            | Supporting Infrastructure Class | Authentication Class Name                 | Usage Context                                                                                                                                                                             |
|-----------------------------------------------|---------------------------------|-------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| No Authentication                             | `InfrastructureAccount`         | `Authentication`                          | Only really used for the local account that the tool is being run from.                                                                                                                   |
| Unix Host Authentication                      | `UnixInfrastructureAccount`     | `SshHostBasedAuthenticationConfig`        | Supporting SSH authentication to hosts, where those hosts are defined in local SSH configuration. for example in a file in `/etc/ssh/ssh_config.d`                                        |
| Unix Username & password based authentication | `UnixInfrastructureAccount`     | `SshCredentialsBasedAuthenticationConfig` | Supports unix authentication via SSH using a username and password.                                                                                                                       |
| Unix Key based authentication                 | `UnixInfrastructureAccount`     | `SshPrivateKeyBasedAuthenticationConfig`  | Supports unix authentication using private keys.                                                                                                                                          |
| Generic AWS Authentication                    | `AwsInfrastructureAccount`      | `AwsAuthentication`                       | AWS Authentication with no specifics defined and credentials are derived from the environment [more info](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html).|
| AWS authentication using keys                 | `AwsInfrastructureAccount`      | `AwsKeyBasedAuthentication`               | Uses AWS access key and secret key values to authenticate.                                                                                                                                |
| AWS authentication using profiles             | `AwsInfrastructureAccount`      | `AwsProfileBasedAuthentication`           | Uses AWS named profile to authenticate.                                                                                                                                                   |

