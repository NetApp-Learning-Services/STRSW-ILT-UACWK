# Destroy

The `destroy` argument allows you to destroy Astra resources.  Its opposite command is [create](../create/README.md), which allows you to create these resources.

**Use with caution**, as there is no confirmation required for these commands.

* [Backup](#backup)
* [Hook](#hook)
* [Script](#script)
* [Snapshot](#snapshot)

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

## Hook

The `destroy hook` command allows you to destroy a specific application execution hook.  The command usage is:

```text
./toolkit.py destroy hook <appID> <hookID>
```

Sample output:

```text
$ ./toolkit.py destroy hook 7b647ab6-834b-4553-9b23-02ecdd8562f7 \
    6f9e8190-96fd-420c-be36-7324c6b54ce1
Hook 6f9e8190-96fd-420c-be36-7324c6b54ce1 destroyed
```

## Script

The `destroy script` command allows you to destroy a specific script (aka hook source).  The command usage is:

```text
./toolkit.py destroy script <scriptID>
```

Sample output:

```text
$ ./toolkit.py destroy script 879655c8-29e2-4131-bff2-1c654e093291
Script 879655c8-29e2-4131-bff2-1c654e093291 destroyed
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
