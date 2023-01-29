# Status at 2023-01-12

I am starting today with a major re-write as I thought again about the solution.

Objectives:

* Align the configuration with the general structure of a [Kubernetes Manifest](https://kubernetes.io/docs/concepts/overview/working-with-objects/kubernetes-objects/) file:

```yaml
apiVersion: v1
kind: SomeKind
metadata:
    name: MyName1
    labels:
        label1: value1
spec:
    something:
        somethingelse: 123
---
apiVersion: v1
kind: SomeOtherKind
metadata:
    name: MyName2
    labels:
        label1: label2
spec:
    selector:
        matchLabels:
            label1: value1
    something:
        somethingelse: 456
```

## What Kind of Objects Is Required?

| Kind                      | Description                                                                                                                                                                                                                                                                        |
|---------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Environment               | Defines the high level environment, linked to a specific AWS Account via a Profile (or environment variables, for authentication). There is also a default environment called `default` which is assumed for any resources environment bound but without an environment identifier |
| EnvironmentVariables      | Parameters available to an environment                                                                                                                                                                                                                                             |
| ShellScript               | Defines a shell script to be run. The shell script output should be matched to a output parser                                                                                                                                                                                     |
| InfrastructureTemplate    | Defines the content or file location of a cloud infrastructure manifest, for example an AWS CloudFormation Template.                                                                                                                                                               |
| Task                      | Defines a task to be executed. Tasks can be limited to be executed only in certain environments.                                                                                                                                                                                   |
| Deployment                | Defines a deployment specific to an environment that contains one or more tasks.                                                                                                                                                                                                   |

See `examples/example_01/example_02.yaml` for an example

Order of parsing of configuration:

1. ShellScript
2. EnvironmentVariables - Note: if `metadata.labels.environment` is set, and matches the provided running environment, parse. If environment label is not present, assume name is `default` and only parse if the running environment name is also `default`
3. Environment 
4. InfrastructureTemplate
5. Task
6. Deployment

## Deployment State

There is a global configuration for the application, either in `$HOME/.verbacratis/config` or that can be specified using the `--config` parameter to specify the location of the configuration.

If no configuration is available, the following will be set as default:

```yaml
---
apiVersion: v1-alpha
kind: StateStore
metadata:
  name: verbacratis-state-store
spec:
  connectionUrl: sqlite:///verbacratis.db
  provider: sqlalchemy
---
apiVersion: v1-alpha
kind: GlobalConfiguration
metadata:
    name: verbacratis
spec:
    logging:
        handlers:
        -   name: StreamHandler
            parameters:
            -   parameterName: format
                parameterType: str
                parameterValue: '%(funcName)s:%(lineno)d -  %(levelname)s - %(message)s'
    infrastructureAccounts:
    -   accountName: deployment-host
        accountProvider: ShellScript
        authentication:
            runOnDeploymentHost: true
```

## Basic Application Logic

TODO
