# Manage (aka Define)

The `manage` argument allows you to manage a discovered [application](#app), or a currently unmanaged [cluster](#cluster).

```text
$ ./toolkit.py manage -h                
usage: toolkit.py manage [-h] {app,cluster} ...

optional arguments:
  -h, --help     show this help message and exit

objectType:
  {app,cluster}
    app          manage app
    cluster      manage cluster
```

## App

To define (or manage) an app, you must first gather the [namespace name](../list/README.md#namespaces) and [cluster ID](../list/README.md#clusters).  After an application is managed, it is recommended to [create a protectionpolicy](../create/README.md#protectionpolicy) for the app.

[Label selectors](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/) are optional strings to filter resources within a namespace to be included in or excluded from the application definition.  For instance, if you have multiple apps within the `default` namespace, label selectors allow you to define these applications separately within Astra Control.

Command usage:

```text
./toolkit.py manage app <appLogicalName> <namespaceName> <clusterID> <--labelSelectors optionalLabelSelectors>
```

Sample output:

```text
$ ./toolkit.py manage app wordpress wordpress b81bdd8f-c2c7-40eb-a602-4af06d3c6e4d
{"type": "application/astra-app", "version": "2.0", "id": "40f27720-5e6d-4ab7-8647-cc05f2019319", "name": "wordpress", "namespaceScopedResources": [{"namespace": "wordpress"}], "state": "discovering", "lastResourceCollectionTimestamp": "2022-07-25T14:21:48Z", "stateTransitions": [{"to": ["pending"]}, {"to": ["provisioning"]}, {"from": "pending", "to": ["discovering", "failed"]}, {"from": "discovering", "to": ["ready", "failed"]}, {"from": "ready", "to": ["discovering", "restoring", "unavailable", "failed"]}, {"from": "unavailable", "to": ["ready", "restoring"]}, {"from": "provisioning", "to": ["discovering", "failed"]}, {"from": "restoring", "to": ["discovering", "failed"]}], "stateDetails": [], "protectionState": "none", "protectionStateDetails": [], "namespaces": [], "clusterName": "uscentral1-cluster", "clusterID": "b81bdd8f-c2c7-40eb-a602-4af06d3c6e4d", "clusterType": "gke", "metadata": {"labels": [], "creationTimestamp": "2022-07-25T14:21:48Z", "modificationTimestamp": "2022-07-25T14:21:48Z", "createdBy": "12a5d9dd-851e-4235-af27-86c0b63bf3a9"}}
```

To use a single label, specify the `-l`/`--labelSelectors` argument and the [label selector](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/) of your choice, *without spaces*:

```text
$ ./toolkit.py manage app wordpress default -l app.kubernetes.io/instance=wordpress b81bdd8f-c2c7-40eb-a602-4af06d3c6e4d 
{"type": "application/astra-app", "version": "2.0", "id": "07c67881-ae5b-4091-a881-23be39ae72ae", "name": "wordpress", "namespaceScopedResources": [{"namespace": "default", "labelSelectors": ["app.kubernetes.io/instance=wordpress"]}], "state": "discovering", "lastResourceCollectionTimestamp": "2022-07-27T17:10:50Z", "stateTransitions": [{"to": ["pending"]}, {"to": ["provisioning"]}, {"from": "pending", "to": ["discovering", "failed"]}, {"from": "discovering", "to": ["ready", "failed"]}, {"from": "ready", "to": ["discovering", "restoring", "unavailable", "failed"]}, {"from": "unavailable", "to": ["ready", "restoring"]}, {"from": "provisioning", "to": ["discovering", "failed"]}, {"from": "restoring", "to": ["discovering", "failed"]}], "stateDetails": [], "protectionState": "none", "protectionStateDetails": [], "namespaces": [], "clusterName": "uscentral1-cluster", "clusterID": "b81bdd8f-c2c7-40eb-a602-4af06d3c6e4d", "clusterType": "gke", "metadata": {"labels": [], "creationTimestamp": "2022-07-27T17:10:50Z", "modificationTimestamp": "2022-07-27T17:10:50Z", "createdBy": "12a5d9dd-851e-4235-af27-86c0b63bf3a9"}}
```

Multiple labels utilize comma separation:

```text
$ ./toolkit.py manage app wordpress default -l app.kubernetes.io/name=wordpress,app.kubernetes.io/managed-by=Helm b81bdd8f-c2c7-40eb-a602-4af06d3c6e4d
{'clusterID': 'b81bdd8f-c2c7-40eb-a602-4af06d3c6e4d', 'name': 'wordpress', 'namespaceScopedResources': [{'namespace': 'default', 'labelSelectors': ['app.kubernetes.io/name=wordpress,app.kubernetes.io/managed-by=Helm']}], 'type': 'application/astra-app', 'version': '2.0'}
{"type": "application/astra-app", "version": "2.0", "id": "0d2fa973-4c9f-4e7b-9de3-2ac74c204a5c", "name": "wordpress", "namespaceScopedResources": [{"namespace": "default", "labelSelectors": ["app.kubernetes.io/name=wordpress,app.kubernetes.io/managed-by=Helm"]}], "state": "discovering", "lastResourceCollectionTimestamp": "2022-07-27T17:33:02Z", "stateTransitions": [{"to": ["pending"]}, {"to": ["provisioning"]}, {"from": "pending", "to": ["discovering", "failed"]}, {"from": "discovering", "to": ["ready", "failed"]}, {"from": "ready", "to": ["discovering", "restoring", "unavailable", "failed"]}, {"from": "unavailable", "to": ["ready", "restoring"]}, {"from": "provisioning", "to": ["discovering", "failed"]}, {"from": "restoring", "to": ["discovering", "failed"]}], "stateDetails": [], "protectionState": "none", "protectionStateDetails": [], "namespaces": [], "clusterName": "uscentral1-cluster", "clusterID": "b81bdd8f-c2c7-40eb-a602-4af06d3c6e4d", "clusterType": "gke", "metadata": {"labels": [], "creationTimestamp": "2022-07-27T17:33:02Z", "modificationTimestamp": "2022-07-27T17:33:02Z", "createdBy": "12a5d9dd-851e-4235-af27-86c0b63bf3a9"}}
```

Any label selectors which require spaces or characters that interfere with bash/zsh (for instance `!`) should be encased in quotes:

```text
$ ./toolkit.py manage app cassandra default -l 'tier notin (frontend)' b81bdd8f-c2c7-40eb-a602-4af06d3c6e4d
{"type": "application/astra-app", "version": "2.0", "id": "736d1231-807b-4ee2-ba51-e8a35a2829d3", "name": "cassandra", "namespaceScopedResources": [{"namespace": "default", "labelSelectors": ["tier notin (frontend)"]}], "state": "discovering", "lastResourceCollectionTimestamp": "2022-07-27T17:48:47Z", "stateTransitions": [{"to": ["pending"]}, {"to": ["provisioning"]}, {"from": "pending", "to": ["discovering", "failed"]}, {"from": "discovering", "to": ["ready", "failed"]}, {"from": "ready", "to": ["discovering", "restoring", "unavailable", "failed"]}, {"from": "unavailable", "to": ["ready", "restoring"]}, {"from": "provisioning", "to": ["discovering", "failed"]}, {"from": "restoring", "to": ["discovering", "failed"]}], "stateDetails": [], "protectionState": "none", "protectionStateDetails": [], "namespaces": [], "clusterName": "uscentral1-cluster", "clusterID": "b81bdd8f-c2c7-40eb-a602-4af06d3c6e4d", "clusterType": "gke", "metadata": {"labels": [], "creationTimestamp": "2022-07-27T17:48:47Z", "modificationTimestamp": "2022-07-27T17:48:47Z", "createdBy": "12a5d9dd-851e-4235-af27-86c0b63bf3a9"}}
```

```text
$ ./toolkit.py manage app cassandra default -l '!app' b81bdd8f-c2c7-40eb-a602-4af06d3c6e4d
{"type": "application/astra-app", "version": "2.0", "id": "8484c2b6-8496-41fb-b2d1-8bbb549609de", "name": "cassandra", "namespaceScopedResources": [{"namespace": "default", "labelSelectors": ["!app"]}], "state": "discovering", "lastResourceCollectionTimestamp": "2022-07-27T17:58:25Z", "stateTransitions": [{"to": ["pending"]}, {"to": ["provisioning"]}, {"from": "pending", "to": ["discovering", "failed"]}, {"from": "discovering", "to": ["ready", "failed"]}, {"from": "ready", "to": ["discovering", "restoring", "unavailable", "failed"]}, {"from": "unavailable", "to": ["ready", "restoring"]}, {"from": "provisioning", "to": ["discovering", "failed"]}, {"from": "restoring", "to": ["discovering", "failed"]}], "stateDetails": [], "protectionState": "none", "protectionStateDetails": [], "namespaces": [], "clusterName": "uscentral1-cluster", "clusterID": "b81bdd8f-c2c7-40eb-a602-4af06d3c6e4d", "clusterType": "gke", "metadata": {"labels": [], "creationTimestamp": "2022-07-27T17:58:25Z", "modificationTimestamp": "2022-07-27T17:58:25Z", "createdBy": "12a5d9dd-851e-4235-af27-86c0b63bf3a9"}}
```

## Cluster

To manage a cluster, you must gather the [cluster ID](../list/README.md#clusters), and a corresponding [storageclass ID](../list/README.md#storageclasses).  Command usage:

```text
./toolkit.py manage cluster <clusterID> <storageclassID>
```

Sample output:

```text
$ ./toolkit.py manage cluster 80d6bef8-300c-44bd-9e36-04ef874bdc29 \
    ba6d5a64-a321-4fd7-9842-9adce829229a
{"type": "application/astra-managedCluster", "version": "1.1", "id": "80d6bef8-300c-44bd-9e36-04ef874bdc29", "name": "aks-eastus-cluster", "state": "pending", "stateUnready": [], "managedState": "managed", "managedStateUnready": [], "managedTimestamp": "2022-05-19T20:33:59Z", "inUse": "false", "clusterType": "aks", "clusterVersion": "1.22", "clusterVersionString": "v1.22.6", "clusterCreationTimestamp": "0001-01-01T00:00:00Z", "namespaces": [], "defaultStorageClass": "ba6d5a64-a321-4fd7-9842-9adce829229a", "cloudID": "7b8d4252-293c-4c70-b101-7fd6b7d08e15", "credentialID": "04c067b2-df55-4d9c-8a3a-c869a779c276", "location": "eastus", "isMultizonal": "false", "metadata": {"labels": [{"name": "astra.netapp.io/labels/read-only/hasNonTridentCSIDriverSupport", "value": "true"}, {"name": "astra.netapp.io/labels/read-only/hasTridentDriverSupport", "value": "true"}, {"name": "astra.netapp.io/labels/read-only/azure/subscriptionID", "value": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxa2935"}, {"name": "astra.netapp.io/labels/read-only/cloudName", "value": "Azure"}], "creationTimestamp": "2022-05-19T20:33:59Z", "modificationTimestamp": "2022-05-19T20:34:03Z", "createdBy": "system"`
```
