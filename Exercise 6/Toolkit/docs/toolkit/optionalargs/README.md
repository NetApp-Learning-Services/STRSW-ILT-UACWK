# Optional Global Arguments

There are currently 4 global arguments that modify command output.  Most of these arguments (all but `--help`) should be placed immediately after `./toolkit.py` invocation, and before positional verbs (like deploy or clone):

* [Help](#help)
* [Verbose](#verbose)
* [Output](#output)
  * [Table](#table)
  * [Json](#json)
  * [Yaml](#yaml)
* [Quiet](#quiet)

## Help

The `--help` / `-h` argument can be utilized at any location within `./toolkit.py`.  If it's used immediately after `./toolkit.py`, then positional level arguments are shown.

```text
$ ./toolkit.py --help
usage: toolkit.py [-h] [-v] [-o {json,yaml,table}] [-q] {deploy,clone,restore,list,create,manage,destroy,unmanage} ...

positional arguments:
  {deploy,clone,restore,list,create,manage,destroy,unmanage}
                        subcommand help
    deploy              deploy a bitnami chart
    clone               clone a namespace to a destination cluster
    restore             restore an app from a backup or snapshot
    list (get)          List all items in a class
    create              Create an object
    manage              Manage an object
    destroy             Destroy an object
    unmanage            Unmanage an object

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         print verbose/verbose output
  -o {json,yaml,table}, --output {json,yaml,table}
                        command output format
  -q, --quiet           supress output
```

If utilized after positional arguments, then information about that specific command is shown.

```text
$ ./toolkit.py list --help
usage: toolkit.py list [-h] {apps,backups,clouds,clusters,snapshots,storageclasses} ...

optional arguments:
  -h, --help            show this help message and exit

objectType:
  {apps,backups,clouds,clusters,snapshots,storageclasses}
    apps                list apps
    backups             list backups
    clouds              list clouds
    clusters            list clusters
    snapshots           list snapshots
    storageclasses      list storageclasses
```

Additionally, if the positional arguments require sub-arguments, the `--help` displays further information.

```text
$ ./toolkit.py list apps -h
usage: toolkit.py list apps [-h] [-u | -i] [-s SOURCE] [-n NAMESPACE] [-c CLUSTER]

optional arguments:
  -h, --help            show this help message and exit
  -u, --unmanaged       Show only unmanaged apps
  -i, --ignored         Show ignored apps
  -s SOURCE, --source SOURCE
                        app source
  -n NAMESPACE, --namespace NAMESPACE
                        Only show apps from this namespace
  -c CLUSTER, --cluster CLUSTER
                        Only show apps from this cluster
```

## Verbose

The `--verbose` global argument prints additional output, such API call information (which is useful when modifying the `toolkit.py` or `astraSDK.py` files.  It **must** be placed immediately after the `./toolkit.py` invocation.

**Caution**: be mindful of running this command in front of others, as API credential information is displayed.

```text
API URL: https://hidden.astra.netapp.io/accounts/12345678-abcd-4567-8901-abcd01234567/topology/v1/apps
API Method: GET
API Headers: {'Authorization': 'Bearer KroeirTcUoMs6baBcUhXcAGK0-4tbm_ol1hJC2OtaDg='}
API data: {}
API params: {}
API HTTP Status Code: 200

+----------------+--------------------------------------+-----------------+----------------+--------------+-----------+
| appName        | appID                                | clusterName     | namespace      | state        | source    |
+================+======================================+=================+================+==============+===========+
| wordpress-east | 8f462cea-a166-438d-85b1-8aa5cfb0ad9f | useast1-cluster | wordpress      | running      | namespace |
+----------------+--------------------------------------+-----------------+----------------+--------------+-----------+
| wordpress-west | a8dc676e-d182-4d7c-9113-43f5a2963b54 | uswest1-cluster | wordpress-prod | running      | namespace |
+----------------+--------------------------------------+-----------------+----------------+--------------+-----------+
| temp-clone     | ad125374-e090-425b-a048-d719b93b0feb | uswest1-cluster | clonens        | provisioning | namespace |
+----------------+--------------------------------------+-----------------+----------------+--------------+-----------+
| jfrogcr        | cbffb71a-a96b-4c13-9d36-e1fbeac8aaa0 | uswest1-cluster | jfrogcr        | running      | namespace |
+----------------+--------------------------------------+-----------------+----------------+--------------+-----------+
```

## Output

The `--output {json,yaml,table`} argument modifies the output method of `list` commands.  The default option is `table`, which is most useful for manual `toolkit` operation.  The `json` and `yaml` are useful to gather more information about the various objects, and/or further automated processing.

### Table

The `table` output is the default option, so it's not necessary to explicitly use.

```text
$ ./toolkit.py -o table list apps
+----------------+--------------------------------------+-----------------+----------------+--------------+-----------+
| appName        | appID                                | clusterName     | namespace      | state        | source    | 
+================+======================================+=================+================+==============+===========+
| wordpress-east | 8f462cea-a166-438d-85b1-8aa5cfb0ad9f | useast1-cluster | wordpress      | running      | namespace | 
+----------------+--------------------------------------+-----------------+----------------+--------------+-----------+
| wordpress-west | a8dc676e-d182-4d7c-9113-43f5a2963b54 | uswest1-cluster | wordpress-prod | running      | namespace | 
+----------------+--------------------------------------+-----------------+----------------+--------------+-----------+
| temp-clone     | ad125374-e090-425b-a048-d719b93b0feb | uswest1-cluster | clonens        | provisioning | namespace | 
+----------------+--------------------------------------+-----------------+----------------+--------------+-----------+
| jfrogcr        | cbffb71a-a96b-4c13-9d36-e1fbeac8aaa0 | uswest1-cluster | jfrogcr        | running      | namespace | 
+----------------+--------------------------------------+-----------------+----------------+--------------+-----------+
```

### Json

The `json` output prints the full API object in json format.

```text
$ ./toolkit.py -o json list apps
{"items": [{"type": "application/astra-app", "version": "1.1", "id": "8f462cea-a166-438d-85b1-8aa5cfb0ad9f", "name": "wordpress", "state": "running", "stateUnready": [], "managedState": "managed", "managedStateUnready": [], "managedTimestamp": "2022-05-19T15:12:05Z", "protectionState": "protected", "protectionStateUnready": [], "collectionState": "fullyCollected", "collectionStateTransitions": [{"from": "notCollected", "to": ["partiallyCollected", "fullyCollected"]}, {"from": "partiallyCollected", "to": ["fullyCollected"]}, {"from": "fullyCollected", "to": []}], "collectionStateDetails": [], "appDefnSource": "namespace", "appLabels": [], "system": "false", "namespace": "wordpress", "clusterName": "useast1-cluster", "clusterID": "9fd690f3-4ae5-423d-9b58-95b6ba4f02e4", "clusterType": "gke", "metadata": {"labels": [], "creationTimestamp": "2022-05-19T15:11:31Z", "modificationTimestamp": "2022-05-20T18:15:00Z", "createdBy": "system"`, {"type": "application/astra-app", "version": "1.1", "id": "a8dc676e-d182-4d7c-9113-43f5a2963b54", "name": "wordpress-w", "state": "running", "stateUnready": [], "managedState": "managed", "managedStateUnready": [], "managedTimestamp": "2022-05-19T15:14:38Z", "protectionState": "partial", "protectionStateUnready": ["Missing a recent backup"], "collectionState": "fullyCollected", "collectionStateTransitions": [{"from": "notCollected", "to": ["partiallyCollected", "fullyCollected"]}, {"from": "partiallyCollected", "to": ["fullyCollected"]}, {"from": "fullyCollected", "to": []}], "collectionStateDetails": [], "appDefnSource": "namespace", "appLabels": [], "system": "false", "namespace": "wordpress-w", "clusterName": "uswest1-cluster", "clusterID": "c9456cae-b2d4-400b-ac53-60637d57da57", "clusterType": "gke", "metadata": {"labels": [], "creationTimestamp": "2022-05-19T15:14:13Z", "modificationTimestamp": "2022-05-20T18:15:00Z", "createdBy": "system"`, {"type": "application/astra-managedApp", "version": "1.1", "id": "ad125374-e090-425b-a048-d719b93b0feb", "name": "clonens", "state": "running", "stateUnready": [], "managedState": "managed", "managedStateUnready": [], "managedTimestamp": "2022-05-19T19:25:50Z", "protectionState": "none", "protectionStateUnready": [], "collectionState": "fullyCollected", "collectionStateTransitions": [{"from": "notCollected", "to": ["partiallyCollected", "fullyCollected"]}, {"from": "partiallyCollected", "to": ["fullyCollected"]}, {"from": "fullyCollected", "to": []}], "collectionStateDetails": [], "appDefnSource": "namespace", "appLabels": [], "system": "false", "namespace": "clonens", "clusterName": "uswest1-cluster", "clusterID": "c9456cae-b2d4-400b-ac53-60637d57da57", "clusterType": "gke", "sourceAppID": "8f462cea-a166-438d-85b1-8aa5cfb0ad9f", "sourceClusterID": "9fd690f3-4ae5-423d-9b58-95b6ba4f02e4", "backupID": "fa8b87a2-8533-4fec-82dd-dd9cbeec2c9b", "metadata": {"labels": [{"name": "astra.netapp.io/labels/read-only/appType", "value": "clone"}], "creationTimestamp": "2022-05-19T19:25:50Z", "modificationTimestamp": "2022-05-20T18:15:00Z", "createdBy": "8146d293-d897-4e16-ab10-8dca934637ab"`, {"type": "application/astra-app", "version": "1.1", "id": "cbffb71a-a96b-4c13-9d36-e1fbeac8aaa0", "name": "jfrogcr", "state": "running", "stateUnready": [], "managedState": "managed", "managedStateUnready": [], "managedTimestamp": "2022-05-20T16:00:06Z", "protectionState": "protected", "protectionStateUnready": [], "collectionState": "fullyCollected", "collectionStateTransitions": [{"from": "notCollected", "to": ["partiallyCollected", "fullyCollected"]}, {"from": "partiallyCollected", "to": ["fullyCollected"]}, {"from": "fullyCollected", "to": []}], "collectionStateDetails": [], "appDefnSource": "namespace", "appLabels": [], "system": "false", "namespace": "jfrogcr", "clusterName": "uswest1-cluster", "clusterID": "c9456cae-b2d4-400b-ac53-60637d57da57", "clusterType": "gke", "metadata": {"labels": [], "creationTimestamp": "2022-05-20T15:59:35Z", "modificationTimestamp": "2022-05-20T18:15:00Z", "createdBy": "system"`], "metadata": {`
```

This is useful in conjunction with the [jq](https://stedolan.github.io/jq/) utility, first for pretty-printing the output:

```text
$ ./toolkit.py -o json list apps | jq
{
  "items": [
    {
      "type": "application/astra-app",
      "version": "1.1",
      "id": "8f462cea-a166-438d-85b1-8aa5cfb0ad9f",
      "name": "wordpress-east",
      "state": "running",
      "stateUnready": [],
      "managedState": "managed",
      "managedStateUnready": [],
      "managedTimestamp": "2022-05-19T15:12:05Z",
      "protectionState": "protected",
      "protectionStateUnready": [],
      "collectionState": "fullyCollected",
      "collectionStateTransitions": [
        {
          "from": "notCollected",
          "to": [
            "partiallyCollected",
            "fullyCollected"
          ]
        },
        {
          "from": "partiallyCollected",
          "to": [
            "fullyCollected"
          ]
        },
        {
          "from": "fullyCollected",
          "to": []
        }
      ],
      "collectionStateDetails": [],
      "appDefnSource": "namespace",
      "appLabels": [],
      "system": "false",
      "namespace": "wordpress",
      "clusterName": "useast1-cluster",
      "clusterID": "9fd690f3-4ae5-423d-9b58-95b6ba4f02e4",
      "clusterType": "gke",
      "metadata": {
        "labels": [],
        "creationTimestamp": "2022-05-19T15:11:31Z",
        "modificationTimestamp": "2022-05-20T18:18:15Z",
        "createdBy": "system"
      }
    },
    {
      "type": "application/astra-app",
      "version": "1.1",
      "id": "a8dc676e-d182-4d7c-9113-43f5a2963b54",
      "name": "wordpress-west",
      "state": "running",
      "stateUnready": [],
      "managedState": "managed",
      "managedStateUnready": [],
      "managedTimestamp": "2022-05-19T15:14:38Z",
      "protectionState": "none",
      "protectionStateUnready": [],
      "collectionState": "fullyCollected",
      "collectionStateTransitions": [
        {
          "from": "notCollected",
          "to": [
            "partiallyCollected",
            "fullyCollected"
          ]
        },
        {
          "from": "partiallyCollected",
          "to": [
            "fullyCollected"
          ]
        },
        {
          "from": "fullyCollected",
          "to": []
        }
      ],
      "collectionStateDetails": [],
      "appDefnSource": "namespace",
      "appLabels": [],
      "system": "false",
      "namespace": "wordpress-prod",
      "clusterName": "uswest1-cluster",
      "clusterID": "c9456cae-b2d4-400b-ac53-60637d57da57",
      "clusterType": "gke",
      "metadata": {
        "labels": [],
        "creationTimestamp": "2022-05-19T15:14:13Z",
        "modificationTimestamp": "2022-05-20T18:18:15Z",
        "createdBy": "system"
      }
    },
    {
      "type": "application/astra-managedApp",
      "version": "1.1",
      "id": "ad125374-e090-425b-a048-d719b93b0feb",
      "name": "temp-clone",
      "state": "running",
      "stateUnready": [],
      "managedState": "managed",
      "managedStateUnready": [],
      "managedTimestamp": "2022-05-19T19:25:50Z",
      "protectionState": "none",
      "protectionStateUnready": [],
      "collectionState": "fullyCollected",
      "collectionStateTransitions": [
        {
          "from": "notCollected",
          "to": [
            "partiallyCollected",
            "fullyCollected"
          ]
        },
        {
          "from": "partiallyCollected",
          "to": [
            "fullyCollected"
          ]
        },
        {
          "from": "fullyCollected",
          "to": []
        }
      ],
      "collectionStateDetails": [],
      "appDefnSource": "namespace",
      "appLabels": [],
      "system": "false",
      "namespace": "clonens",
      "clusterName": "uswest1-cluster",
      "clusterID": "c9456cae-b2d4-400b-ac53-60637d57da57",
      "clusterType": "gke",
      "sourceAppID": "8f462cea-a166-438d-85b1-8aa5cfb0ad9f",
      "sourceClusterID": "9fd690f3-4ae5-423d-9b58-95b6ba4f02e4",
      "backupID": "fa8b87a2-8533-4fec-82dd-dd9cbeec2c9b",
      "metadata": {
        "labels": [
          {
            "name": "astra.netapp.io/labels/read-only/appType",
            "value": "clone"
          }
        ],
        "creationTimestamp": "2022-05-19T19:25:50Z",
        "modificationTimestamp": "2022-05-20T18:18:15Z",
        "createdBy": "8146d293-d897-4e16-ab10-8dca934637ab"
      }
    },
    {
      "type": "application/astra-app",
      "version": "1.1",
      "id": "cbffb71a-a96b-4c13-9d36-e1fbeac8aaa0",
      "name": "jfrogcr",
      "state": "running",
      "stateUnready": [],
      "managedState": "managed",
      "managedStateUnready": [],
      "managedTimestamp": "2022-05-20T16:00:06Z",
      "protectionState": "none",
      "protectionStateUnready": [],
      "collectionState": "fullyCollected",
      "collectionStateTransitions": [
        {
          "from": "notCollected",
          "to": [
            "partiallyCollected",
            "fullyCollected"
          ]
        },
        {
          "from": "partiallyCollected",
          "to": [
            "fullyCollected"
          ]
        },
        {
          "from": "fullyCollected",
          "to": []
        }
      ],
      "collectionStateDetails": [],
      "appDefnSource": "namespace",
      "appLabels": [],
      "system": "false",
      "namespace": "jfrogcr",
      "clusterName": "uswest1-cluster",
      "clusterID": "c9456cae-b2d4-400b-ac53-60637d57da57",
      "clusterType": "gke",
      "metadata": {
        "labels": [],
        "creationTimestamp": "2022-05-20T15:59:35Z",
        "modificationTimestamp": "2022-05-20T18:18:15Z",
        "createdBy": "system"
      }
    }
  ],
  "metadata": {}
}
```

Second, it can be used to extract certain information, for instance if you wanted to determine the `protectionState` of your managed applications:

```text
$ ./toolkit.py -o json list apps | jq '.items[] | {id, name, protectionState}'
{
  "id": "8f462cea-a166-438d-85b1-8aa5cfb0ad9f",
  "name": "wordpress-east",
  "protectionState": "protected"
}
{
  "id": "a8dc676e-d182-4d7c-9113-43f5a2963b54",
  "name": "wordpress-west",
  "protectionState": "none"
}
{
  "id": "ad125374-e090-425b-a048-d719b93b0feb",
  "name": "clonens",
  "protectionState": "none"
}
{
  "id": "cbffb71a-a96b-4c13-9d36-e1fbeac8aaa0",
  "name": "jfrogcr",
  "protectionState": "none"
}
```

Lastly, it's useful for short shell scripts which require multiple object IDs.  For instance, say you wanted to [destroy](../destroy/README.md) all [snapshots](../destroy/README.md#snapshot) for a particular application.

You can first just gather the snapshot IDs:

```text
$ ./toolkit.py -o json list snapshots --app cbffb71a-a96b-4c13-9d36-e1fbeac8aaa0 \
    | jq -r '.items[].id'
4e0c53cc-820b-4935-a65a-c89f665e7fbd
5700cc40-f446-46a1-ab36-bc053616d84e
```

You can then enclose that command in a simple for loop:

```text
$ for i in `tk -o json list snapshots --app cbffb71a-a96b-4c13-9d36-e1fbeac8aaa0 \
    | jq -r '.items[].id'`; do echo "=== destroying snapshot $i ==="; ./toolkit.py destroy \
    snapshot cbffb71a-a96b-4c13-9d36-e1fbeac8aaa0 $i; done
=== destroying snapshot 4e0c53cc-820b-4935-a65a-c89f665e7fbd ===
Snapshot 4e0c53cc-820b-4935-a65a-c89f665e7fbd destroyed
=== destroying snapshot 5700cc40-f446-46a1-ab36-bc053616d84e ===
Snapshot 5700cc40-f446-46a1-ab36-bc053616d84e destroyed
```

Or, say you wanted to [protect](../create/README.md#protectionpolicy) all of your apps that are currently unprotected:

```text
$ for i in `./toolkit.py -o json list apps \
    | jq -r '.items[] | select(.protectionState == "none") | {id} | join(" ")'`; \
    do echo "=== protecting app $i ==="; \
    ./toolkit.py create protectionpolicy $i -g hourly -b 2 -s 3; done
=== protecting app a8dc676e-d182-4d7c-9113-43f5a2963b54 ===
{"type": "application/astra-schedule", "version": "1.1", "id": "a8dc676e-d182-4d7c-9113-43f5a2963b54", "name": "hourly-trpvk", "enabled": "true", "granularity": "hourly", "minute": "0", "snapshotRetention": "3", "backupRetention": "2", "metadata": {"labels": [], "creationTimestamp": "2022-05-24T20:24:14Z", "modificationTimestamp": "2022-05-24T20:24:14Z", "createdBy": "8146d293-d897-4e16-ab10-8dca934637ab"}}
=== protecting app ad125374-e090-425b-a048-d719b93b0feb ===
{"type": "application/astra-schedule", "version": "1.1", "id": "ad125374-e090-425b-a048-d719b93b0feb", "name": "hourly-d4bcx", "enabled": "true", "granularity": "hourly", "minute": "0", "snapshotRetention": "3", "backupRetention": "2", "metadata": {"labels": [], "creationTimestamp": "2022-05-24T20:24:15Z", "modificationTimestamp": "2022-05-24T20:24:15Z", "createdBy": "8146d293-d897-4e16-ab10-8dca934637ab"}}
=== protecting app cbffb71a-a96b-4c13-9d36-e1fbeac8aaa0 ===
{"type": "application/astra-schedule", "version": "1.1", "id": "cbffb71a-a96b-4c13-9d36-e1fbeac8aaa0", "name": "hourly-r8pr3", "enabled": "true", "granularity": "hourly", "minute": "0", "snapshotRetention": "3", "backupRetention": "2", "metadata": {"labels": [], "creationTimestamp": "2022-05-24T20:24:17Z", "modificationTimestamp": "2022-05-24T20:24:17Z", "createdBy": "8146d293-d897-4e16-ab10-8dca934637ab"}}
```

### Yaml

If you prefer `yaml` over json, the `--output yaml` argument can be utilized.  It can also be used in conjunction with [yq](https://github.com/mikefarah/yq) in similar fashion as jq.

```text
$ ./toolkit.py -o yaml list clusters
items:
- cloudID: 0ec2e027-80bc-426a-b844-692de243b29e
  clusterCreationTimestamp: '2022-05-16T15:51:54Z'
  clusterType: gke
  clusterVersion: '1.21'
  clusterVersionString: v1.21.10-gke.2000
  defaultStorageClass: 0f17bdd2-38e0-4f10-a351-9844de4243ee
  id: c9456cae-b2d4-400b-ac53-60637d57da57
  inUse: 'true'
  isMultizonal: 'true'
  location: us-west1-b
  managedState: managed
  managedStateUnready: []
  managedTimestamp: '2022-05-19T15:08:10Z'
  metadata:
    createdBy: system
    creationTimestamp: '2022-05-16T16:00:21Z'
    labels:
    - name: astra.netapp.io/labels/read-only/hasTridentDriverSupport
      value: 'true'
    - name: astra.netapp.io/labels/read-only/gcp/projectNumber
      value: '239048101169'
    - name: astra.netapp.io/labels/read-only/gcp/HostVpcProjectID
      value: xxxxxxx01169
    - name: astra.netapp.io/labels/read-only/hasNonTridentCSIDriverSupport
      value: 'true'
    - name: astra.netapp.io/labels/read-only/cloudName
      value: GCP
    modificationTimestamp: '2022-05-20T18:51:22Z'
  name: uswest1-cluster
  namespaces:
  - clonens
  - default
  - hourly-vydir-n1hfv
  - jfrogcr
  - kube-node-lease
  - kube-public
  - kube-system
  - trident
  - wordpress-w
  state: running
  stateUnready: []
  tridentVersion: 22.01.0
  type: application/astra-cluster
  version: '1.1'
- cloudID: 0ec2e027-80bc-426a-b844-692de243b29e
  clusterCreationTimestamp: '2022-05-16T16:06:34Z'
  clusterType: gke
  clusterVersion: '1.21'
  clusterVersionString: v1.21.10-gke.2000
  defaultStorageClass: 0f17bdd2-38e0-4f10-a351-9844de4243ee
  id: 9fd690f3-4ae5-423d-9b58-95b6ba4f02e4
  inUse: 'true'
  isMultizonal: 'true'
  location: us-east1-b
  managedState: managed
  managedStateUnready: []
  managedTimestamp: '2022-05-19T15:09:04Z'
  metadata:
    createdBy: 8146d293-d897-4e16-ab10-8dca934637ab
    creationTimestamp: '2022-05-16T16:09:26Z'
    labels:
    - name: astra.netapp.io/labels/read-only/gcp/HostVpcProjectID
      value: xxxxxxx01169
    - name: astra.netapp.io/labels/read-only/gcp/projectNumber
      value: '239048101169'
    - name: astra.netapp.io/labels/read-only/hasNonTridentCSIDriverSupport
      value: 'true'
    - name: astra.netapp.io/labels/read-only/hasTridentDriverSupport
      value: 'true'
    - name: astra.netapp.io/labels/read-only/cloudName
      value: GCP
    modificationTimestamp: '2022-05-20T18:51:22Z'
  name: useast1-cluster
  namespaces:
  - default
  - kube-node-lease
  - kube-public
  - kube-system
  - trident
  - wordpress
  state: running
  stateUnready: []
  tridentVersion: 22.01.0
  type: application/astra-cluster
  version: '1.1'
```

## Quiet

The `--quiet` argument suppresses output, while still utilizing proper exit codes, and throwing error messages for incorrect commands.  Consider this command (without the `--quiet` argument):

```text
$ ./toolkit.py manage app 1d16c9f0-1b7f-4f21-804c-4162b0cfd56e 
{"type": "application/astra-managedApp", "version": "1.1", "id": "1d16c9f0-1b7f-4f21-804c-4162b0cfd56e", "name": "jfrogcr-artifactory", "state": "running", "stateUnready": [], "managedState": "managed", "managedStateUnready": [], "managedTimestamp": "2022-05-20T18:52:51Z", "protectionState": "none", "protectionStateUnready": [], "collectionState": "fullyCollected", "collectionStateTransitions": [{"from": "notCollected", "to": ["partiallyCollected", "fullyCollected"]}, {"from": "partiallyCollected", "to": ["fullyCollected"]}, {"from": "fullyCollected", "to": []}], "collectionStateDetails": [], "appDefnSource": "helm", "appLabels": [{"name": "app", "value": "artifactory"}, {"name": "release", "value": "jfrogcr"}], "system": "false", "pods": [{"podName": "jfrogcr-artifactory-0", "podNamespace": "jfrogcr", "nodeName": "gke-uswest1-cluster-default-node-pool-3ee0f741-kkxr", "containers": [{"containerName": "artifactory", "image": "releases-docker.jfrog.io/jfrog/artifactory-jcr:7.38.10", "containerState": "available", "containerStateUnready": []}], "podState": "available", "podStateUnready": [], "podLabels": [{"name": "release", "value": "jfrogcr"}, {"name": "role", "value": "artifactory"}, {"name": "statefulset.kubernetes.io/pod-name", "value": "jfrogcr-artifactory-0"}, {"name": "app", "value": "artifactory"}, {"name": "chart", "value": "artifactory-107.38.10"}, {"name": "component", "value": "artifactory"}, {"name": "controller-revision-hash", "value": "jfrogcr-artifactory-585f5f66f6"}, {"name": "heritage", "value": "Helm"}], "podCreationTimestamp": "2022-05-20T15:58:53Z"}, {"podName": "jfrogcr-artifactory-nginx-748d4c8894-ntcjp", "podNamespace": "jfrogcr", "nodeName": "gke-uswest1-cluster-default-node-pool-3ee0f741-stm6", "containers": [{"containerName": "nginx", "image": "releases-docker.jfrog.io/jfrog/nginx-artifactory-pro:7.38.10", "containerState": "provisioning", "containerStateUnready": ["Container 'nginx' is not ready"]}], "podState": "provisioning", "podStateUnready": ["Ready condition is false: containers with unready status: [nginx]", "ContainersReady condition is false: containers with unready status: [nginx]", "Container 'nginx' is not ready"], "podLabels": [{"name": "heritage", "value": "Helm"}, {"name": "pod-template-hash", "value": "748d4c8894"}, {"name": "release", "value": "jfrogcr"}, {"name": "app", "value": "artifactory"}, {"name": "chart", "value": "artifactory-107.38.10"}, {"name": "component", "value": "nginx"}], "podCreationTimestamp": "2022-05-20T15:58:53Z"}], "namespace": "jfrogcr", "clusterName": "uswest1-cluster", "clusterID": "c9456cae-b2d4-400b-ac53-60637d57da57", "clusterType": "gke", "metadata": {"labels": [], "creationTimestamp": "2022-05-20T15:59:36Z", "modificationTimestamp": "2022-05-20T17:13:12Z", "createdBy": "system"`
```

With the `--quiet` argument instead:

```text
$ ./toolkit --quiet manage app 1d16c9f0-1b7f-4f21-804c-4162b0cfd56e
$ echo $?
0
```

While incorrect commands still display output even with the `--quiet` argument:

```text
$ ./toolkit --quiet manage app 11111111-1111-1111-1111-111111111111
usage: toolkit.py manage app [-h]
                             {d00964bb-8d83-4151-99e8-7d31fb7e0611,5cd31c6a-2f3e-434b-8649-735569637c4b,a1a4b844-f2c4-4047-a886-ddfa80a12c2d,ded34e23-02ec-47f5-9702-0afb413b344e,125e9d1e-a278-491f-b278-134edf38d44c,ac374e80-4acb-41d5-8276-096b0259be00,df32149a-1fe7-4e1a-89dc-6201343ee6f0}
toolkit.py manage app: error: argument appID: invalid choice: '11111111-1111-1111-1111-111111111111' (choose from 'd00964bb-8d83-4151-99e8-7d31fb7e0611', '5cd31c6a-2f3e-434b-8649-735569637c4b', 'a1a4b844-f2c4-4047-a886-ddfa80a12c2d', 'ded34e23-02ec-47f5-9702-0afb413b344e', '125e9d1e-a278-491f-b278-134edf38d44c', 'ac374e80-4acb-41d5-8276-096b0259be00', 'df32149a-1fe7-4e1a-89dc-6201343ee6f0')
$ echo $?
2
```
