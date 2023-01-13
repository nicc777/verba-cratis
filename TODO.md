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
| Task                      | Defines a task to be executed.                                                                                                                                                                                                                                                     |

See `examples/example_01/example_02.yaml` for an example
