# Optional Global Arguments

There are currently 4 global arguments that modify command output.  Most of these arguments (all but `--help`) should be placed immediately after `./toolkit.py` invocation, and before positional verbs (like deploy or clone):

* [Help](#help)
* [Verbose](#verbose)
* [Output](#output)
  * [Table](#table)
  * [Json](#json)
  * [Yaml](#yaml)
* [Quiet](#quiet)
* [Fast](#fast)

## Help

The `--help` / `-h` argument can be utilized at any location within `./toolkit.py`.  If it's used immediately after `./toolkit.py`, then positional level arguments are shown.

```text
$ ./toolkit.py --help
usage: toolkit.py [-h] [-v] [-o {json,yaml,table}] [-q] {deploy,clone,restore,list,get,create,manage,define,destroy,unmanage} ...

positional arguments:
  {deploy,clone,restore,list,get,create,manage,define,destroy,unmanage}
                        subcommand help
    deploy              Deploy a helm chart
    clone               Clone an app
    restore             Restore an app from a backup or snapshot
    list (get)          List all items in a class
    create              Create an object
    manage (define)     Manage an object
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
usage: toolkit.py list [-h] {apps,backups,clouds,clusters,namespaces,snapshots,storageclasses} ...

optional arguments:
  -h, --help            show this help message and exit

objectType:
  {apps,backups,clouds,clusters,namespaces,snapshots,storageclasses}
    apps                list apps
    backups             list backups
    clouds              list clouds
    clusters            list clusters
    namespaces          list namespaces
    snapshots           list snapshots
    storageclasses      list storageclasses
```

Additionally, if the positional arguments require sub-arguments, the `--help` displays further information.

```text
usage: toolkit.py list apps [-h] [-n NAMESPACE] [-c CLUSTER]

optional arguments:
  -h, --help            show this help message and exit
  -n NAMESPACE, --namespace NAMESPACE
                        Only show apps from this namespace
  -c CLUSTER, --cluster CLUSTER
                        Only show apps from this cluster
```

## Verbose

The `--verbose` global argument prints additional output, such API call information (which is useful when modifying the `toolkit.py` or `astraSDK.py` files.  It **must** be placed immediately after the `./toolkit.py` invocation.

**Caution**: be mindful of running this command in front of others, as API credential information is displayed.

```text
$ ./toolkit.py --verbose list apps
API URL: https://hidden.astra.netapp.io/accounts/737c6a6e-930f-48ce-82ba-afcafc0633dd/k8s/v2/apps
API Method: GET
API Headers: {'Authorization': 'Bearer KroeirTcUoMs6baBcUhXcAGK0-4tbm_ol1hJC2OtaDg='}
API data: {}
API params: {}
API HTTP Status Code: 200

+------------------------------+--------------------------------------+--------------------+-------------+--------------+
| appName                      | appID                                | clusterName        | namespace   | state        |
+==============================+======================================+====================+=============+==============+
| wordpress                    | 79c608be-828d-4b3b-92d4-5589c0a4e515 | uscentral1-cluster | wordpress   | ready        |
+------------------------------+--------------------------------------+--------------------+-------------+--------------+
| cassandra                    | 79871ad1-2f69-4532-806a-42ba11cc45ac | uscentral1-cluster | cassandra   | ready        |
+------------------------------+--------------------------------------+--------------------+-------------+--------------+
| wordpress-clone-202207271713 | 7c212175-9cbd-4bb9-96a4-3a61a8ea0fda | useast4-cluster    |             | provisioning |
+------------------------------+--------------------------------------+--------------------+-------------+--------------+
```

## Output

The `--output {json,yaml,table`} argument modifies the output method of `list` commands.  The default option is `table`, which is most useful for manual `toolkit` operation.  The `json` and `yaml` are useful to gather more information about the various objects, and/or further automated processing.

### Table

The `table` output is the default option, so it's not necessary to explicitly use.

```text
$ ./toolkit.py -o table list apps
+------------------------------+--------------------------------------+--------------------+-------------+--------------+
| appName                      | appID                                | clusterName        | namespace   | state        |
+==============================+======================================+====================+=============+==============+
| wordpress                    | 79c608be-828d-4b3b-92d4-5589c0a4e515 | uscentral1-cluster | wordpress   | ready        |
+------------------------------+--------------------------------------+--------------------+-------------+--------------+
| cassandra                    | 79871ad1-2f69-4532-806a-42ba11cc45ac | uscentral1-cluster | cassandra   | ready        |
+------------------------------+--------------------------------------+--------------------+-------------+--------------+
| wordpress-clone-202207271713 | 7c212175-9cbd-4bb9-96a4-3a61a8ea0fda | useast4-cluster    |             | provisioning |
+------------------------------+--------------------------------------+--------------------+-------------+--------------+
```

### Json

The `json` output prints the full API object in json format.

```text
$ ./toolkit.py -o json list apps
{"items": [{"type": "application/astra-app", "version": "2.0", "id": "79c608be-828d-4b3b-92d4-5589c0a4e515", "name": "wordpress", "namespaceScopedResources": [{"namespace": "wordpress"}], "state": "ready", "lastResourceCollectionTimestamp": "2022-07-27T21:09:26Z", "stateTransitions": [{"to": ["pending"]}, {"to": ["provisioning"]}, {"from": "pending", "to": ["discovering", "failed"]}, {"from": "discovering", "to": ["ready", "failed"]}, {"from": "ready", "to": ["discovering", "restoring", "unavailable", "failed"]}, {"from": "unavailable", "to": ["ready", "restoring"]}, {"from": "provisioning", "to": ["discovering", "failed"]}, {"from": "restoring", "to": ["discovering", "failed"]}], "stateDetails": [], "protectionState": "partial", "protectionStateDetails": [], "namespaces": ["wordpress"], "clusterName": "uscentral1-cluster", "clusterID": "b81bdd8f-c2c7-40eb-a602-4af06d3c6e4d", "clusterType": "gke", "metadata": {"labels": [], "creationTimestamp": "2022-07-27T21:07:28Z", "modificationTimestamp": "2022-07-27T21:09:54Z", "createdBy": "12a5d9dd-851e-4235-af27-86c0b63bf3a9"}}, {"type": "application/astra-app", "version": "2.0", "id": "79871ad1-2f69-4532-806a-42ba11cc45ac", "name": "cassandra", "namespaceScopedResources": [{"namespace": "cassandra", "labelSelectors": ["app.kubernetes.io/instance=cassandra"]}], "state": "ready", "lastResourceCollectionTimestamp": "2022-07-27T21:09:31Z", "stateTransitions": [{"to": ["pending"]}, {"to": ["provisioning"]}, {"from": "pending", "to": ["discovering", "failed"]}, {"from": "discovering", "to": ["ready", "failed"]}, {"from": "ready", "to": ["discovering", "restoring", "unavailable", "failed"]}, {"from": "unavailable", "to": ["ready", "restoring"]}, {"from": "provisioning", "to": ["discovering", "failed"]}, {"from": "restoring", "to": ["discovering", "failed"]}], "stateDetails": [], "protectionState": "partial", "protectionStateDetails": [], "namespaces": ["cassandra"], "clusterName": "uscentral1-cluster", "clusterID": "b81bdd8f-c2c7-40eb-a602-4af06d3c6e4d", "clusterType": "gke", "metadata": {"labels": [], "creationTimestamp": "2022-07-27T21:07:33Z", "modificationTimestamp": "2022-07-27T21:09:54Z", "createdBy": "12a5d9dd-851e-4235-af27-86c0b63bf3a9"}}], "metadata": {}}
```

This is useful in conjunction with the [jq](https://stedolan.github.io/jq/) utility, first for pretty-printing the output:

```text
$ ./toolkit.py -o json list apps | jq
{
  "items": [
    {
      "type": "application/astra-app",
      "version": "2.0",
      "id": "79c608be-828d-4b3b-92d4-5589c0a4e515",
      "name": "wordpress",
      "namespaceScopedResources": [
        {
          "namespace": "wordpress"
        }
      ],
      "state": "ready",
      "lastResourceCollectionTimestamp": "2022-07-27T21:09:26Z",
      "stateTransitions": [
        {
          "to": [
            "pending"
          ]
        },
        {
          "to": [
            "provisioning"
          ]
        },
        {
          "from": "pending",
          "to": [
            "discovering",
            "failed"
          ]
        },
        {
          "from": "discovering",
          "to": [
            "ready",
            "failed"
          ]
        },
        {
          "from": "ready",
          "to": [
            "discovering",
            "restoring",
            "unavailable",
            "failed"
          ]
        },
        {
          "from": "unavailable",
          "to": [
            "ready",
            "restoring"
          ]
        },
        {
          "from": "provisioning",
          "to": [
            "discovering",
            "failed"
          ]
        },
        {
          "from": "restoring",
          "to": [
            "discovering",
            "failed"
          ]
        }
      ],
      "stateDetails": [],
      "protectionState": "protected",
      "protectionStateDetails": [],
      "namespaces": [
        "wordpress"
      ],
      "clusterName": "uscentral1-cluster",
      "clusterID": "b81bdd8f-c2c7-40eb-a602-4af06d3c6e4d",
      "clusterType": "gke",
      "metadata": {
        "labels": [],
        "creationTimestamp": "2022-07-27T21:07:28Z",
        "modificationTimestamp": "2022-07-27T21:20:03Z",
        "createdBy": "12a5d9dd-851e-4235-af27-86c0b63bf3a9"
      }
    },
    {
      "type": "application/astra-app",
      "version": "2.0",
      "id": "79871ad1-2f69-4532-806a-42ba11cc45ac",
      "name": "cassandra",
      "namespaceScopedResources": [
        {
          "namespace": "cassandra",
          "labelSelectors": [
            "app.kubernetes.io/instance=cassandra"
          ]
        }
      ],
      "state": "ready",
      "lastResourceCollectionTimestamp": "2022-07-27T21:16:27Z",
      "stateTransitions": [
        {
          "to": [
            "pending"
          ]
        },
        {
          "to": [
            "provisioning"
          ]
        },
        {
          "from": "pending",
          "to": [
            "discovering",
            "failed"
          ]
        },
        {
          "from": "discovering",
          "to": [
            "ready",
            "failed"
          ]
        },
        {
          "from": "ready",
          "to": [
            "discovering",
            "restoring",
            "unavailable",
            "failed"
          ]
        },
        {
          "from": "unavailable",
          "to": [
            "ready",
            "restoring"
          ]
        },
        {
          "from": "provisioning",
          "to": [
            "discovering",
            "failed"
          ]
        },
        {
          "from": "restoring",
          "to": [
            "discovering",
            "failed"
          ]
        }
      ],
      "stateDetails": [],
      "protectionState": "partial",
      "protectionStateDetails": [],
      "namespaces": [
        "cassandra"
      ],
      "clusterName": "uscentral1-cluster",
      "clusterID": "b81bdd8f-c2c7-40eb-a602-4af06d3c6e4d",
      "clusterType": "gke",
      "metadata": {
        "labels": [],
        "creationTimestamp": "2022-07-27T21:07:33Z",
        "modificationTimestamp": "2022-07-27T21:20:03Z",
        "createdBy": "12a5d9dd-851e-4235-af27-86c0b63bf3a9"
      }
    },
    {
      "type": "application/astra-app",
      "version": "2.0",
      "id": "7c212175-9cbd-4bb9-96a4-3a61a8ea0fda",
      "name": "wordpress-clone-202207271713",
      "namespaceScopedResources": [
        {
          "namespace": "wordpress-clonens-202207271713",
          "labelSelectors": []
        }
      ],
      "state": "provisioning",
      "lastResourceCollectionTimestamp": "2022-07-27T21:13:22Z",
      "stateTransitions": [
        {
          "to": [
            "pending"
          ]
        },
        {
          "to": [
            "provisioning"
          ]
        },
        {
          "from": "pending",
          "to": [
            "discovering",
            "failed"
          ]
        },
        {
          "from": "discovering",
          "to": [
            "ready",
            "failed"
          ]
        },
        {
          "from": "ready",
          "to": [
            "discovering",
            "restoring",
            "unavailable",
            "failed"
          ]
        },
        {
          "from": "unavailable",
          "to": [
            "ready",
            "restoring"
          ]
        },
        {
          "from": "provisioning",
          "to": [
            "discovering",
            "failed"
          ]
        },
        {
          "from": "restoring",
          "to": [
            "discovering",
            "failed"
          ]
        }
      ],
      "stateDetails": [],
      "protectionState": "none",
      "protectionStateDetails": [],
      "namespaces": [],
      "clusterName": "useast4-cluster",
      "clusterID": "9857d628-dc4b-4227-8470-7b7dd4ed84e9",
      "clusterType": "gke",
      "sourceClusterID": "b81bdd8f-c2c7-40eb-a602-4af06d3c6e4d",
      "backupID": "22b699cf-5a0f-4598-9840-1be055dd672b",
      "metadata": {
        "labels": [
          {
            "name": "astra.netapp.io/labels/read-only/appType",
            "value": "clone"
          }
        ],
        "creationTimestamp": "2022-07-27T21:13:21Z",
        "modificationTimestamp": "2022-07-27T21:20:03Z",
        "createdBy": "12a5d9dd-851e-4235-af27-86c0b63bf3a9"
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
  "id": "79c608be-828d-4b3b-92d4-5589c0a4e515",
  "name": "wordpress",
  "protectionState": "protected"
}
{
  "id": "79871ad1-2f69-4532-806a-42ba11cc45ac",
  "name": "cassandra",
  "protectionState": "partial"
}
{
  "id": "7c212175-9cbd-4bb9-96a4-3a61a8ea0fda",
  "name": "wordpress-clone-202207271713",
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
$ for i in `./toolkit.py -o json list snapshots --app cbffb71a-a96b-4c13-9d36-e1fbeac8aaa0 \
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
- cloudID: e7a0bf84-0256-4ab6-a4ec-4aa5a4e49705
  clusterCreationTimestamp: '2022-07-26T20:33:55Z'
  clusterType: gke
  clusterVersion: '1.21'
  clusterVersionString: v1.21.11-gke.1100
  defaultStorageClass: 81a9302a-d4dd-473c-b386-93c67508c823
  id: b81bdd8f-c2c7-40eb-a602-4af06d3c6e4d
  inUse: 'true'
  isMultizonal: 'true'
  location: us-central1-b
  managedState: managed
  managedStateUnready: []
  managedTimestamp: '2022-07-27T21:06:27Z'
  metadata:
    createdBy: 12a5d9dd-851e-4235-af27-86c0b63bf3a9
    creationTimestamp: '2022-07-20T17:40:45Z'
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
    modificationTimestamp: '2022-07-27T21:13:28Z'
  name: uscentral1-cluster
  namespaces:
  - cassandra
  - default
  - kube-node-lease
  - kube-public
  - kube-system
  - trident
  - wordpress
  restoreTargetSupported: 'true'
  snapshotSupported: 'true'
  state: running
  stateUnready: []
  type: application/astra-cluster
  version: '1.1'
- cloudID: e7a0bf84-0256-4ab6-a4ec-4aa5a4e49705
  clusterCreationTimestamp: '2022-07-27T20:37:06Z'
  clusterType: gke
  clusterVersion: '1.21'
  clusterVersionString: v1.21.11-gke.1100
  defaultStorageClass: 81a9302a-d4dd-473c-b386-93c67508c823
  id: 9857d628-dc4b-4227-8470-7b7dd4ed84e9
  inUse: 'true'
  isMultizonal: 'true'
  location: us-east4-b
  managedState: managed
  managedStateUnready: []
  managedTimestamp: '2022-07-27T21:06:21Z'
  metadata:
    createdBy: 12a5d9dd-851e-4235-af27-86c0b63bf3a9
    creationTimestamp: '2022-07-27T20:38:58Z'
    labels:
    - name: astra.netapp.io/labels/read-only/gcp/projectNumber
      value: '239048101169'
    - name: astra.netapp.io/labels/read-only/gcp/HostVpcProjectID
      value: xxxxxxx01169
    - name: astra.netapp.io/labels/read-only/hasNonTridentCSIDriverSupport
      value: 'true'
    - name: astra.netapp.io/labels/read-only/hasTridentDriverSupport
      value: 'true'
    - name: astra.netapp.io/labels/read-only/cloudName
      value: GCP
    modificationTimestamp: '2022-07-27T21:13:28Z'
  name: useast4-cluster
  namespaces: []
  restoreTargetSupported: 'true'
  snapshotSupported: 'true'
  state: pending
  stateUnready: []
  type: application/astra-cluster
  version: '1.1'
```

## Quiet

The `--quiet` argument suppresses output, while still utilizing proper exit codes, and throwing error messages for incorrect commands.  Consider this command (without the `--quiet` argument):

```text
$ ./toolkit.py manage app cassandra default -l name=cassandra b81bdd8f-c2c7-40eb-a602-4af06d3c6e4d
{'clusterID': 'b81bdd8f-c2c7-40eb-a602-4af06d3c6e4d', 'name': 'cassandra', 'namespaceScopedResources': [{'namespace': 'default', 'labelSelectors': ['name=cassandra']}], 'type': 'application/astra-app', 'version': '2.0'}
{"type": "application/astra-app", "version": "2.0", "id": "9dc08664-3d5d-4f7d-b2fd-266d12114f3b", "name": "cassandra", "namespaceScopedResources": [{"namespace": "default", "labelSelectors": ["name=cassandra"]}], "state": "discovering", "lastResourceCollectionTimestamp": "2022-07-27T17:38:05Z", "stateTransitions": [{"to": ["pending"]}, {"to": ["provisioning"]}, {"from": "pending", "to": ["discovering", "failed"]}, {"from": "discovering", "to": ["ready", "failed"]}, {"from": "ready", "to": ["discovering", "restoring", "unavailable", "failed"]}, {"from": "unavailable", "to": ["ready", "restoring"]}, {"from": "provisioning", "to": ["discovering", "failed"]}, {"from": "restoring", "to": ["discovering", "failed"]}], "stateDetails": [], "protectionState": "none", "protectionStateDetails": [], "namespaces": [], "clusterName": "uscentral1-cluster", "clusterID": "b81bdd8f-c2c7-40eb-a602-4af06d3c6e4d", "clusterType": "gke", "metadata": {"labels": [], "creationTimestamp": "2022-07-27T17:38:05Z", "modificationTimestamp": "2022-07-27T17:38:05Z", "createdBy": "12a5d9dd-851e-4235-af27-86c0b63bf3a9"}}
```

With the `--quiet` argument instead:

```text
$ ./toolkit.py manage app cassandra default -l name=cassandra b81bdd8f-c2c7-40eb-a602-4af06d3c6e4d
$ echo $?
0
```

While incorrect commands still display output even with the `--quiet` argument:

```text
$ ./toolkit.py --quiet manage app cassandra default -l name=cassandra 11111111-1111-1111-1111-111111111111
usage: toolkit.py manage app [-h] [-l LABELSELECTORS] appName {cassandra,default,wordpress} {b81bdd8f-c2c7-40eb-a602-4af06d3c6e4d}
toolkit.py manage app: error: argument clusterID: invalid choice: '11111111-1111-1111-1111-111111111111' (choose from 'b81bdd8f-c2c7-40eb-a602-4af06d3c6e4d')
$ echo $?
2
```

## Fast

The `-f`/`--fast` argument increases the toolkit speed by disabling the `choices` list within argparse.  This has a couple of advantages, but also some drawbacks, so it should be used with caution.

Take for instance running a `./toolkit.py clone -h` command, which prints out the help text of the `clone` command.  Since by default the `choices` lists of objects are populated for each potential argument, several API calls must be made to populate these lists.  Depending on your location and network speed, this can result in help commands taking several seconds (almost 4 seconds in this example).

```text
$ time ./toolkit.py clone -h
usage: toolkit.py clone [-h] [-b] [--cloneAppName CLONEAPPNAME] [--cloneNamespace CLONENAMESPACE]
                        [--clusterID {51a01591-1b00-4404-b6f4-4b6262c248bf,e2d5bcad-0008-499e-a598-61a86d1edecb}]
                        (--backupID {0022a7a3-3ab8-4796-aa5f-fd31f073a3ea,bbe423ec-e068-423a-aa63-6ac94ed666ba,7aa6661d-f0b2-41ca-8f5b-8345b71c1902} | --snapshotID {5e3ca1e6-2605-447b-9dcc-f25caf8b6904,5ea6d987-aee7-4c6b-86a0-fac42caf4088,e2908442-0e54-43cc-a7d9-aecb9203f9b1} | --sourceAppID {7ab349be-7112-414f-8e90-8aca9543037b,d214246b-2c96-4661-ba5a-e2a5c230faea,3378b940-3043-4602-b233-e9ebf10cb757})

optional arguments:
  -h, --help            show this help message and exit
  -b, --background      Run clone operation in the background
  --cloneAppName CLONEAPPNAME
                        Clone app name
  --cloneNamespace CLONENAMESPACE
                        Clone namespace name (optional, if not specified cloneAppName is used)
  --clusterID {51a01591-1b00-4404-b6f4-4b6262c248bf,e2d5bcad-0008-499e-a598-61a86d1edecb}
                        Cluster to clone into (can be same as source)
  --backupID {0022a7a3-3ab8-4796-aa5f-fd31f073a3ea,bbe423ec-e068-423a-aa63-6ac94ed666ba,7aa6661d-f0b2-41ca-8f5b-8345b71c1902}
                        Source backup to clone
  --snapshotID {5e3ca1e6-2605-447b-9dcc-f25caf8b6904,5ea6d987-aee7-4c6b-86a0-fac42caf4088,e2908442-0e54-43cc-a7d9-aecb9203f9b1}
                        Source snapshot to restore from
  --sourceAppID {7ab349be-7112-414f-8e90-8aca9543037b,d214246b-2c96-4661-ba5a-e2a5c230faea,3378b940-3043-4602-b233-e9ebf10cb757}
                        Source app to clone
./toolkit.py clone -h  0.46s user 0.09s system 13% cpu 3.996 total
```

If instead the `-f`/`--fast` argument is used, the `choices` lists are not populated, which results in zero API calls being made for a simple help operation, resulting in only local processing time (around 1/4 of a second).

```text
$ time ./toolkit.py --fast clone -h
usage: toolkit.py clone [-h] [-b] [--cloneAppName CLONEAPPNAME] [--cloneNamespace CLONENAMESPACE] [--clusterID CLUSTERID]
                        (--backupID BACKUPID | --snapshotID SNAPSHOTID | --sourceAppID SOURCEAPPID)

optional arguments:
  -h, --help            show this help message and exit
  -b, --background      Run clone operation in the background
  --cloneAppName CLONEAPPNAME
                        Clone app name
  --cloneNamespace CLONENAMESPACE
                        Clone namespace name (optional, if not specified cloneAppName is used)
  --clusterID CLUSTERID
                        Cluster to clone into (can be same as source)
  --backupID BACKUPID   Source backup to clone
  --snapshotID SNAPSHOTID
                        Source snapshot to restore from
  --sourceAppID SOURCEAPPID
                        Source app to clone
./toolkit.py --fast clone -h  0.19s user 0.06s system 95% cpu 0.259 total
```

This has a secondary advantage of cleaning up the help text in busy environments.

The `fast` argument can also be used with all other toolkit operations, which will see a variety of speed improvments based on the number of API calls that normally are made to populate the `choices` list.  For example, managing a cluster with and without the `fast` argument (8 seconds versus 3 seconds):

```text
time ./toolkit.py manage cluster e2d5bcad-0008-499e-a598-61a86d1edecb 81a9302a-d4dd-473c-b386-93c67508c823
{"type": "application/astra-managedCluster", "version": "1.1", "id": "e2d5bcad-0008-499e-a598-61a86d1edecb", "name": "uscentral1-cluster", "state": "pending", "stateUnready": [], "managedState": "managed", "restoreTargetSupported": "true", "snapshotSupported": "true", "managedStateUnready": [], "managedTimestamp": "2022-08-11T16:35:55Z", "inUse": "false", "clusterType": "gke", "clusterVersion": "1.22", "clusterVersionString": "v1.22.10-gke.600", "clusterCreationTimestamp": "2022-08-10T13:42:26Z", "namespaces": [], "defaultStorageClass": "81a9302a-d4dd-473c-b386-93c67508c823", "cloudID": "0ec2e027-80bc-426a-b844-692de243b29e", "credentialID": "86ae5829-6ac5-4515-94c8-50b9bc33ebe4", "location": "us-central1-b", "isMultizonal": "true", "metadata": {"labels": [{"name": "astra.netapp.io/labels/read-only/gcp/projectNumber", "value": "239048101169"}, {"name": "astra.netapp.io/labels/read-only/gcp/HostVpcProjectID", "value": "xxxxxxx01169"}, {"name": "astra.netapp.io/labels/read-only/hasNonTridentCSIDriverSupport", "value": "true"}, {"name": "astra.netapp.io/labels/read-only/hasTridentDriverSupport", "value": "true"}, {"name": "astra.netapp.io/labels/read-only/cloudName", "value": "GCP"}], "creationTimestamp": "2022-08-11T16:35:55Z", "modificationTimestamp": "2022-08-11T16:35:57Z", "createdBy": "system"}}
./toolkit.py manage cluster e2d5bcad-0008-499e-a598-61a86d1edecb   0.43s user 0.09s system 6% cpu 8.108 total
```

```text
time ./toolkit.py -f manage cluster e2d5bcad-0008-499e-a598-61a86d1edecb 81a9302a-d4dd-473c-b386-93c67508c823
{"type": "application/astra-managedCluster", "version": "1.1", "id": "e2d5bcad-0008-499e-a598-61a86d1edecb", "name": "uscentral1-cluster", "state": "pending", "stateUnready": [], "managedState": "managed", "restoreTargetSupported": "true", "snapshotSupported": "true", "managedStateUnready": [], "managedTimestamp": "2022-08-11T16:36:36Z", "inUse": "false", "clusterType": "gke", "clusterVersion": "1.22", "clusterVersionString": "v1.22.10-gke.600", "clusterCreationTimestamp": "2022-08-10T13:42:26Z", "namespaces": [], "defaultStorageClass": "81a9302a-d4dd-473c-b386-93c67508c823", "cloudID": "0ec2e027-80bc-426a-b844-692de243b29e", "credentialID": "5235c3a7-6a1b-42af-aa59-ac350c08130d", "location": "us-central1-b", "isMultizonal": "true", "metadata": {"labels": [{"name": "astra.netapp.io/labels/read-only/gcp/projectNumber", "value": "239048101169"}, {"name": "astra.netapp.io/labels/read-only/gcp/HostVpcProjectID", "value": "xxxxxxx01169"}, {"name": "astra.netapp.io/labels/read-only/hasNonTridentCSIDriverSupport", "value": "true"}, {"name": "astra.netapp.io/labels/read-only/hasTridentDriverSupport", "value": "true"}, {"name": "astra.netapp.io/labels/read-only/cloudName", "value": "GCP"}], "creationTimestamp": "2022-08-11T16:36:37Z", "modificationTimestamp": "2022-08-11T16:36:38Z", "createdBy": "system"}}
./toolkit.py -f manage cluster e2d5bcad-0008-499e-a598-61a86d1edecb   0.22s user 0.06s system 9% cpu 3.002 total
```

**However**, the drawback of the `fast` argument is the lack of guardrails.  Take for instance trying to manage that same cluster, but accidentally missing the last character on the storage class UUID when pasting it in:

```text
$ ./toolkit.py manage cluster e2d5bcad-0008-499e-a598-61a86d1edecb 81a9302a-d4dd-473c-b386-93c67508c82 
usage: toolkit.py manage cluster [-h]
                                 {e2d5bcad-0008-499e-a598-61a86d1edecb}
                                 {b3843cb8-7de4-4a5b-9734-f9a54f89369c,dbff270b-b6b6-4fc4-afd1-74fb43710755,81a9302a-d4dd-473c-b386-93c67508c823,f6322d5c-755d-42ad-96f0-552a20610741,a908dda1-89ba-4122-9830-6637ab3cbf78}
toolkit.py manage cluster: error: argument storageClassID: invalid choice: '81a9302a-d4dd-473c-b386-93c67508c82' (choose from 'b3843cb8-7de4-4a5b-9734-f9a54f89369c', 'dbff270b-b6b6-4fc4-afd1-74fb43710755', '81a9302a-d4dd-473c-b386-93c67508c823', 'f6322d5c-755d-42ad-96f0-552a20610741', 'a908dda1-89ba-4122-9830-6637ab3cbf78')
```

Argparse detects that the storage class UUID is incorrect, and catches the error prior to making any API calls.  When using the `fast` argument, this error checking is not performed, resulting in a 400 API response:

```text
$ ./toolkit.py -f manage cluster e2d5bcad-0008-499e-a598-61a86d1edecb 81a9302a-d4dd-473c-b386-93c67508c82
API HTTP Status Code: 400 - Bad Request
Error text: {"error":"failed to create managed cluster: failed to get storage class name: failed to find storage class with ID: 81a9302a-d4dd-473c-b386-93c67508c82"}
astraSDK.manageCluster() failed
```

For this reason use the `fast` argument **AT YOUR OWN RISK**, and please take extra care to be sure that the commands entered are correct.
