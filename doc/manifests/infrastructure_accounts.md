- [Standard fields required for all Manifests](#standard-fields-required-for-all-manifests)
- [Authentication Definitions](#authentication-definitions)
  - [Authentication manifest](#authentication-manifest)
    - [Examples of Authentication manifests](#examples-of-authentication-manifests)
  - [UnixHostAuthentication manifest](#unixhostauthentication-manifest)
    - [Examples of UnixHostAuthentication manifests](#examples-of-unixhostauthentication-manifests)
  - [SshHostBasedAuthenticationConfig manifest](#sshhostbasedauthenticationconfig-manifest)
    - [Examples of SshHostBasedAuthenticationConfig manifests](#examples-of-sshhostbasedauthenticationconfig-manifests)
  - [SshPrivateKeyBasedAuthenticationConfig manifest](#sshprivatekeybasedauthenticationconfig-manifest)
    - [Examples of SshPrivateKeyBasedAuthenticationConfig manifests](#examples-of-sshprivatekeybasedauthenticationconfig-manifests)
  - [AwsAuthentication manifest](#awsauthentication-manifest)
    - [Examples of AwsAuthentication manifests](#examples-of-awsauthentication-manifests)
  - [AwsKeyBasedAuthentication manifest](#awskeybasedauthentication-manifest)
    - [Examples of AwsKeyBasedAuthentication manifests](#examples-of-awskeybasedauthentication-manifests)
  - [AwsProfileBasedAuthentication manifest](#awsprofilebasedauthentication-manifest)
    - [Examples of AwsProfileBasedAuthentication manifests](#examples-of-awsprofilebasedauthentication-manifests)
- [Infrastructure Account Manifests](#infrastructure-account-manifests)
  - [The local system running the application](#the-local-system-running-the-application)
  - [UnixInfrastructureAccount manifest](#unixinfrastructureaccount-manifest)
    - [Examples of UnixInfrastructureAccount manifests](#examples-of-unixinfrastructureaccount-manifests)
  - [AwsInfrastructureAccount manifest](#awsinfrastructureaccount-manifest)
    - [Examples of AwsInfrastructureAccount manifests](#examples-of-awsinfrastructureaccount-manifests)
      - [Example 1 - Using AWS profile based authentication](#example-1---using-aws-profile-based-authentication)
      - [Example 2 - Using AWS credentials from the environment](#example-2---using-aws-credentials-from-the-environment)

# Standard fields required for all Manifests

The following are manifest fields required for all manifests:

| Field           | Required | Values           | Description                                                                                                  |
|-----------------|:--------:|------------------|--------------------------------------------------------------------------------------------------------------|
| `apiVersion`    | Yes      | `v1-alpha`       | No strict parsing enforcement is done at the moment, but this will change in the future                      |
| `kind`          | Yes      | See list         | Describes the type of manifest                                                                               |
| `metadata.name` | Yes      | Variable String  | A globally unique identifier for this manifest. Used in other manifests to link to a specific named manifest |

List of Infrastructure related `Kind` values:

* `Authentication` - [more info](#examples-of-authentication-manifests)
* `UnixHostAuthentication` - [more info](#defaulthostbasedauthentication-manifest)
* `SshHostBasedAuthenticationConfig` - [more info](#sshhostbasedauthenticationconfig-manifest)
* `SshPrivateKeyBasedAuthenticationConfig` - [more info](#examples-of-sshprivatekeybasedauthenticationconfig-manifests)
* `AwsAuthentication` - [more info](#awsauthentication-manifest)
* `AwsKeyBasedAuthentication` - [more info](#awskeybasedauthentication-manifest)
* `AwsProfileBasedAuthentication` - [more info](#awsprofilebasedauthentication-manifest)
* `InfrastructureAccount` - [more info](#the-local-system-running-the-application)
* `UnixInfrastructureAccount` - [more info](#)
* `AwsInfrastructureAccount` - [more info](#)

# Authentication Definitions

## Authentication manifest

In addition to the standard required fields, the following fields can also be used:

| Field           | Required | Values           | Description                                                                             |
|-----------------|:--------:|------------------|-----------------------------------------------------------------------------------------|
| `metadata.name` | Yes      | `no-auth`        | Signifies that no authentication will be done (assuming we are already logged in)       |

### Examples of Authentication manifests

```yaml
---
apiVersion: v1-alpha
kind: Authentication
metadata:
  name: no-auth
```

## UnixHostAuthentication manifest

In addition to the standard required fields, the following fields can also be used:

| Field           | Required | Values           | Description                                                                             |
|-----------------|:--------:|------------------|-----------------------------------------------------------------------------------------|
| `metadata.name` | Yes      | String           | The DNS resolvable hostname or IP Address of a host                                     |

### Examples of UnixHostAuthentication manifests

```yaml
apiVersion: v1-alpha
kind: UnixHostAuthentication
metadata:
  name: localhost
```

## SshHostBasedAuthenticationConfig manifest

In addition to the standard required fields, the following fields can also be used:

| Field             | Required | Values           | Description                                                                                         |
|-------------------|:--------:|------------------|-----------------------------------------------------------------------------------------------------|
| `metadata.name`   | Yes      | String           | The user name and DNS resolvable hostname or IP Address of a host in the format `username@hostname` |
| `spec.password`   | Yes      | String           | The password. Consider using environment variables and never include actual passwords in a manifest |

> **Note**
> Environment variable expansion will be explained later

<!-- TODO Link to environment variable expansion  -->

> **Warning**
> When using any for of authentication that require a password/passphrase, never include such a piece of sensitive information in the manifest file. Later examples will demonstrate how to use environment variables to obtain sensitive credential information from an external source like an environment variable.

### Examples of SshHostBasedAuthenticationConfig manifests

```yaml
apiVersion: v1-alpha
kind: SshCredentialsBasedAuthenticationConfig
metadata:
  name: testuser@example.tld
spec:
  password: ${EnvironmentVariables:computed:MyPassword}
```

## SshPrivateKeyBasedAuthenticationConfig manifest

In addition to the standard required fields, the following fields can also be used:

| Field                 | Required | Values           | Description                                                                                         |
|-----------------------|:--------:|------------------|-----------------------------------------------------------------------------------------------------|
| `metadata.name`       | Yes      | String           | The user name and DNS resolvable hostname or IP Address of a host in the format `username@hostname` |
| `spec.privateKeyPath` | Yes      | String           | The path to the private key on the local system that will run the deployment application            |

### Examples of SshPrivateKeyBasedAuthenticationConfig manifests

```yaml
apiVersion: v1-alpha
kind: SshPrivateKeyBasedAuthenticationConfig
metadata:
  name: testuser@example.tld
spec:
  privateKeyPath: /tmp/test_key_file
```

## AwsAuthentication manifest

This kind of manifest is only useful if the AWS credentials can be obtained from the local environment, for example environment variables.

In addition to the standard required fields, the following fields can also be used:

| Field                 | Required | Values           | Description                                                                                                                                                                                                                  |
|-----------------------|:--------:|------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `metadata.name`       | Yes      | String           | A globally unique name                                                                                                                                                                                                       |
| `spec.region`         | No       | String           | If no region is specified, a default region or region defined in environment variables will be used. Must be a valid [AWS region](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html) |

### Examples of AwsAuthentication manifests

```yaml
apiVersion: v1-alpha
kind: AwsAuthentication
metadata:
  name: default
spec:
  region: eu-central-1
```

## AwsKeyBasedAuthentication manifest

In addition to the standard required fields, the following fields can also be used:

| Field                 | Required | Values           | Description                                                                                                                                                                                                                  |
|-----------------------|:--------:|------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `metadata.name`       | Yes      | String           | A globally unique name                                                                                                                                                                                                       |
| `spec.region`         | No       | String           | If no region is specified, a default region or region defined in environment variables will be used. Must be a valid [AWS region](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html) |
| `spec.access_key`     | Yes      | String           | The value of the access key                                                                                                                                                                                                  |
| `spec.secret_key`     | Yes      | String           | The value of the secret key. Consider using environment variables!                                                                                                                                                           |

> **Note**
> Environment variable expansion will be explained later

<!-- TODO Link to environment variable expansion  -->

> **Warning**
> When using any for of authentication that require a password/passphrase, never include such a piece of sensitive information in the manifest file. Later examples will demonstrate how to use environment variables to obtain sensitive credential information from an external source like an environment variable.

### Examples of AwsKeyBasedAuthentication manifests

```yaml
apiVersion: v1-alpha
kind: AwsKeyBasedAuthentication
metadata:
  name: default
spec:
  access_key: abc
  region: eu-central-1
  secret_key: ${{EnvironmentVariables:computed:someSecret}}
```

## AwsProfileBasedAuthentication manifest

In addition to the standard required fields, the following fields can also be used:

| Field                 | Required | Values           | Description                                                                                                                                                                                                                  |
|-----------------------|:--------:|------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `metadata.name`       | Yes      | String           | A globally unique name                                                                                                                                                                                                       |
| `spec.region`         | No       | String           | If no region is specified, a default region or region defined in environment variables will be used. Must be a valid [AWS region](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html) |
| `spec.profile_name`   | Yes      | String           | The name of the profile as defined in your local AWS configuration (see [AWS Documentation](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-profiles.html))                                                   |

> **Note**
> Environment variable expansion will be explained later

<!-- TODO Link to environment variable expansion  -->

> **Warning**
> When using any for of authentication that require a password/passphrase, never include such a piece of sensitive information in the manifest file. Later examples will demonstrate how to use environment variables to obtain sensitive credential information from an external source like an environment variable.

### Examples of AwsProfileBasedAuthentication manifests

```yaml
apiVersion: v1-alpha
kind: AwsProfileBasedAuthentication
metadata:
  name: abc
spec:
  profile_name: default
  region: eu-central-1
```

# Infrastructure Account Manifests

Each infrastructure account is linked to one authentication manifest. The only exception is the internally generated manifest for the local system the application is running on, named `deployment-host`

## The local system running the application

Internally a manifest is automatically created for the machine running the deployment application. Below is the basic example:

```yaml
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

You can refer to the local machine as `deployment-host` for anything, like a task, that needs to run code on the local machine.

> **Note**
> You never have to actually define the above in any manifest - it is automatically generated. All environments you define else where will automatically be added to the `deployment-host` list of environments.

## UnixInfrastructureAccount manifest

In addition to the standard required fields, the following fields can also be used:

| Field                    | Required | Values           | Description                                                                                                                                                                                                                  |
|--------------------------|:--------:|------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `metadata.name`          | Yes      | String           | A globally unique name                                                                                                                                                                                                       |
| `metadata.environments`  | Yes      | List of String   | A list of environment names for which this host is in scope.                                                                                                                                                                 |
| `spec.authentication`    | Yes      | String           | Name of the authentication manifest linked to this host                                                                                                                                                                      |
| `spec.provider`          | Yes      | String           | Defines the kind of execution to be performed on this host. :warning: Still in active development, so this may change !!!                                                                                                    |

> **Note**
> Environment variable expansion will be explained later

<!-- TODO Link to environment variable expansion  -->

> **Warning**
> When using any for of authentication that require a password/passphrase, never include such a piece of sensitive information in the manifest file. Later examples will demonstrate how to use environment variables to obtain sensitive credential information from an external source like an environment variable.

### Examples of UnixInfrastructureAccount manifests

```yaml
---
apiVersion: v1-alpha
kind: SshCredentialsBasedAuthenticationConfig
metadata:
  name: cd-user@host1.myorg
spec:
  password: ${{EnvironmentVariables:computed:someSecret}}
---
apiVersion: v1-alpha
kind: UnixInfrastructureAccount
metadata:
  name: host1
  environments:
  - default
spec:
  authentication: cd-user@host1.myorg
  provider: ShellScript
```

## AwsInfrastructureAccount manifest

In addition to the standard required fields, the following fields can also be used:

| Field                    | Required | Values           | Description                                                                                                                                                                                                                  |
|--------------------------|:--------:|------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `metadata.name`          | Yes      | String           | A globally unique name                                                                                                                                                                                                       |
| `metadata.environments`  | Yes      | List of String   | A list of environment names for which this host is in scope.                                                                                                                                                                 |
| `spec.authentication`    | Yes      | String           | Name of the authentication manifest linked to this host                                                                                                                                                                      |
| `spec.provider`          | Yes      | String           | Defines the kind of execution to be performed on this host. :warning: Still in active development, so this may change !!!                                                                                                    |

> **Note**
> Environment variable expansion will be explained later

<!-- TODO Link to environment variable expansion  -->

> **Warning**
> When using any for of authentication that require a password/passphrase, never include such a piece of sensitive information in the manifest file. Later examples will demonstrate how to use environment variables to obtain sensitive credential information from an external source like an environment variable.

### Examples of AwsInfrastructureAccount manifests

#### Example 1 - Using AWS profile based authentication

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
  name: sandbox-account
  environments:
  - sandbox-env
spec:
  authentication: accXYZ
  provider: AWS
```

#### Example 2 - Using AWS credentials from the environment

```yaml
---
apiVersion: v1-alpha
kind: AwsAuthentication
metadata:
  name: default
spec:
  region: eu-central-1
---
apiVersion: v1-alpha
kind: AwsInfrastructureAccount
metadata:
  environments:
  - default
  name: test
spec:
  authentication: default
  provider: AWS
```