# Manage

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

To manage an app, you must first gather the [app ID](../list/README.md#apps).  The app must be in a "discovered" state, not in an "ignored" state.  After an application is managed, it is recommended to [create a protectionpolicy](../create/README.md#protectionpolicy) for the app.

Command usage:

```text
./toolkit.py manage app <appID>
```

Sample output:

```text
$ ./toolkit.py manage app 1d16c9f0-1b7f-4f21-804c-4162b0cfd56e
{"type": "application/astra-managedApp", "version": "1.1", "id": "1d16c9f0-1b7f-4f21-804c-4162b0cfd56e", "name": "jfrogcr-artifactory", "state": "running", "stateUnready": [], "managedState": "managed", "managedStateUnready": [], "managedTimestamp": "2022-05-20T17:13:19Z", "protectionState": "none", "protectionStateUnready": [], "collectionState": "fullyCollected", "collectionStateTransitions": [{"from": "notCollected", "to": ["partiallyCollected", "fullyCollected"]}, {"from": "partiallyCollected", "to": ["fullyCollected"]}, {"from": "fullyCollected", "to": []}], "collectionStateDetails": [], "appDefnSource": "helm", "appLabels": [{"name": "app", "value": "artifactory"}, {"name": "release", "value": "jfrogcr"}], "system": "false", "pods": [{"podName": "jfrogcr-artifactory-0", "podNamespace": "jfrogcr", "nodeName": "gke-uswest1-cluster-default-node-pool-3ee0f741-kkxr", "containers": [{"containerName": "artifactory", "image": "releases-docker.jfrog.io/jfrog/artifactory-jcr:7.38.10", "containerState": "available", "containerStateUnready": []}], "podState": "available", "podStateUnready": [], "podLabels": [{"name": "release", "value": "jfrogcr"}, {"name": "role", "value": "artifactory"}, {"name": "statefulset.kubernetes.io/pod-name", "value": "jfrogcr-artifactory-0"}, {"name": "app", "value": "artifactory"}, {"name": "chart", "value": "artifactory-107.38.10"}, {"name": "component", "value": "artifactory"}, {"name": "controller-revision-hash", "value": "jfrogcr-artifactory-585f5f66f6"}, {"name": "heritage", "value": "Helm"}], "podCreationTimestamp": "2022-05-20T15:58:53Z"}, {"podName": "jfrogcr-artifactory-nginx-748d4c8894-ntcjp", "podNamespace": "jfrogcr", "nodeName": "gke-uswest1-cluster-default-node-pool-3ee0f741-stm6", "containers": [{"containerName": "nginx", "image": "releases-docker.jfrog.io/jfrog/nginx-artifactory-pro:7.38.10", "containerState": "provisioning", "containerStateUnready": ["Container 'nginx' is not ready"]}], "podState": "provisioning", "podStateUnready": ["Ready condition is false: containers with unready status: [nginx]", "ContainersReady condition is false: containers with unready status: [nginx]", "Container 'nginx' is not ready"], "podLabels": [{"name": "pod-template-hash", "value": "748d4c8894"}, {"name": "release", "value": "jfrogcr"}, {"name": "app", "value": "artifactory"}, {"name": "chart", "value": "artifactory-107.38.10"}, {"name": "component", "value": "nginx"}, {"name": "heritage", "value": "Helm"}], "podCreationTimestamp": "2022-05-20T15:58:53Z"}], "namespace": "jfrogcr", "clusterName": "uswest1-cluster", "clusterID": "c9456cae-b2d4-400b-ac53-60637d57da57", "clusterType": "gke", "metadata": {"labels": [], "creationTimestamp": "2022-05-20T15:59:36Z", "modificationTimestamp": "2022-05-20T17:13:12Z", "createdBy": "system"`
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
