
- [Important Concepts](#important-concepts)
- [Accounts and Authentication](#accounts-and-authentication)
  - [Infrastructure Accounts](#infrastructure-accounts)
  - [Authentication to Infrastructure](#authentication-to-infrastructure)
  - [Manifests](#manifests)
    - [Local host with no need for authentication:](#local-host-with-no-need-for-authentication)

# Important Concepts

This page will try to explain some of the concepts used in this project

# Accounts and Authentication

## Infrastructure Accounts

An infrastructure account defines something you have to log into to execute deployment commands.

At the moment, the following types of Infrastructure accounts are supported:

| Type                | Class Name                   | Usage Context                                                                           |
|---------------------|------------------------------|-----------------------------------------------------------------------------------------|
| Local Account       | `InfrastructureAccount`      | This is the system this tool is running on                                              |
| Unix System Account | `UnixInfrastructureAccount`  | This is a remote Unix system which needs to be logged into in order to deploy resources |
| AWS Account         | `AwsInfrastructureAccount`   | This represents an AWS account in which you aim to deploy services                      |

> _**Note**_: A Unix account is typically a host that has a SSHD service running with the user account having a BASH compatible shell. Of course (in theory), this could also be a Windows system, but that was not really the intention.

## Authentication to Infrastructure

Each type on [Infrastructure Account](#infrastructure-account) also require some form of authentication. The following authentication types are supported:

| Type                                          | Supporting Infrastructure Class | Authentication Class Name                 | Usage Context                                                                                                                                                                             |
|-----------------------------------------------|---------------------------------|-------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| No Authentication                             | `InfrastructureAccount`         | `Authentication`                          | Only really used for the local account that the tool is being run from.                                                                                                                   |
| Unix Host Authentication                      | `UnixInfrastructureAccount`     | `SshHostBasedAuthenticationConfig`        | Supporting SSH authentication to hosts, where those hosts are defined in local SSH configuration. for example in a file in `/etc/ssh/ssh_config.d`                                        |
| Unix Username & password based authentication | `UnixInfrastructureAccount`     | `SshCredentialsBasedAuthenticationConfig` | Supports unix authentication via SSH using a username and password.                                                                                                                       |
| Unix Key based authentication                 | `UnixInfrastructureAccount`     | `SshPrivateKeyBasedAuthenticationConfig`  | Supports unix authentication using private keys.                                                                                                                                          |
| Generic AWS Authentication                    | `AwsInfrastructureAccount`      | `AwsAuthentication`                       | AWS Authentication with no specifics defined and credentials are derived from the environment [more info](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html).|
| AWS authentication using keys                 | `AwsInfrastructureAccount`      | `AwsKeyBasedAuthentication`               | Uses AWS access key and secret key values to authenticate.                                                                                                                                |
| AWS authentication using profiles             | `AwsInfrastructureAccount`      | `AwsProfileBasedAuthentication`           | Uses AWS named profile to authenticate.                                                                                                                                                   |

## Manifests

The above classes each translates to a specific YAML manifest, comparable to Kubernetes manifest files. This makes it easy to convert to and from classes and files.

The following combinations are typically possible:

### Local host with no need for authentication:

Manifest example:

```yaml
TODO
```

