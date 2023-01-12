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

| Kind        | Description                                                                                                                       |
|-------------|-----------------------------------------------------------------------------------------------------------------------------------|
| Environment | Defines the high level environment, linked to a specific AWS Account via a Profile (or environment variables, for authentication) |

### Environment Kind

Example:

```yaml
apiVersion: v1-alpha
kind: Environment
metadata:
    name: dev
    labels:
        phase: deployment
spec:
    authentication:
        useProfile: true
        profileName: AwsDevProfileName
```
