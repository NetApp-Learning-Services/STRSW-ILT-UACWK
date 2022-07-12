# Clone

The `clone` argument allows you to clone a [managed application](../manage/README.md#app) to a destination [cluster](..list/README.md#clusters) of your choice.  It is currently only possible to clone from a [backup](../list/README.md#backups), not a [snapshot](../list/README.md#snapshots), however if a backup does not exist, one will be automatically created.

After cloning an application, it is recommended to [create a protection policy](../create/README.md#protectionpolicy) for the new application.

The overall command usage is:

```text
./toolkit.py clone <optionalBackgroundArg> --sourceNamespace <sourceAppNamespace> --backupID \
    <backupID> --clusterID <clusterID> --destName <destAppName> --destNamespace <destNamespaceName>
```

* `--sourceNamespace`: must specify a [managed application](../manage/README.md#app) with a **source** as `namespace`
* `--backupID`: the backupID to create the clone from (if a backup does not exist, do not specify the argument and one will be created for you)
* `--clusterID`: the destination clusterID (it can be any cluster manged by Astra Control)
* `--destName`: the name of the new application
* `--destNamespace`: the name of the new namespace on the destination cluster (it **must not** exist already)

When the optional `--background`/`-b` argument is **not** specified, the command polls for the status of the clone operation every 3 seconds, and reports back once complete.

```text
$ ./toolkit.py clone --sourceNamespace a643b5dc-bfa0-4624-8bdd-5ad5325f20fd --backupID \
    7be82451-7e89-43fb-8251-9a347ce513e0 --clusterID f098c896-5c56-48e3-9956-2552088c1018 \
    --destName wordpress-clone1 --destNamespace wordpress-clone1
Submitting clone succeeded.
Waiting for clone to become available..............................................................
...................................................................................................
....................................................................................Cloning
operation complete.
```

When the optional `--background`/`-b` argument **is** specified, the command simply initiates the clone task, and leaves it to the user to validate the clone operation completion.

```text
$ ./toolkit.py clone -b --sourceNamespace a643b5dc-bfa0-4624-8bdd-5ad5325f20fd --backupID \
    7be82451-7e89-43fb-8251-9a347ce513e0 --clusterID f098c896-5c56-48e3-9956-2552088c1018 \
    --destName wordpress-clone2 --destNamespace wordpress-clone2
Submitting clone succeeded.
Background clone flag selected, run 'list apps' to get status.
$ ./toolkit.py list apps
+------------------+--------------------------------------+-----------------+------------------+--------------+-----------+
| appName          | appID                                | clusterName     | namespace        | state        | source    |
+==================+======================================+=================+==================+==============+===========+
| wordpress        | a643b5dc-bfa0-4624-8bdd-5ad5325f20fd | useast1-cluster | wordpress        | running      | namespace |
+------------------+--------------------------------------+-----------------+------------------+--------------+-----------+
| wordpress-clone1 | 8f91e976-1250-445d-876d-d9f9da35f845 | uswest1-cluster | wordpress-clone1 | running      | namespace |
+------------------+--------------------------------------+-----------------+------------------+--------------+-----------+
| wordpress-clone2 | 040f387c-66d4-4a2f-9972-a00677a4a8e4 | uswest1-cluster | wordpress-clone2 | provisioning | namespace |
+------------------+--------------------------------------+-----------------+------------------+--------------+-----------+
```

The `clone` argument also features an interactive wizard which promts the user for any arguments not specified in the original command:

```text
$ ./toolkit.py clone -b
Select destination cluster for the clone
Index   ClusterID                               clusterName         clusterPlatform
1:      a93d150d-2171-41d9-a8b0-f94bb8e2b025    useast1-cluster     gke
2:      f098c896-5c56-48e3-9956-2552088c1018    uswest1-cluster     gke
Select a line (1-2): 2
Namespace for the clone (This must not be a namespace that currently exists on the destination cluster): wordpress-clone3
Name for the clone: wordpress-clone3
sourceNamespace and backupID are unspecified, you can pick a sourceNamespace, then select a backup of that sourceNamespace. (If a backup of that namespace doesn't exist one will be created.  Or you can specify a backupID to use directly.
sourceNamespace or backupID: sourceNamespace
Select source namespace to be cloned
Index   AppID                                   appName             clusterName         ClusterID
1:      a643b5dc-bfa0-4624-8bdd-5ad5325f20fd    wordpress           useast1-cluster     a93d150d-2171-41d9-a8b0-f94bb8e2b025
2:      8f91e976-1250-445d-876d-d9f9da35f845    wordpress-clone1    uswest1-cluster     f098c896-5c56-48e3-9956-2552088c1018
3       040f387c-66d4-4a2f-9972-a00677a4a8e4    wordpress-clone2    uswest1-cluster     f098c896-5c56-48e3-9956-2552088c1018
Select a line (1-3): 1
Select source backup
Index   BackupID                                BackupName          Timestamp               AppID
1:      7be82451-7e89-43fb-8251-9a347ce513e0    20220523-snap1      2022-05-23T18:21:20Z    a643b5dc-bfa0-4624-8bdd-5ad5325f20fd
2:      25b9ffad-dd1a-47a1-8481-8328f2aa7cf4    daily-xok21-ifrx2   2022-05-24T05:30:10Z    a643b5dc-bfa0-4624-8bdd-5ad5325f20fd
3:      75dd0128-a9a1-4e55-932e-acab589b71b2    hourly-cpesy-nhcfh  2022-05-24T12:15:15Z    a643b5dc-bfa0-4624-8bdd-5ad5325f20fd
4:      ca338a28-6f7c-4a05-913f-6e5eaf217190    hourly-cpesy-zhslc  2022-05-24T13:15:13Z    a643b5dc-bfa0-4624-8bdd-5ad5325f20fd
Select a line (1-4): 3
Submitting clone succeeded.
Background clone flag selected, run 'list apps' to get status.
$ 
$ ./toolkit.py list apps           
+------------------+--------------------------------------+-----------------+------------------+--------------+-----------+
| appName          | appID                                | clusterName     | namespace        | state        | source    |
+==================+======================================+=================+==================+==============+===========+
| wordpress        | a643b5dc-bfa0-4624-8bdd-5ad5325f20fd | useast1-cluster | wordpress        | running      | namespace |
+------------------+--------------------------------------+-----------------+------------------+--------------+-----------+
| wordpress-clone1 | 8f91e976-1250-445d-876d-d9f9da35f845 | uswest1-cluster | wordpress-clone1 | running      | namespace |
+------------------+--------------------------------------+-----------------+------------------+--------------+-----------+
| wordpress-clone2 | 040f387c-66d4-4a2f-9972-a00677a4a8e4 | uswest1-cluster | wordpress-clone2 | running      | namespace |
+------------------+--------------------------------------+-----------------+------------------+--------------+-----------+
| wordpress-clone3 | fb27f932-4201-49d0-b59b-2381428bd26a | uswest1-cluster | wordpress-clone3 | provisioning | namespace |
+------------------+--------------------------------------+-----------------+------------------+--------------+-----------+
```
