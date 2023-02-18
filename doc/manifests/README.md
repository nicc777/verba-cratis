# Manifests Documentation

Here you can find all the specifications for the various manifests used by the system.

> **Note**
> * In general the `kind` field of a manifest always map to a class name in source code, typically defined under `verbacratis.models.`.
> * Each `metadata.name` field needs to be globally unique as it is used for referencing between manifests/objects
> * Reserved `metadata.name` include `deployment-host`


| High Level Type                                                |
|----------------------------------------------------------------|
| [Infrastructure Account Manifests](infrastructure_accounts.md) |
| [Project Manifests](project_definitions.md)                    |
