# Unmanage

The `unmanage` argument allows you to unmanage a currently managed [application](#app), or a currently unmanaged [cluster](#cluster).

```text
$ ./toolkit.py unmanage -h
usage: toolkit.py unmanage [-h] {app,cluster} ...

optional arguments:
  -h, --help     show this help message and exit

objectType:
  {app,cluster}
    app          unmanage app
    cluster      unmanage cluster
```

## App

Prior to unmanaging an appplication, it is recommended to first [destroy](../destroy/README.md) all [snapshots](../destroy/README.md#snapshot) and [backups](../destroy/README.md#backup) of the app.  Once that is complete, the [app ID](../list/README.md#apps) is utilized with the following command.

```text
./toolkit.py unmanage app <appID>
```

Sample output:

```text
$ ./toolkit.py unmanage app 1d16c9f0-1b7f-4f21-804c-4162b0cfd56e
App unmanaged
```

## Cluster

Prior to unmanaging a cluster, it is recommended to first unmanage all [applications](#app) running in the cluster.  Once that is complete, utilzie the [cluster ID](../list/README.md#clusters) with the following command.

```text
./toolkit.py unmanage cluster <clusterID>
```

Sample output:

```text
$ ./toolkit.py unmanage cluster 80d6bef8-300c-44bd-9e36-04ef874bdc29
Cluster unmanaged
```
