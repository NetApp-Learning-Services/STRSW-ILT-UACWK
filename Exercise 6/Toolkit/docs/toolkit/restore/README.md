# Restore

The `restore` argument allows you to restore a [managed application](../manage/README.md#app) (that has at least one [snapshot](../create/README.md#snapshot) or [backup](../create/README.md#backup)) to a previous version.

**Note**: this command **completely replaces** the current running application without confirmation; if you do not wish to destroy the current app, please see the [clone command](../clone/README.md).

The overall command usage is:

```text
./toolkit.py restore <optionalBackgroundArg> <appID> <snapshotOrBackgroundArgument> \
    <snapshotOrBackgroundID>
```

The [appID](../list/README.md#apps) can be gathered from the [list](../list/README.md) command.

The [snapshotID](../list/README.md#snapshots) or [backupID](../list/README.md#backups) can be gathered from the [list](../list/README.md) command, or by specifying the [appID](../list/README.md#apps) with the `-h` flag:

```text
$ ./toolkit.py restore a643b5dc-bfa0-4624-8bdd-5ad5325f20fd -h
usage: toolkit.py restore [-h] [-b]
                          (--backupID {7be82451-7e89-43fb-8251-9a347ce513e0,25b9ffad-dd1a-47a1-8481-8328f2aa7cf4,11cd0c80-89ed-4826-bf36-3e7396bd33d3,75dd0128-a9a1-4e55-932e-acab589b71b2,ca338a28-6f7c-4a05-913f-6e5eaf217190} | --snapshotID {136c0d8e-d4a7-4034-a846-021f0afc0b2b,cfe3a758-3300-44a9-8abc-aec4cfa42a98,08b9d94a-e888-4359-b472-f8de0c94cdf0,84660c80-708d-4b08-8a44-abdf90ac199b,bc1e94e7-90a0-4b49-8bee-639a467e46a7,136baec8-4b56-455c-b45d-0012f6f5bb89})
                          {a643b5dc-bfa0-4624-8bdd-5ad5325f20fd}

positional arguments:
  {a643b5dc-bfa0-4624-8bdd-5ad5325f20fd}
                        appID to restore

optional arguments:
  -h, --help            show this help message and exit
  -b, --background      Run restore operation in the background
  --backupID {7be82451-7e89-43fb-8251-9a347ce513e0,25b9ffad-dd1a-47a1-8481-8328f2aa7cf4,11cd0c80-89ed-4826-bf36-3e7396bd33d3,75dd0128-a9a1-4e55-932e-acab589b71b2,ca338a28-6f7c-4a05-913f-6e5eaf217190}
                        Source backup to restore from
  --snapshotID {136c0d8e-d4a7-4034-a846-021f0afc0b2b,cfe3a758-3300-44a9-8abc-aec4cfa42a98,08b9d94a-e888-4359-b472-f8de0c94cdf0,84660c80-708d-4b08-8a44-abdf90ac199b,bc1e94e7-90a0-4b49-8bee-639a467e46a7,136baec8-4b56-455c-b45d-0012f6f5bb89}
                        Source snapshot to restore from
```

When the optional `--background`/`-b` argument is **not** specified, the command polls for the status of the restore operation every 5 seconds, and reports back once complete.

```text
./toolkit.py restore a643b5dc-bfa0-4624-8bdd-5ad5325f20fd --snapshotID \
    136c0d8e-d4a7-4034-a846-021f0afc0b2b
Restore job in progress............................................................................
...................................................................................................
........Success!
```

When the optional `--background`/`-b` argument **is** specified, the command simply initiates the restore task, and leaves it to the user to validate the restore operation completion.

```text
$ ./toolkit.py restore -b a643b5dc-bfa0-4624-8bdd-5ad5325f20fd --backupID \
    7be82451-7e89-43fb-8251-9a347ce513e0
Restore job submitted successfully
Background restore flag selected, run 'list apps' to get status
$ ./toolkit.py list apps
+-----------+--------------------------------------+-----------------+-------------+-----------+-----------+
| appName   | appID                                | clusterName     | namespace   | state     | source    |
+===========+======================================+=================+=============+===========+===========+
| wordpress | a643b5dc-bfa0-4624-8bdd-5ad5325f20fd | useast1-cluster | wordpress   | restoring | namespace |
+-----------+--------------------------------------+-----------------+-------------+-----------+-----------+
```
