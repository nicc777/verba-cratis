# Infrastructure Account Manifests

## The local system running the application

Internally a manifest is automatically created for the machine running the deployment application. Below is the basic example:

```yaml
---
apiVersion: v1-alpha
kind: Authentication
metadata:
  name: no-auth
---
apiVersion: v1-alpha
kind: UnixInfrastructureAccount
metadata:
  environments:
  - default
  name: deployment-host
spec:
  authentication:
    authenticationReference: no-auth
    type: Authentication
  provider: ShellScript
```

You can refer to the local machine as `deployment-host` for anything, like a task, that needs to run code on the local machine.

> **Note**
> You never have to actually define the above in any manifest - it is automatically generated. All environments you define else where will automatically be added to the `deployment-host` list of environments.
