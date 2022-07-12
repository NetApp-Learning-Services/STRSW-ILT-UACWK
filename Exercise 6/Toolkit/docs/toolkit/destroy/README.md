# Destroy

The `destroy` argument allows you to destroy Astra resources, such as [backups](#backup) and and [snapshots](#snapshot).  Its opposite command is [create](../create/README.md), which allows you to create these resources.

**Use with caution**, as there is no confirmation required for these commands.

```text
$ ./toolkit.py destroy -h
usage: toolkit.py destroy [-h] {backup,snapshot} ...

optional arguments:
  -h, --help         show this help message and exit

objectType:
  {backup,snapshot}
    backup           destroy backup
    snapshot         destroy snapshot
```

## Backup

The `destroy backup` command allows you to destroy a specific application backup.  The command usage is:

```text
./toolkit.py destroy backup <appID> <backupID>
```

The command initiates the backup destruction, and then returns the command prompt, so it make take a minute for the backup to no longer be present when performing a `list backups`.

```text
$ ./toolkit.py destroy backup a643b5dc-bfa0-4624-8bdd-5ad5325f20fd \
    c06ec1e4-ae3d-4a32-bea0-771505f88203
Backup c06ec1e4-ae3d-4a32-bea0-771505f88203 destroyed
```

## Snapshot

The `destroy snapshot` command allows you to destroy a specific application snapshot.  The command usage is:

```text
./toolkit.py destroy snapshot <appID> <snapshotID>
```

The command initiates the snapshot destruction, and then returns the command prompt, so it make take a minute for the snapshot to no longer be present when performing a `list snapshot`.

```text
$ ./toolkit.py destroy snapshot a643b5dc-bfa0-4624-8bdd-5ad5325f20fd \
    3cb65a44-62a1-4157-a314-3840b761c6c8
Snapshot 3cb65a44-62a1-4157-a314-3840b761c6c8 destroyed
```
