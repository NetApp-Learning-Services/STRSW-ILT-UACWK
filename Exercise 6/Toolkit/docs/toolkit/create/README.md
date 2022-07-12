# Create

The `create` argument allows you to create Astra resources, including [backups](#backup), [protection policies](#protectionpolicy), and [snapshots](#snapshot).  Its opposite command is [destroy](../destroy/README.md), which allows you to destroy these same resources.

```text
$ ./toolkit.py create -h
usage: toolkit.py create [-h] {backup,protectionpolicy,snapshot} ...

optional arguments:
  -h, --help            show this help message and exit

objectType:
  {backup,protectionpolicy,snapshot}
    backup              create backup
    protectionpolicy    create protectionpolicy
    snapshot            create snapshot
```

## Backup

The `create backup` command allows you to take an ad-hoc backup.  The command usage is:

```text
./toolkit.py create backup <optionalBackgroundArg> <appID> <backupName>
```

When the optional `--background`/`-b` argument is **not** specified, the command polls for the status of the backup operation every 5 seconds, and reports back once complete.

```text
$ ./toolkit.py create backup a643b5dc-bfa0-4624-8bdd-5ad5325f20fd 20220523-cli-backup1
Starting backup of a643b5dc-bfa0-4624-8bdd-5ad5325f20fd
Waiting for backup to complete.....................................................................
..................................................................complete!
```

When the optional `--background`/`-b` argument **is** specified, the command simply initiates the backup task, and leaves it to the user to validate the backup completion.

```text
$ ./toolkit.py create backup -b a643b5dc-bfa0-4624-8bdd-5ad5325f20fd 20220523-cli-backup2
Starting backup of a643b5dc-bfa0-4624-8bdd-5ad5325f20fd
Background backup flag selected, run 'list backups' to get status
$ ./toolkit.py list backups
+--------------------------------------+----------------------+--------------------------------------+---------------+
| AppID                                | backupName           | backupID                             | backupState   |
+======================================+======================+======================================+===============+
| a643b5dc-bfa0-4624-8bdd-5ad5325f20fd | hourly-cpesy-g82fd   | 2ce7996a-3b21-4dc7-ae5f-7c287c479f7e | completed     |
+--------------------------------------+----------------------+--------------------------------------+---------------+
| a643b5dc-bfa0-4624-8bdd-5ad5325f20fd | 20220523-cli-backup1 | 7be82451-7e89-43fb-8251-9a347ce513e0 | completed     |
+--------------------------------------+----------------------+--------------------------------------+---------------+
| a643b5dc-bfa0-4624-8bdd-5ad5325f20fd | 20220523-cli-backup2 | c06ec1e4-ae3d-4a32-bea0-771505f88203 | running       |
+--------------------------------------+----------------------+--------------------------------------+---------------+
```

## Protectionpolicy

The `create protectionpolicy` command allows you to create (or add to) a protection policy for a [managed application](../manage/README.md#app).  The high level command usage is:

```text
./toolkit.py create protectionpolicy <appID> -g <granularity> <date/time args> \
    -b <backupsToRetain> -s <snapshotsToRetain>
```

The \<appID\> argument can be gathered from a [list apps](../list/README.md#apps) command.

To configure a protection policy with all four protection schedules, the `create protectionpolicy` command must be ran four times, once for each level of granularity:

* [Hourly](#hourly)
* [Daily](#daily)
* [Weekly](#weekly)
* [Monthly](#monthly)

There are four total \<date/time arguments\>, which either must be entered, must not be entered, are optional, or not applicable, depending upon the granularity level chosen:

| DateTime \ Granularity | Hourly   | Daily    | Weekly   | Monthly  |
| ---------------------- | -------- | -------- | -------- | -------- |
| `-m` / `--minute`      | Must     | Optional | Optional | Optional |
| `-H` / `--hour`        | Must Not | Must     | Must     | Must     |
| `-W` / `--dayOfWeek`   | N/A      | N/A      | Must     | Must Not |
| `-M` / `--dayOfMonth`  | N/A      | N/A      | N/A      | Must     |

The possible values for the \<date/time arguments\> are as follows:

* **`-m` / `--minute`**: Between 0 and 59, inclusive, with 0 as the default if not specified.
* **`-H` / `--hour`**: Between 0 and 23, inclusive (UTC).
* **`-W` / `--dayOfWeek`**: Between 0 and 6, inclusive, with 0 representing Sunday, and 6 Saturday.
* **`-M` / `--dayOfMonth`**: Between 1 and 31, inclusive.

The `--backupRetention`/`-b` and `--snapshotRetention`/`-s` arguments specify the number of backups and snapshots to store, respectively.  Both arguments are required, and can be any number between **0 and 59**, inclusive.

### Hourly

This example creates an `hourly` protection schedule, on the 15 minute mark, while keeping the last two backups and last three snapshots.

```text
$ ./toolkit.py create protectionpolicy a643b5dc-bfa0-4624-8bdd-5ad5325f20fd -g hourly \
    -m 15 -b 2 -s 3
{"type": "application/astra-schedule", "version": "1.1", "id": "c94a0c35-4e24-4664-b3f5-211e5aecf498", "name": "hourly-cpesy", "enabled": "true", "granularity": "hourly", "minute": "15", "snapshotRetention": "3", "backupRetention": "2", "metadata": {"labels": [], "creationTimestamp": "2022-05-23T16:03:23Z", "modificationTimestamp": "2022-05-23T16:03:23Z", "createdBy": "8146d293-d897-4e16-ab10-8dca934637ab"}}
```

### Daily

This example creates a `daily` protection schedule, at 05:30 UTC, while keeping the last two backups and last two snapshots.

```text
$ ./toolkit.py create protectionpolicy a643b5dc-bfa0-4624-8bdd-5ad5325f20fd -g daily \
    -H 5 -m 30 -b 2 -s 2
{"type": "application/astra-schedule", "version": "1.1", "id": "cbd5edd2-21c9-4283-a7cc-4eaae5c25952", "name": "daily-xok21", "enabled": "true", "granularity": "daily", "minute": "30", "hour": "5", "snapshotRetention": "2", "backupRetention": "2", "metadata": {"labels": [], "creationTimestamp": "2022-05-23T16:07:54Z", "modificationTimestamp": "2022-05-23T16:07:54Z", "createdBy": "8146d293-d897-4e16-ab10-8dca934637ab"}}
```

### Weekly

This example creates a `weekly` protection schedule, on Sundays at 04:45 UTC, while keeping the last backup and last snapshot.

```text
$ ./toolkit.py create protectionpolicy a643b5dc-bfa0-4624-8bdd-5ad5325f20fd -g weekly \
    -W 0 -H 4 -m 45 -b 1 -s 1
{"type": "application/astra-schedule", "version": "1.1", "id": "aa174808-4f8c-4a0b-839e-5ceecf7c0f2d", "name": "weekly-uh8hq", "enabled": "true", "granularity": "weekly", "minute": "45", "hour": "4", "dayOfWeek": "0", "snapshotRetention": "1", "backupRetention": "1", "metadata": {"labels": [], "creationTimestamp": "2022-05-23T16:23:36Z", "modificationTimestamp": "2022-05-23T16:23:36Z", "createdBy": "8146d293-d897-4e16-ab10-8dca934637ab"}}
```

### Monthly

This example creates a `monthly` protection schedule, on the 1st day of the month at 03:45 UTC, while keeping the last backup and last snapshot.

```text
./toolkit.py create protectionpolicy a643b5dc-bfa0-4624-8bdd-5ad5325f20fd -g monthly \
    -M 1 -H 3 -m 45 -b 1 -s 1
{"type": "application/astra-schedule", "version": "1.1", "id": "f9dad3d7-a085-4e07-99be-88a90fc8362b", "name": "monthly-teds6", "enabled": "true", "granularity": "monthly", "minute": "45", "hour": "3", "dayOfMonth": "1", "snapshotRetention": "1", "backupRetention": "1", "metadata": {"labels": [], "creationTimestamp": "2022-05-23T16:24:52Z", "modificationTimestamp": "2022-05-23T16:24:52Z", "createdBy": "8146d293-d897-4e16-ab10-8dca934637ab"}}
```

## Snapshot

The `create snapshot` command allows you to take an ad-hoc snapshot.  The command usage is:

```text
./toolkit.py create snapshot <optionalBackgroundArg> <appID> <snapshotName>
```

When the optional `--background`/`-b` argument is **not** specified, the command polls for the status of the snapshot operation every 5 seconds, and reports back once complete.

```text
$ ./toolkit.py create snapshot a643b5dc-bfa0-4624-8bdd-5ad5325f20fd 20220523-cli-snap1
Starting snapshot of a643b5dc-bfa0-4624-8bdd-5ad5325f20fd
Waiting for snapshot to complete.....complete!
```

When the optional `--background`/`-b` argument **is** specified, the command simply initiates the snapshot task, and leaves it to the user to validate the snapshot completion.

```text
./toolkit.py create snapshot -b a643b5dc-bfa0-4624-8bdd-5ad5325f20fd 20220523-cli-snap2
Starting snapshot of a643b5dc-bfa0-4624-8bdd-5ad5325f20fd
Background snapshot flag selected, run 'list snapshots' to get status
$ ./toolkit.py list snapshots
+--------------------------------------+-----------------------------------+--------------------------------------+-----------------+
| appID                                | snapshotName                      | snapshotID                           | snapshotState   |
+======================================+===================================+======================================+=================+
| a643b5dc-bfa0-4624-8bdd-5ad5325f20fd | wordpress-snapshot-20220523161542 | 04354edd-3f53-4479-9829-ca3723021c3e | completed       |
+--------------------------------------+-----------------------------------+--------------------------------------+-----------------+
| a643b5dc-bfa0-4624-8bdd-5ad5325f20fd | 20220523-cli-snap1                | 136c0d8e-d4a7-4034-a846-021f0afc0b2b | completed       |
+--------------------------------------+-----------------------------------+--------------------------------------+-----------------+
| a643b5dc-bfa0-4624-8bdd-5ad5325f20fd | 20220523-cli-snap2                | 3cb65a44-62a1-4157-a314-3840b761c6c8 | running         |
+--------------------------------------+-----------------------------------+--------------------------------------+-----------------+

```
