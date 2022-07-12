# List

The `list` command shows various resources known to Astra.

* [Apps](#apps)
* [Backups](#backups)
* [Clouds](#clouds)
* [Clusters](#clusters)
* [Snapshots](#snapshots)
* [Storageclasses](#storageclasses)

## Apps

`list apps` displays applications known to Astra.  The default command (without arguments) shows `managed` applications, but `unmanaged` or `ignored` applications can also be shown with optional arguments.  Additionally, apps may be filtered by a cluster name.

Command usage:

```text
./toolkit.py list apps <optional-arguments>
```

Sample output:

```text
$ ./toolkit.py list apps
+----------------+--------------------------------------+-----------------+----------------+--------------+-----------+
| appName        | appID                                | clusterName     | namespace      | state        | source    |
+================+======================================+=================+================+==============+===========+
| wordpress-east | 8f462cea-a166-438d-85b1-8aa5cfb0ad9f | useast1-cluster | wordpress      | running      | namespace |
+----------------+--------------------------------------+-----------------+----------------+--------------+-----------+
| wordpress-west | a8dc676e-d182-4d7c-9113-43f5a2963b54 | uswest1-cluster | wordpress-prod | running      | namespace |
+----------------+--------------------------------------+-----------------+----------------+--------------+-----------+
| temp-clone     | ad125374-e090-425b-a048-d719b93b0feb | uswest1-cluster | clonens        | provisioning | namespace |
+----------------+--------------------------------------+-----------------+----------------+--------------+-----------+
```

```text
$ ./toolkit.py list apps --cluster useast1-cluster
+----------------+--------------------------------------+-----------------+-------------+---------+-----------+
| appName        | appID                                | clusterName     | namespace   | state   | source    |
+================+======================================+=================+=============+=========+===========+
| wordpress-east | 8f462cea-a166-438d-85b1-8aa5cfb0ad9f | useast1-cluster | wordpress   | running | namespace |
+----------------+--------------------------------------+-----------------+-------------+---------+-----------+
```

```text
$ ./toolkit.py list apps --namespace wordpress-prod
+----------------+--------------------------------------+-----------------+----------------+---------+-----------+
| appName        | appID                                | clusterName     | namespace      | state   | source    |
+================+======================================+=================+================+=========+===========+
| wordpress-west | a8dc676e-d182-4d7c-9113-43f5a2963b54 | uswest1-cluster | wordpress-prod | running | namespace |
+----------------+--------------------------------------+-----------------+----------------+---------+-----------+
```

```text
$ ./toolkit.py list apps --unmanaged
+-----------------+--------------------------------------+-----------------+------------+---------+----------+
| appName         | appID                                | clusterName     | namespace  | state   | source   |
+=================+======================================+=================+============+=========+==========+
| staging-magento | d00964bb-8d83-4151-99e8-7d31fb7e0611 | useast1-cluster | magneto846 | running | helm     |
+-----------------+--------------------------------------+-----------------+------------+---------+----------+
| staging-spark   | 5cd31c6a-2f3e-434b-8649-735569637c4b | uswest1-cluster | spark034   | running | helm     |
+-----------------+--------------------------------------+-----------------+------------+---------+----------+
```

```text
$ ./toolkit.py list apps --ignored
+---------------+--------------------------------------+-----------------+--------------+---------+----------+
| appName       | appID                                | clusterName     | namespace    | state   | source   |
+===============+======================================+=================+==============+=========+==========+
| dev-rabbitmq  | 125e9d1e-a278-491f-b278-134edf38d44c | useast1-cluster | rabbitmq836  | running | helm     |
+---------------+--------------------------------------+-----------------+--------------+---------+----------+
| dev-zookeeper | ac374e80-4acb-41d5-8276-096b0259be00 | uswest1-cluster | zookeeper972 | running | helm     |
+---------------+--------------------------------------+-----------------+--------------+---------+----------+
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
+--------------------------------------+--------------------+--------------------------------------+---------------+
| AppID                                | backupName         | backupID                             | backupState   |
+======================================+====================+======================================+===============+
| 8f462cea-a166-438d-85b1-8aa5cfb0ad9f | hourly-mslr6-dr8rl | c695dfe2-5245-49a1-8a79-8d5c49deac5e | completed     |
+--------------------------------------+--------------------+--------------------------------------+---------------+
| 8f462cea-a166-438d-85b1-8aa5cfb0ad9f | hourly-mslr6-jjw1g | ddb30a46-fca9-4705-8b89-31f87aa6c20b | running       |
+--------------------------------------+--------------------+--------------------------------------+---------------+
| a8dc676e-d182-4d7c-9113-43f5a2963b54 | hourly-vydir-roxw8 | ec3cbcb7-cc27-43da-b670-7cf8b2416552 | completed     |
+--------------------------------------+--------------------+--------------------------------------+---------------+
| a8dc676e-d182-4d7c-9113-43f5a2963b54 | hourly-vydir-n1hfv | b1a74715-680a-4217-971e-d4deabce72e0 | running       |
+--------------------------------------+--------------------+--------------------------------------+---------------+
```

```text
$ ./toolkit.py list backups --app wordpress
+--------------------------------------+--------------------+--------------------------------------+---------------+
| AppID                                | backupName         | backupID                             | backupState   |
+======================================+====================+======================================+===============+
| 8f462cea-a166-438d-85b1-8aa5cfb0ad9f | hourly-mslr6-dr8rl | c695dfe2-5245-49a1-8a79-8d5c49deac5e | completed     |
+--------------------------------------+--------------------+--------------------------------------+---------------+
| 8f462cea-a166-438d-85b1-8aa5cfb0ad9f | hourly-mslr6-jjw1g | ddb30a46-fca9-4705-8b89-31f87aa6c20b | running       |
+--------------------------------------+--------------------+--------------------------------------+---------------+
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
+-------------+--------------------------------------+-------------+
| cloudName   | cloudID                              | cloudType   |
+=============+======================================+=============+
| GCP         | 0ec2e027-80bc-426a-b844-692de243b29e | GCP         |
+-------------+--------------------------------------+-------------+
| Azure       | 7b8d4252-293c-4c70-b101-7fd6b7d08e15 | Azure       |
+-------------+--------------------------------------+-------------+
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
+--------------------+--------------------------------------+---------------+----------------+
| clusterName        | clusterID                            | clusterType   | managedState   |
+====================+======================================+===============+================+
| aks-eastus-cluster | 80d6bef8-300c-44bd-9e36-04ef874bdc29 | aks           | unmanaged      |
+--------------------+--------------------------------------+---------------+----------------+
| uswest1-cluster    | c9456cae-b2d4-400b-ac53-60637d57da57 | gke           | managed        |
+--------------------+--------------------------------------+---------------+----------------+
| useast1-cluster    | 9fd690f3-4ae5-423d-9b58-95b6ba4f02e4 | gke           | managed        |
+--------------------+--------------------------------------+---------------+----------------+
```

```text
$ ./toolkit.py list clusters --hideManaged
+--------------------+--------------------------------------+---------------+----------------+
| clusterName        | clusterID                            | clusterType   | managedState   |
+====================+======================================+===============+================+
| aks-eastus-cluster | 80d6bef8-300c-44bd-9e36-04ef874bdc29 | aks           | unmanaged      |
+--------------------+--------------------------------------+---------------+----------------+
```

```text
$ ./toolkit.py list clusters --hideUnmanaged
+-----------------+--------------------------------------+---------------+----------------+
| clusterName     | clusterID                            | clusterType   | managedState   |
+=================+======================================+===============+================+
| uswest1-cluster | c9456cae-b2d4-400b-ac53-60637d57da57 | gke           | managed        |
+-----------------+--------------------------------------+---------------+----------------+
| useast1-cluster | 9fd690f3-4ae5-423d-9b58-95b6ba4f02e4 | gke           | managed        |
+-----------------+--------------------------------------+---------------+----------------+
```

## Snapshots

`list snapshots` shows all app snapshots.  They can also be filtered a cluster name.

Command usage:

```text
./toolkit.py list snapshots <optional-arguments>
```

Sample output:

```text
$ ./toolkit.py list snapshots
+--------------------------------------+-------------------------------------+--------------------------------------+-----------------+
| appID                                | snapshotName                        | snapshotID                           | snapshotState   |
+======================================+=====================================+======================================+=================+
| 8f462cea-a166-438d-85b1-8aa5cfb0ad9f | wordpress-snapshot-20220520000039   | 8daeed16-f4d3-4d24-90f0-34748161ef05 | completed       |
+--------------------------------------+-------------------------------------+--------------------------------------+-----------------+
| 8f462cea-a166-438d-85b1-8aa5cfb0ad9f | wordpress-snapshot-20220520010028   | b586d51a-28b3-4dd2-aecf-057191c9fc77 | completed       |
+--------------------------------------+-------------------------------------+--------------------------------------+-----------------+
| a8dc676e-d182-4d7c-9113-43f5a2963b54 | wordpress-w-snapshot-20220519200036 | 12a2f61c-23b2-4c98-bc51-638c9ab9f9c1 | running         |
+--------------------------------------+-------------------------------------+--------------------------------------+-----------------+
```

```text
$ ./toolkit.py list snapshots --app wordpress-east
+--------------------------------------+-----------------------------------+--------------------------------------+-----------------+
| appID                                | snapshotName                      | snapshotID                           | snapshotState   |
+======================================+===================================+======================================+=================+
| 8f462cea-a166-438d-85b1-8aa5cfb0ad9f | wordpress-snapshot-20220520000039 | 8daeed16-f4d3-4d24-90f0-34748161ef05 | completed       |
+--------------------------------------+-----------------------------------+--------------------------------------+-----------------+
| 8f462cea-a166-438d-85b1-8aa5cfb0ad9f | wordpress-snapshot-20220520010028 | b586d51a-28b3-4dd2-aecf-057191c9fc77 | completed       |
+--------------------------------------+-----------------------------------+--------------------------------------+-----------------+
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
