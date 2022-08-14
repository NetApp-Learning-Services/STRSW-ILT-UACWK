# List

The `list` command shows various resources known to Astra.

* [Apps](#apps)
* [Assets](#assets)
* [Backups](#backups)
* [Clouds](#clouds)
* [Clusters](#clusters)
* [Hooks](#hooks)
* [Namespaces](#namespaces)
* [Scripts](#scripts)
* [Snapshots](#snapshots)
* [Storageclasses](#storageclasses)

## Apps

`list apps` displays applications known to Astra.  The default command (without arguments) shows `managed` applications, but `unmanaged` applications can also be shown with optional arguments.  Additionally, apps may be filtered by a cluster name.

Command usage:

```text
./toolkit.py list apps <optional-arguments>
```

Sample output:

```text
$ ./toolkit.py list apps
+----------------+--------------------------------------+-----------------+----------------+--------------+
| appName        | appID                                | clusterName     | namespace      | state        |
+================+======================================+=================+================+==============+
| wordpress-east | 8f462cea-a166-438d-85b1-8aa5cfb0ad9f | useast1-cluster | wordpress      | ready        |
+----------------+--------------------------------------+-----------------+----------------+--------------+
| wordpress-west | a8dc676e-d182-4d7c-9113-43f5a2963b54 | uswest1-cluster | wordpress-prod | ready        |
+----------------+--------------------------------------+-----------------+----------------+--------------+
| temp-clone     | ad125374-e090-425b-a048-d719b93b0feb | uswest1-cluster | clonens        | provisioning |
+----------------+--------------------------------------+-----------------+----------------+--------------+
```

```text
$ ./toolkit.py list apps --cluster useast1-cluster
+----------------+--------------------------------------+-----------------+-------------+-------+
| appName        | appID                                | clusterName     | namespace   | state |
+================+======================================+=================+=============+=======+
| wordpress-east | 8f462cea-a166-438d-85b1-8aa5cfb0ad9f | useast1-cluster | wordpress   | ready |
+----------------+--------------------------------------+-----------------+-------------+-------+
```

```text
$ ./toolkit.py list apps --namespace wordpress-prod
+----------------+--------------------------------------+-----------------+----------------+-------+
| appName        | appID                                | clusterName     | namespace      | state |
+================+======================================+=================+================+=======+
| wordpress-west | a8dc676e-d182-4d7c-9113-43f5a2963b54 | uswest1-cluster | wordpress-prod | ready |
+----------------+--------------------------------------+-----------------+----------------+-------+
```

## Assets

`list assets` shows a single application's assets which are managed via Astra Control.

Command usage:

```text
./toolkit.py list assets <appID>
```

Sample output:

```text
$ ./toolkit.py list assets fad776eb-f80f-4a2b-b297-c4d4ff255b14
+---------------------------------+-----------------------+
| assetName                       | assetType             |
+=================================+=======================+
| cassandra                       | ServiceAccount        |
+---------------------------------+-----------------------+
| default                         | ServiceAccount        |
+---------------------------------+-----------------------+
| kube-root-ca.crt                | ConfigMap             |
+---------------------------------+-----------------------+
| data-cassandra-0                | PersistentVolumeClaim |
+---------------------------------+-----------------------+
| cassandra                       | Secret                |
+---------------------------------+-----------------------+
| cassandra-token-rqrdr           | Secret                |
+---------------------------------+-----------------------+
| default-token-p2m7l             | Secret                |
+---------------------------------+-----------------------+
| sh.helm.release.v1.cassandra.v1 | Secret                |
+---------------------------------+-----------------------+
| cassandra                       | Service               |
+---------------------------------+-----------------------+
| cassandra-headless              | Service               |
+---------------------------------+-----------------------+
| cassandra                       | StatefulSet           |
+---------------------------------+-----------------------+
| cassandra-0                     | Pod                   |
+---------------------------------+-----------------------+
```

## Backups

`list backups` shows all app backups.  They can also be filtered by an application.

Command usage:

```text
./toolkit.py list backups <optional-arguments>
```

Sample output:

```text
$ ./toolkit.py list backups
+--------------------------------------+--------------------+--------------------------------------+-------------+
| AppID                                | backupName         | backupID                             | backupState |
+======================================+====================+======================================+=============+
| 8f462cea-a166-438d-85b1-8aa5cfb0ad9f | hourly-mslr6-dr8rl | c695dfe2-5245-49a1-8a79-8d5c49deac5e | completed   |
+--------------------------------------+--------------------+--------------------------------------+-------------+
| 8f462cea-a166-438d-85b1-8aa5cfb0ad9f | hourly-mslr6-jjw1g | ddb30a46-fca9-4705-8b89-31f87aa6c20b | ready       |
+--------------------------------------+--------------------+--------------------------------------+-------------+
| a8dc676e-d182-4d7c-9113-43f5a2963b54 | hourly-vydir-roxw8 | ec3cbcb7-cc27-43da-b670-7cf8b2416552 | completed   |
+--------------------------------------+--------------------+--------------------------------------+-------------+
| a8dc676e-d182-4d7c-9113-43f5a2963b54 | hourly-vydir-n1hfv | b1a74715-680a-4217-971e-d4deabce72e0 | ready       |
+--------------------------------------+--------------------+--------------------------------------+-------------+
```

```text
$ ./toolkit.py list backups --app wordpress
+--------------------------------------+--------------------+--------------------------------------+-------------+
| AppID                                | backupName         | backupID                             | backupState |
+======================================+====================+======================================+=============+
| 8f462cea-a166-438d-85b1-8aa5cfb0ad9f | hourly-mslr6-dr8rl | c695dfe2-5245-49a1-8a79-8d5c49deac5e | completed   |
+--------------------------------------+--------------------+--------------------------------------+-------------+
| 8f462cea-a166-438d-85b1-8aa5cfb0ad9f | hourly-mslr6-jjw1g | ddb30a46-fca9-4705-8b89-31f87aa6c20b | ready       |
+--------------------------------------+--------------------+--------------------------------------+-------------+
```

## Clouds

`list clouds` shows the clouds that have been added to Astra.  Currently only displaying clouds is possible through the SDK, please utilize the UI for adding or removing clouds.

Command usage:

```text
./toolkit.py list clouds
```

Sample output:

```text
$ ./toolkit.py list clouds
+-------------+--------------------------------------+-----------+
| cloudName   | cloudID                              | cloudType |
+=============+======================================+===========+
| GCP         | 0ec2e027-80bc-426a-b844-692de243b29e | GCP       |
+-------------+--------------------------------------+-----------+
| Azure       | 7b8d4252-293c-4c70-b101-7fd6b7d08e15 | Azure     |
+-------------+--------------------------------------+-----------+
```

## Clusters

`list clusters` shows all clusters deployed within the clouds managed by Astra.  By default both managed and unmanaged clusters are displayed, with arguments for hiding either.

Command usage:

```text
./toolkit.py list clusters <optional-arguments>
```

Sample output:

```text
$ ./toolkit.py list clusters
+--------------------+--------------------------------------+-------------+--------------+
| clusterName        | clusterID                            | clusterType | managedState |
+====================+======================================+=============+==============+
| aks-eastus-cluster | 80d6bef8-300c-44bd-9e36-04ef874bdc29 | aks         | unmanaged    |
+--------------------+--------------------------------------+-------------+--------------+
| uswest1-cluster    | c9456cae-b2d4-400b-ac53-60637d57da57 | gke         | managed      |
+--------------------+--------------------------------------+-------------+--------------+
| useast1-cluster    | 9fd690f3-4ae5-423d-9b58-95b6ba4f02e4 | gke         | managed      |
+--------------------+--------------------------------------+-------------+--------------+
```

```text
$ ./toolkit.py list clusters --hideManaged
+--------------------+--------------------------------------+-------------+--------------+
| clusterName        | clusterID                            | clusterType | managedState |
+====================+======================================+=============+==============+
| aks-eastus-cluster | 80d6bef8-300c-44bd-9e36-04ef874bdc29 | aks         | unmanaged    |
+--------------------+--------------------------------------+-------------+--------------+
```

```text
$ ./toolkit.py list clusters --hideUnmanaged
+-----------------+--------------------------------------+-------------+--------------+
| clusterName     | clusterID                            | clusterType | managedState |
+=================+======================================+=============+==============+
| uswest1-cluster | c9456cae-b2d4-400b-ac53-60637d57da57 | gke         | managed      |
+-----------------+--------------------------------------+-------------+--------------+
| useast1-cluster | 9fd690f3-4ae5-423d-9b58-95b6ba4f02e4 | gke         | managed      |
+-----------------+--------------------------------------+-------------+--------------+
```

## Hooks

`list hooks` shows all application execution hooks.  They can also be filtered by an application.

Command usage:

```text
./toolkit.py list hooks <optional-arguments>
```

Sample output:

```text
$ ./toolkit.py list hooks
+--------------------------------------+----------------------------+--------------------------------------+------------------------------------------------+
| appID                                | hookName                   | hookID                               | matchingImages                                 |
+======================================+============================+======================================+================================================+
| eebd59f2-e9b3-47b0-b0e8-1306d805f104 | cassandra-pre-snap         | 3e9bb6f4-9433-4dc3-b256-cf9837aeb2e7 | docker.io/bitnami/cassandra:4.0.5-debian-11-r4 |
+--------------------------------------+----------------------------+--------------------------------------+------------------------------------------------+
| eebd59f2-e9b3-47b0-b0e8-1306d805f104 | cassandra-post-snap        | 50f0ece4-43c8-42a6-8826-b438e476883c | docker.io/bitnami/cassandra:4.0.5-debian-11-r4 |
+--------------------------------------+----------------------------+--------------------------------------+------------------------------------------------+
| 7b647ab6-834b-4553-9b23-02ecdd8562f7 | wordpress-mariadb-pre-snap | 8f748130-5202-45d3-9e86-0cf0e8ee97c2 | docker.io/bitnami/mariadb:10.6.8-debian-11-r20 |
+--------------------------------------+----------------------------+--------------------------------------+------------------------------------------------+
```

```text
$ ./toolkit.py list hooks --app cassandra
+--------------------------------------+----------------------------+--------------------------------------+------------------------------------------------+
| appID                                | hookName                   | hookID                               | matchingImages                                 |
+======================================+============================+======================================+================================================+
| eebd59f2-e9b3-47b0-b0e8-1306d805f104 | cassandra-pre-snap         | 3e9bb6f4-9433-4dc3-b256-cf9837aeb2e7 | docker.io/bitnami/cassandra:4.0.5-debian-11-r4 |
+--------------------------------------+----------------------------+--------------------------------------+------------------------------------------------+
| eebd59f2-e9b3-47b0-b0e8-1306d805f104 | cassandra-post-snap        | 50f0ece4-43c8-42a6-8826-b438e476883c | docker.io/bitnami/cassandra:4.0.5-debian-11-r4 |
+--------------------------------------+----------------------------+--------------------------------------+------------------------------------------------+
```

## Namespaces

`list namespaces` shows all non-system namespaces of all of the managed clusters.  They can also be filtered by:

* `--clusterID`/`-c`: show namespaces only from the matching cluster ID
* `--nameFilter`/`-f`: show namespaces which *contain* the filter provided (`ss` would match on both `cassandra` and `wordpress`)
* `--showRemoved`/`-r`: *also* show namespaces which are in a `removed` namespaceState
* `--minutes`/`-m`: show namespaces only created within the last X minutes

Command usage:

```text
./toolkit.py list namespaces <optional-arguments>
```

Sample output:

```text
$ ./toolkit.py list namespaces
+-----------+--------------------------------------+----------------+----------------+--------------------------------------+
| name      | namespaceID                          | namespaceState | associatedApps | clusterID                            |
+===========+======================================+================+================+======================================+
| default   | 06951563-6f6f-41aa-a612-6a8e95646737 | discovered     | jfrog, gitlab  | af0aecb9-9b18-473f-b417-54fb38e1e28d |
+-----------+--------------------------------------+----------------+----------------+--------------------------------------+
| default   | 06951563-6f6f-41aa-a612-6a8e95646737 | discovered     |                | b81bdd8f-c2c7-40eb-a602-4af06d3c6e4d |
+-----------+--------------------------------------+----------------+----------------+--------------------------------------+
| cassandra | 0c81f720-ab01-42a5-bb48-8bb3abab8817 | discovered     | cassandra      | b81bdd8f-c2c7-40eb-a602-4af06d3c6e4d |
+-----------+--------------------------------------+----------------+----------------+--------------------------------------+
| wordpress | 1d1f210a-f37a-4474-b8df-1b4605090f10 | discovered     | wordpress      | af0aecb9-9b18-473f-b417-54fb38e1e28d |
+-----------+--------------------------------------+----------------+----------------+--------------------------------------+
```

```text
$ ./toolkit.py list namespaces --clusterID af0aecb9-9b18-473f-b417-54fb38e1e28d
+-----------+--------------------------------------+----------------+----------------+--------------------------------------+
| name      | namespaceID                          | namespaceState | associatedApps | clusterID                            |
+===========+======================================+================+================+======================================+
| default   | 06951563-6f6f-41aa-a612-6a8e95646737 | discovered     | jfrog, gitlab  | af0aecb9-9b18-473f-b417-54fb38e1e28d |
+-----------+--------------------------------------+----------------+----------------+--------------------------------------+
| wordpress | 1d1f210a-f37a-4474-b8df-1b4605090f10 | discovered     | wordpress      | af0aecb9-9b18-473f-b417-54fb38e1e28d |
+-----------+--------------------------------------+----------------+----------------+--------------------------------------+
```

```text
$ ./toolkit.py list namespaces --nameFilter word
+-----------+--------------------------------------+----------------+----------------+--------------------------------------+
| name      | namespaceID                          | namespaceState | associatedApps | clusterID                            |
+===========+======================================+================+================+======================================+
| wordpress | 1d1f210a-f37a-4474-b8df-1b4605090f10 | discovered     | wordpress      | af0aecb9-9b18-473f-b417-54fb38e1e28d |
+-----------+--------------------------------------+----------------+----------------+--------------------------------------+
```

```text
$ ./toolkit.py list namespaces --showRemoved
+----------------+--------------------------------------+----------------+----------------+--------------------------------------+
| name           | namespaceID                          | namespaceState | associatedApps | clusterID                            |
+================+======================================+================+================+======================================+
| default        | 06951563-6f6f-41aa-a612-6a8e95646737 | discovered     | jfrog, gitlab  | af0aecb9-9b18-473f-b417-54fb38e1e28d |
+----------------+--------------------------------------+----------------+----------------+--------------------------------------+
| default        | 06951563-6f6f-41aa-a612-6a8e95646737 | discovered     |                | b81bdd8f-c2c7-40eb-a602-4af06d3c6e4d |
+----------------+--------------------------------------+----------------+----------------+--------------------------------------+
| cassandra      | 0c81f720-ab01-42a5-bb48-8bb3abab8817 | discovered     | cassandra      | b81bdd8f-c2c7-40eb-a602-4af06d3c6e4d |
+----------------+--------------------------------------+----------------+----------------+--------------------------------------+
| wordpress      | 1d1f210a-f37a-4474-b8df-1b4605090f10 | discovered     | wordpress      | af0aecb9-9b18-473f-b417-54fb38e1e28d |
+----------------+--------------------------------------+----------------+----------------+--------------------------------------+
| wordpressclone | 9d54366c-ba9b-46e6-8dec-3bbc55699ffd | removed        | wordpressclone | af0aecb9-9b18-473f-b417-54fb38e1e28d |
+----------------+--------------------------------------+----------------+----------------+--------------------------------------+
```

```text
$ ./toolkit.py list namespaces --minutes 60
+-----------+--------------------------------------+----------------+----------------+--------------------------------------+
| name      | namespaceID                          | namespaceState | associatedApps | clusterID                            |
+===========+======================================+================+================+======================================+
| cassandra | 0c81f720-ab01-42a5-bb48-8bb3abab8817 | discovered     | cassandra      | b81bdd8f-c2c7-40eb-a602-4af06d3c6e4d |
+-----------+--------------------------------------+----------------+----------------+--------------------------------------+
```

## Scripts

`list scripts` shows all of the account's scripts, which are used with [execution hooks](../create/README.md#execution-hook).  With the `-s`/`--getScriptSource` argument, providing a matching script name will output the body of the script.

Command usage:

```text
./toolkit.py list scripts <optional-arguments>
```

Sample output:

```text
$ ./toolkit.py list scripts
+---------------+--------------------------------------+----------------------------------+
| scriptName    | scriptID                             | description                      |
+===============+======================================+==================================+
| postgres      | e3daff37-5611-4f33-86d2-e64eeb48b7c0 | Validated on PostgreSQL 14.4.0   |
+---------------+--------------------------------------+----------------------------------+
| mongoDB       | c842e867-bafd-4490-a0b1-a77311633456 | Validated on MongoDB 5.0.8       |
+---------------+--------------------------------------+----------------------------------+
| elasticsearch | 29c97315-8cc0-43aa-acec-12ff02998fa4 | Validated on Elasticsearch 8.2.3 |
+---------------+--------------------------------------+----------------------------------+
| exampleScript | e6e633f7-5ed3-4598-b773-e0d13631f5a6 |                                  |
+---------------+--------------------------------------+----------------------------------+
```

```text
$ ./toolkit.py list scripts -s exampleScript
#!/bin/bash
echo "this is just an example"
```

## Snapshots

`list snapshots` shows all app snapshots.  They can also be filtered by an app name.

Command usage:

```text
./toolkit.py list snapshots <optional-arguments>
```

Sample output:

```text
$ ./toolkit.py list snapshots
+--------------------------------------+-------------------------------------+--------------------------------------+---------------+
| appID                                | snapshotName                        | snapshotID                           | snapshotState |
+======================================+=====================================+======================================+===============+
| 8f462cea-a166-438d-85b1-8aa5cfb0ad9f | wordpress-snapshot-20220520000039   | 8daeed16-f4d3-4d24-90f0-34748161ef05 | completed     |
+--------------------------------------+-------------------------------------+--------------------------------------+---------------+
| 8f462cea-a166-438d-85b1-8aa5cfb0ad9f | wordpress-snapshot-20220520010028   | b586d51a-28b3-4dd2-aecf-057191c9fc77 | completed     |
+--------------------------------------+-------------------------------------+--------------------------------------+---------------+
| a8dc676e-d182-4d7c-9113-43f5a2963b54 | wordpress-w-snapshot-20220519200036 | 12a2f61c-23b2-4c98-bc51-638c9ab9f9c1 | ready         |
+--------------------------------------+-------------------------------------+--------------------------------------+---------------+
```

```text
$ ./toolkit.py list snapshots --app wordpress-east
+--------------------------------------+-----------------------------------+--------------------------------------+---------------+
| appID                                | snapshotName                      | snapshotID                           | snapshotState |
+======================================+===================================+======================================+===============+
| 8f462cea-a166-438d-85b1-8aa5cfb0ad9f | wordpress-snapshot-20220520000039 | 8daeed16-f4d3-4d24-90f0-34748161ef05 | completed     |
+--------------------------------------+-----------------------------------+--------------------------------------+---------------+
| 8f462cea-a166-438d-85b1-8aa5cfb0ad9f | wordpress-snapshot-20220520010028 | b586d51a-28b3-4dd2-aecf-057191c9fc77 | completed     |
+--------------------------------------+-----------------------------------+--------------------------------------+---------------+
```

## Storageclasses

`list storageclasses` lists the storageclasses of *all* clusters, whether managed or unmanaged.  This command is particularly relevent when [managing a cluster](../manage/README.md#cluster) as the default storageclassID is a required argument.

Command usage:

```text
./toolkit.py list storageclasses
```

Sample output:

```text
./toolkit.py list storageclasses
+---------+--------------------+--------------------------------------+--------------------------+
| cloud   | cluster            | storageclassID                       | storageclassName         |
+=========+====================+======================================+==========================+
| GCP     | uswest1-cluster    | 0f17bdd2-38e0-4f10-a351-9844de4243ee | netapp-cvs-standard      |
+---------+--------------------+--------------------------------------+--------------------------+
| GCP     | uswest1-cluster    | 759bc884-841e-4373-ade6-bc842f8862fb | premium-rwo              |
+---------+--------------------+--------------------------------------+--------------------------+
| GCP     | uswest1-cluster    | bf855d91-9a8c-4008-a5da-e2a6868b4bd3 | standard-rwo             |
+---------+--------------------+--------------------------------------+--------------------------+
| GCP     | useast1-cluster    | 0f17bdd2-38e0-4f10-a351-9844de4243ee | netapp-cvs-standard      |
+---------+--------------------+--------------------------------------+--------------------------+
| GCP     | useast1-cluster    | 679c1409-e2e1-43d1-bc09-7b8df0426be2 | premium-rwo              |
+---------+--------------------+--------------------------------------+--------------------------+
| GCP     | useast1-cluster    | 058194c6-1932-45ab-af97-306479c24c06 | standard-rwo             |
+---------+--------------------+--------------------------------------+--------------------------+
| Azure   | aks-eastus-cluster | ba6d5a64-a321-4fd7-9842-9adce829229a | netapp-anf-perf-standard |
+---------+--------------------+--------------------------------------+--------------------------+
| Azure   | aks-eastus-cluster | 61ccd37a-d407-4252-9a42-82aced92b1f2 | default                  |
+---------+--------------------+--------------------------------------+--------------------------+
| Azure   | aks-eastus-cluster | 4a373518-acab-4d45-b6f5-d3fd5777069d | managed                  |
+---------+--------------------+--------------------------------------+--------------------------+
| Azure   | aks-eastus-cluster | 9e50815c-c433-448b-9aba-d03fa2f5ec2b | managed-csi              |
+---------+--------------------+--------------------------------------+--------------------------+
| Azure   | aks-eastus-cluster | f868b07a-6a33-4a85-8e88-eafffbd4bfdf | managed-csi-premium      |
+---------+--------------------+--------------------------------------+--------------------------+
| Azure   | aks-eastus-cluster | 83740760-6d53-46e1-b44f-1cba6cdf4a0a | managed-premium          |
+---------+--------------------+--------------------------------------+--------------------------+
| Azure   | aks-eastus-cluster | d36dad41-9457-4ee5-bfde-cf8d51d54569 | azurefile                |
+---------+--------------------+--------------------------------------+--------------------------+
| Azure   | aks-eastus-cluster | b9adf548-97cf-4ac9-b9be-5b06f0a23451 | azurefile-csi            |
+---------+--------------------+--------------------------------------+--------------------------+
| Azure   | aks-eastus-cluster | a5cf174c-0f48-48f7-8ec7-11aeb831b888 | azurefile-csi-premium    |
+---------+--------------------+--------------------------------------+--------------------------+
| Azure   | aks-eastus-cluster | e1b9b067-20c5-4b4a-8023-8a873d4b25fc | azurefile-premium        |
+---------+--------------------+--------------------------------------+--------------------------+
```
