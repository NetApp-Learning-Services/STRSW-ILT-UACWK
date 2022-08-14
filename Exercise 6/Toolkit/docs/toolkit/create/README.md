# Create

The `create` argument allows you to create Astra resources, including:

* [Backups](#backup)
* [Hooks](#hook)
* [Protection policies](#protectionpolicy)
* [Scripts](#script)
* [Snapshots](#snapshot)

Its opposite command is [destroy](../destroy/README.md), which allows you to destroy these same resources.

```text
$ ./toolkit.py create -h
usage: toolkit.py create [-h] {backup,protectionpolicy,script,snapshot} ...

optional arguments:
  -h, --help            show this help message and exit

objectType:
  {backup,protectionpolicy,script,snapshot}
    backup              create backup
    protectionpolicy    create protectionpolicy
    script              create script (hook source)
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
+--------------------------------------+----------------------+--------------------------------------+-------------+
| AppID                                | backupName           | backupID                             | backupState |
+======================================+======================+======================================+=============+
| a643b5dc-bfa0-4624-8bdd-5ad5325f20fd | hourly-cpesy-g82fd   | 2ce7996a-3b21-4dc7-ae5f-7c287c479f7e | completed   |
+--------------------------------------+----------------------+--------------------------------------+-------------+
| a643b5dc-bfa0-4624-8bdd-5ad5325f20fd | 20220523-cli-backup1 | 7be82451-7e89-43fb-8251-9a347ce513e0 | completed   |
+--------------------------------------+----------------------+--------------------------------------+-------------+
| a643b5dc-bfa0-4624-8bdd-5ad5325f20fd | 20220523-cli-backup2 | c06ec1e4-ae3d-4a32-bea0-771505f88203 | ready       |
+--------------------------------------+----------------------+--------------------------------------+-------------+
```

## Hook

The `create hook` command allows you to create an application execution hook for an [application](../manage/README.md#app).  The high level command usage is:

```text
./toolkit.py create hook <appID> <hookName> <scriptID> -o <operationType> \
    -a <optionalHookArg1> <optionalHookArgX> -r <optionalContainerRegex>
```

Additional information on each argument is as follows:

* `appID` can be gathered from a [list apps](../list/README.md#apps) command
* `hookName` is the friendly name of your choice
* `scriptID` can be gathered from a [list scripts](../list/README.md#scripts) command
* `-o`/`--operation` must be one of:
  * pre-snapshot
  * post-snapshot
  * pre-backup
  * post-backup
  * post-restore
* `-a`/`--hookArguments` are (optional) command line arguments that *may* be required depending upon the script defined via the `scriptID`.  Any number of arguments can be provided.
* `-r`/`--containerRegex` is an (optional) way to provide container image name matching criteria, based on [regular expressions](https://docs.netapp.com/us-en/astra-control-service/use/manage-app-execution-hooks.html).  If special characters are required for the regex, please encase the value in quotes.  If this argument is not provided, then this execution hook applies to **all** container images within the application.

This example creates a "post-snapshot" execution hook for appID "7b647ab6-834b-4553-9b23-02ecdd8562f7" named "wordpress-mariadb-post-snapshot", and provides the command line argument "post" to scriptID "41bd1ee4-6283-4e6b-a9f0-a4b29de3fb3d".  Since a container regex is not provided, it matches on all images within the app.

```text
$ ./toolkit.py create hook 7b647ab6-834b-4553-9b23-02ecdd8562f7 wordpress-post-snapshot 41bd1ee4-6283-4e6b-a9f0-a4b29de3fb3d -o post-snapshot -a post
{"metadata": {"labels": [], "creationTimestamp": "2022-08-03T18:43:58Z", "modificationTimestamp": "2022-08-03T18:43:58Z", "createdBy": "59c784bb-9b28-4da5-ae8a-f20794ec562f"}, "type": "application/astra-executionHook", "version": "1.0", "id": "6f9e8190-96fd-420c-be36-7324c6b54ce1", "name": "wordpress-post-snapshot", "hookType": "custom", "action": "snapshot", "stage": "post", "hookSourceID": "41bd1ee4-6283-4e6b-a9f0-a4b29de3fb3d", "arguments": ["post"], "appID": "7b647ab6-834b-4553-9b23-02ecdd8562f7", "enabled": "true"}
```

This example creates a "pre-backup" execution hook for appID "7b647ab6-834b-4553-9b23-02ecdd8562f7" named "wordpress-mariadb-pre-snap", provides the command line argument "pre" to scriptID "41bd1ee4-6283-4e6b-a9f0-a4b29de3fb3d", and only runs agains containers with a matching regex of "\bmariadb\b" (**note** the quotes).

```text
$ ./toolkit.py create hook 7b647ab6-834b-4553-9b23-02ecdd8562f7 wordpress-mariadb-pre-snap 41bd1ee4-6283-4e6b-a9f0-a4b29de3fb3d -o pre-backup -a pre -r "\bmariadb\b"
{"metadata": {"labels": [], "creationTimestamp": "2022-08-03T18:57:39Z", "modificationTimestamp": "2022-08-03T18:57:39Z", "createdBy": "59c784bb-9b28-4da5-ae8a-f20794ec562f"}, "type": "application/astra-executionHook", "version": "1.0", "id": "f2da43bd-0278-4f21-b9b6-ea64a7247423", "name": "wordpress-mariadb-pre-snap", "hookType": "custom", "matchingCriteria": [{"type": "containerImage", "value": "\\bmariadb\\b"}], "action": "backup", "stage": "pre", "hookSourceID": "41bd1ee4-6283-4e6b-a9f0-a4b29de3fb3d", "arguments": ["pre"], "appID": "7b647ab6-834b-4553-9b23-02ecdd8562f7", "enabled": "true"}
```

This example creates a "post-restore" execution hook for appID "eebd59f2-e9b3-47b0-b0e8-1306d805f104" named "cassandra-post-restore", provides two separate command line arguments ("post-restore" and "false") to scriptID "db17a907-9518-4836-850f-1d21bc7651d7", and only runs against containers with a matching regex of "\bcassandra\b" (**note** the quotes).

```text
$ ./toolkit.py create hook eebd59f2-e9b3-47b0-b0e8-1306d805f104 cassandra-post-restore db17a907-9518-4836-850f-1d21bc7651d7 -o post-restore -a post-restore false -r "\bcassandra\b" 
{"metadata": {"labels": [], "creationTimestamp": "2022-08-03T19:01:22Z", "modificationTimestamp": "2022-08-03T19:01:22Z", "createdBy": "59c784bb-9b28-4da5-ae8a-f20794ec562f"}, "type": "application/astra-executionHook", "version": "1.0", "id": "a1a1ca43-1aee-4707-a514-0f251a336e06", "name": "cassandra-post-restore", "hookType": "custom", "matchingCriteria": [{"type": "containerImage", "value": "\\bcassandra\\b"}], "action": "restore", "stage": "post", "hookSourceID": "db17a907-9518-4836-850f-1d21bc7651d7", "arguments": ["post-restore", "false"], "appID": "eebd59f2-e9b3-47b0-b0e8-1306d805f104", "enabled": "true"}
```

## Protectionpolicy

The `create protectionpolicy` command allows you to create (or add to) a protection policy for an [application](../manage/README.md#app).  The high level command usage is:

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

## Script

The `create script` command allows you to create a script (aka hook source).  The command usage is:

```text
./toolkit.py create script <name> <filePath> -d <optionalDescription>
```

The `name` argument is the friendly name of the script, which must not already exist on the system (a 400 error will be thrown if the name is not unique).

The `filePath` argument must be the local filesystem location of the script, either relative or absolute path.

The `-d`/`--description` argument is completely optional, and can be placed anywhere after the third argument (script).

```text
$ ./toolkit.py create script cassandra ~/Verda/Cassandra/cassandra-snap-hooks.sh
{"metadata": {"labels": [], "creationTimestamp": "2022-08-02T14:44:00Z", "modificationTimestamp": "2022-08-02T14:44:00Z", "createdBy": "7cc9170d-d227-49ac-bf9e-6b080ce59524"}, "type": "application/astra-hookSource", "version": "1.0", "id": "6d1f7589-7f0b-4211-99f7-63f69e2495bf", "name": "cassandra", "private": "false", "preloaded": "false", "sourceType": "script", "source": "IyEvYmluL3NoCiMKCiMgY2Fzc2FuZHJhLXNuYXAtaG9va3Muc2gKIwojIFByZS0gYW5kIHBvc3Qtc25hcHNob3QgZXhlY3V0aW9uIGhvb2tzIGZvciBDYXNzYW5kcmEuCiMgVGVzdGVkIHdpdGggQ2Fzc2FuZHJhIDQuMC40IChkZXBsb3llZCBieSBCaXRuYW1pIGhlbG0gY2hhcnQgOS4yLjUpIGFuZCBOZXRBcHAgQXN0cmEgQ29udHJvbCBTZXJ2aWNlIDIyLjA0LgojCiMgYXJnczogW3ByZXxwb3N0XQojIHByZTogZmx1c2ggYWxsIGtleXNwYWNlcyBhbmQgdGFibGVzIGJ5ICJub2RldG9vbCBmbHVzaCIKIyBwb3N0OiBjaGVjayBhbGwgdGFibGVzICgibm9kZXRvb2wgdmVyaWZ5IikKIwojIFRoZSBjdXJyZW50IHZlcnNpb24gb2YgQXN0cmEgQ29udHJvbCBjYW4gb25seSB0YXJnZXQgdGhlIGNvbnRhaW5lcnMgdG8gZXhlY3V0ZSBob29rcyBieSBpbWFnZSBuYW1lLiBUaGUgaG9vayB3aWxsIHJ1biBmb3IgYW55IGNvbnRhaW5lciBpbWFnZSAKIyB0aGF0IG1hdGNoZXMgdGhlIHByb3ZpZGVkIHJlZ3VsYXIgZXhwcmVzc2lvbiBydWxlIGluIEFzdHJhIENvbnRyb2wuCiMKIyBBIHJlc3RvcmUgb3BlcmF0aW9uIHRvIGEgbmV3IG5hbWVzcGFjZSBvciBjbHVzdGVyIHJlcXVpcmVzIHRoYXQgdGhlIG9yaWdpbmFsIGluc3RhbmNlIG9mIHRoZSBhcHBsaWNhdGlvbiB0byBiZSB0YWtlbiBkb3duLiBUaGlzIGlzIHRvIGVuc3VyZSAKIyB0aGF0IHRoZSBwZWVyIGdyb3VwIGluZm9ybWF0aW9uIGNhcnJpZWQgb3ZlciBkb2VzIG5vdCBsZWFkIHRvIGNyb3NzLWluc3RhbmNlIGNvbW11bmljYXRpb24uIENsb25pbmcgb2YgdGhlIGFwcCB3aWxsIG5vdCB3b3JrLgoKIyB1bmlxdWUgZXJyb3IgY29kZXMgZm9yIGV2ZXJ5IGVycm9yIGNhc2UKZWJhc2U9MTAwCmV1c2FnZT0kKChlYmFzZSsxKSkKZWJhZHN0YWdlPSQoKGViYXNlKzIpKQplcHJlPSQoKGViYXNlKzMpKQplcG9zdD0kKChlYmFzZSs0KSkKCiMKIyBXcml0ZXMgdGhlIGdpdmVuIG1lc3NhZ2UgdG8gc3RhbmRhcmQgb3V0cHV0CiMKIyAkKiAtIFRoZSBtZXNzYWdlIHRvIHdyaXRlCiMKbXNnKCkgewogICAgZWNobyAiJCoiCn0KCiMKIyBXcml0ZXMgdGhlIGdpdmVuIGluZm9ybWF0aW9uIG1lc3NhZ2UgdG8gc3RhbmRhcmQgb3V0cHV0CiMKIyAkKiAtIFRoZSBtZXNzYWdlIHRvIHdyaXRlCiMKaW5mbygpIHsKICAgIG1zZyAiSU5GTzogJCoiCn0KCiMKIyBXcml0ZXMgdGhlIGdpdmVuIGVycm9yIG1lc3NhZ2UgdG8gc3RhbmRhcmQgZXJyb3IKIwojICQqIC0gVGhlIG1lc3NhZ2UgdG8gd3JpdGUKIwplcnJvcigpIHsKICAgIG1zZyAiRVJST1I6ICQqIiAxPiYyCn0KCiMKIyBSdW4gcXVpZXNjZSBzdGVwcyBoZXJlCiMKcXVpZXNjZSgpIHsKICAgIGluZm8gIlF1aWVzY2luZyBDYXNzYW5kcmEgLSBmbHVzaGluZyBhbGwga2V5c3BhY2VzIGFuZCB0YWJsZXMiCiAgICBub2RldG9vbCBmbHVzaAogICAgcmM9JD8KICAgIGlmIFsgJHtyY30gLW5lIDAgXTsgdGhlbgogICAgICAgIHJjPSR7ZXByZX0KICAgIGZpCiAgICByZXR1cm4gJHtyY30KfQoKIwojIFJ1biB1bnF1aWVzY2Ugc3RlcHMgaGVyZQojCnVucXVpZXNjZSgpIHsKICAgIGluZm8gIlVucXVpZXNjaW5nIENhc3NhbmRyYSIKICAgIG5vZGV0b29sIHZlcmlmeQogICAgcmM9JD8KICAgIGlmIFsgJHtyY30gLW5lIDAgXTsgdGhlbgogICAgICAgIHJjPSR7ZXBvc3R9CiAgICBmaQogICAgcmV0dXJuICR7cmN9Cn0KCiMKIyBtYWluCiMKCiMgY2hlY2sgYXJnCnN0YWdlPSQxCmlmIFsgLXogIiR7c3RhZ2V9IiBdOyB0aGVuCiAgICBlY2hvICJVc2FnZTogJDAgPHByZXxwb3N0PiIKICAgIGV4aXQgJHtldXNhZ2V9CmZpCgppZiBbICIke3N0YWdlfSIgIT0gInByZSIgXSAmJiBbICIke3N0YWdlfSIgIT0gInBvc3QiIF07IHRoZW4KICAgIGVjaG8gIkludmFsaWQgYXJnOiAke3N0YWdlfSIKICAgIGV4aXQgJHtlYmFkc3RhZ2V9CmZpCgojIGxvZyBzb21ldGhpbmcgdG8gc3Rkb3V0CmluZm8gIlJ1bm5pbmcgJDAgJHtzdGFnZX0iCgppZiBbICIke3N0YWdlfSIgPSAicHJlIiBdOyB0aGVuCiAgICBxdWllc2NlCiAgICByYz0kPwogICAgaWYgWyAke3JjfSAtbmUgMCBdOyB0aGVuCiAgICAgICAgZXJyb3IgIkVycm9yIGR1cmluZyBwcmUtc25hcHNob3QgaG9vayIKICAgIGZpCmZpCgppZiBbICIke3N0YWdlfSIgPSAicG9zdCIgXTsgdGhlbgogICAgdW5xdWllc2NlCiAgICByYz0kPwogICAgaWYgWyAke3JjfSAtbmUgMCBdOyB0aGVuCiAgICAgICAgZXJyb3IgIkVycm9yIGR1cmluZyBwb3N0LXNuYXBzaG90IGhvb2siCiAgICBmaQpmaQoKZXhpdCAke3JjfQ==", "sourceMD5Checksum": "9242a7d82682b9ef15fb460b28d1767a"}
```

```text
$ ./toolkit.py create script -d "example script upload" testScript example.sh
{"metadata": {"labels": [], "creationTimestamp": "2022-08-02T14:41:51Z", "modificationTimestamp": "2022-08-02T14:41:51Z", "createdBy": "7cc9170d-d227-49ac-bf9e-6b080ce59524"}, "type": "application/astra-hookSource", "version": "1.0", "id": "b5cb8496-65e9-4e62-addf-bbfe08b7f3bd", "name": "testScript", "private": "false", "preloaded": "false", "sourceType": "script", "source": "IyEvYmluL2Jhc2gKZWNobyAidGhpcyBpcyBqdXN0IGFuIGV4YW1wbGUi", "sourceMD5Checksum": "8ad9d02befca7ef9a0fd51f7ec4aebe7", "description": "test upload"}
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
+--------------------------------------+-----------------------------------+--------------------------------------+---------------+
| appID                                | snapshotName                      | snapshotID                           | snapshotState |
+======================================+===================================+======================================+===============+
| a643b5dc-bfa0-4624-8bdd-5ad5325f20fd | wordpress-snapshot-20220523161542 | 04354edd-3f53-4479-9829-ca3723021c3e | completed     |
+--------------------------------------+-----------------------------------+--------------------------------------+---------------+
| a643b5dc-bfa0-4624-8bdd-5ad5325f20fd | 20220523-cli-snap1                | 136c0d8e-d4a7-4034-a846-021f0afc0b2b | completed     |
+--------------------------------------+-----------------------------------+--------------------------------------+---------------+
| a643b5dc-bfa0-4624-8bdd-5ad5325f20fd | 20220523-cli-snap2                | 3cb65a44-62a1-4157-a314-3840b761c6c8 | ready         |
+--------------------------------------+-----------------------------------+--------------------------------------+---------------+

```
