
- [Important Concepts](#important-concepts)
- [General Overview - What does this tool actually do?](#general-overview---what-does-this-tool-actually-do)
- [Accounts and Authentication](#accounts-and-authentication)
  - [Infrastructure Accounts](#infrastructure-accounts)
  - [Authentication to Infrastructure](#authentication-to-infrastructure)
  - [Manifests](#manifests)
    - [Local host with no need for authentication](#local-host-with-no-need-for-authentication)
    - [Remote Unix host with username and password](#remote-unix-host-with-username-and-password)
    - [AWS Account with Named Profile Authentication](#aws-account-with-named-profile-authentication)

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

An infrastructure account defines something you have to log into to execute deployment commands.

At the moment, the following types of Infrastructure accounts are supported:

| Type                | Class Name                   | Usage Context                                                                           |
|---------------------|------------------------------|-----------------------------------------------------------------------------------------|
| Local Account       | `InfrastructureAccount`      | This is the system this tool is running on                                              |
| Unix System Account | `UnixInfrastructureAccount`  | This is a remote Unix system which needs to be logged into in order to deploy resources |
| AWS Account         | `AwsInfrastructureAccount`   | This represents an AWS account in which you aim to deploy services                      |

> _**Note**_: A Unix account is typically a host that has a SSHD service running with the user account having a BASH compatible shell. Of course (in theory), this could also be a Windows system, but that was not really the intention.

> _**Note**_: Even though AWS is the only supported cloud platform right now, the idea is to add more in the future.

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

### Local host with no need for authentication

Manifest example:

```yaml
---
apiVersion: v1-alpha
kind: Authentication
metadata:
  name: no-auth
---
apiVersion: v1-alpha
kind: InfrastructureAccount
metadata:
  environments:
  - default
  name: deployment-host
spec:
  authentication:
    authenticationReference: no-auth
    type: Authentication
  provider: RunOnLocalhost
```

> _**Important**_: The deployment system can only have ONE of these deployment hosts defined. All other hosts must be properly defined with their appropriate credentials. Technically you would never have to define this in a manifest as it is always generated as default internally. You can always refer to it by the name `deployment-host` in objects like a `ShellScript`.

### Remote Unix host with username and password

Manifest Example:

```yaml
---
apiVersion: v1-alpha
kind: SshCredentialsBasedAuthenticationConfig
metadata:
  name: cd-user@host1.myorg
spec:
  authenticationType: SshUsingCredentials
  password: ${{EnvironmentVariables:computed:someSecret}}
---
apiVersion: v1-alpha
kind: UnixInfrastructureAccount
metadata:
  environments:
  - default
  name: host1
spec:
  authentication:
    authenticationReference: cd-user@host1.myorg
    type: SshCredentialsBasedAuthenticationConfig
  provider: ShellScript
```

> _**Note**_: Whenever a `ShellScript` will need to authenticate to this host, a call to the object's `auth_id()` method is made and the following string will then be returned: `cd-user@host1.myorg`

> _**Warning**_: Never store passwords in the clear in a manifest. Technically this is possible using this solution, but best practice is to always get the password from the environment. The `EnvironmentVariables` configuration is defined later in this document.

### AWS Account with Named Profile Authentication

Manifest Example:

```yaml
---
apiVersion: v1-alpha
kind: AwsProfileBasedAuthentication
metadata:
  name: accXYZ
spec:
  profile_name: profile_01
  region: eu-central-1
---
apiVersion: v1-alpha
kind: AwsInfrastructureAccount
metadata:
  environments:
  - sandbox-env
  name: sandbox-account
spec:
  authentication:
    authenticationReference: accXYZ
    type: AwsProfileBasedAuthentication
  provider: AWS
```
