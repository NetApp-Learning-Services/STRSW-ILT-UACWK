# Clone

The `clone` argument allows you to clone a [managed application](../manage/README.md#app) to a destination [cluster](..list/README.md#clusters) of your choice.  You may clone from an existing [backup](../list/README.md#backups) or [snapshot](../list/README.md#snapshots), or directly from the running application.

After cloning an application, it is recommended to [create a protection policy](../create/README.md#protectionpolicy) for the new application.

The overall command usage is:

```text
./toolkit.py clone [<optionalBackgroundArg>] --cloneAppName <cloneAppName> \
    [--cloneNamespace <cloneNamespace>] --clusterID <destClusterID> \
    (--backupID <backupID> | --snapshotID <snapshotID> | --sourceAppID <sourceAppID>)
```

* `--cloneAppName`: the name of the new application
* `--cloneNamespace`: the name of the new namespace (**optional**, if not specified, the namespace is the same value as `cloneAppName`)
* `--clusterID`: the destination clusterID (it can be any cluster manged by Astra Control)
* **Only one** of the following arguments must also be specified:
  * `--backupID`: the backupID to create the clone from
  * `--snapshotID`: the snapshotID to create the clone from
  * `--sourceAppID`: a [managed application ID](../manage/README.md#app) (the clone will be created from the running application)

When the optional `--background`/`-b` argument is **not** specified, the command polls for the status of the clone operation every 3 seconds, and reports back once complete.

```text
$ ./toolkit.py clone --cloneAppName myclonedapp --clusterID af0aecb9-9b18-473f-b417-54fb38e1e28d \
    --snapshotID 8e4fafc8-9175-4f47-94b9-181ea435f60c
Submitting clone succeeded.
Waiting for clone to become available..............................................................\
..........Cloning operation complete.
```

When the optional `--background`/`-b` argument **is** specified, the command simply initiates the clone task, and leaves it to the user to validate the clone operation completion.

```text
$ ./toolkit.py clone -b --cloneAppName bgcloneapp --clusterID b81bdd8f-c2c7-40eb-a602-4af06d3c6e4d \
    --sourceAppID f24ac04c-e476-4089-9475-686848457587
Submitting clone succeeded.
Background clone flag selected, run 'list apps' to get status.
$ ./toolkit.py list apps
+------------+--------------------------------------+--------------------+-----------+--------------+
| appName    | appID                                | clusterName        | namespace | state        |
+============+======================================+====================+===========+==============+
| cassandra  | e494a651-fc80-492e-bca8-5d901047c53f | aks-eastus-cluster | cassandra | ready        |
+------------+--------------------------------------+--------------------+-----------+--------------+
| wordpress  | f24ac04c-e476-4089-9475-686848457587 | uscentral1-cluster | wordpress | ready        |
+------------+--------------------------------------+--------------------+-----------+--------------+
| bgcloneapp | 8cd0718f-098b-4978-b692-0126f678dc25 | uscentral1-cluster |           | provisioning |
+------------+--------------------------------------+--------------------+-----------+--------------+
```

The `clone` argument also features an interactive wizard which promts the user for any arguments not specified in the original command (outside of one of `--backupID`, `--snapshotID`, or `--sourceAppID` being required):

```text
$ ./toolkit.py clone -b --backupID e4436f2f-a973-4c5e-b235-f325c54926db
App name for the clone: prompt-clone
Select destination cluster for the clone
Index   ClusterID                               clusterName         clusterPlatform
1:      af0aecb9-9b18-473f-b417-54fb38e1e28d    aks-eastus-cluster  aks
2:      b81bdd8f-c2c7-40eb-a602-4af06d3c6e4d    uscentral1-cluster  gke
Select a line (1-2): 1
Submitting clone succeeded.
Background clone flag selected, run 'list apps' to get status.
$ ./toolkit.py list apps
+--------------+--------------------------------------+--------------------+-----------+--------------+
| appName      | appID                                | clusterName        | namespace | state        |
+==============+======================================+====================+===========+==============+
| cassandra    | e494a651-fc80-492e-bca8-5d901047c53f | aks-eastus-cluster | cassandra | ready        |
+--------------+--------------------------------------+--------------------+-----------+--------------+
| wordpress    | f24ac04c-e476-4089-9475-686848457587 | uscentral1-cluster | wordpress | ready        |
+--------------+--------------------------------------+--------------------+-----------+--------------+
| prompt-clone | 1f000f0a-ca24-4b27-ad48-c64ddc67836b | aks-eastus-cluster |           | provisioning |
+--------------+--------------------------------------+--------------------+-----------+--------------+
```
