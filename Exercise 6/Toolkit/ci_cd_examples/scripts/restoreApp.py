#!/usr/bin/env python
"""
   Copyright 2021 NetApp, Inc

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import time
from func_timeout import func_timeout, FunctionTimedOut
import astraSDK
import argparse

errorText = """
----Error----
Possible Issues:
  1. Astra Control API is not reachable.
  2. The specified clusters are not reachable.
  3. The specified application namespace is not available.
  4. The specified application resources are not running.
  5. The connection to S3 bucket may be interrupted.
"""


class AppDoesNotExistinAstraControl(Exception):
    """Error raised when the specified application doesn't exist within Astra Control"""

    pass


class BackupDoesNotExistinAstraControl(Exception):
    """Error raised when the specified backup doesn't exist within Astra Control"""

    pass


class SnapshotDoesNotExistinAstraControl(Exception):
    """Error raised when the specified snapshot doesn't exist within Astra Control"""

    pass


def getAppID(app_name):
    Apps = astraSDK.getApps().main()
    for key1 in Apps:
        if Apps[key1][0] == app_name:
            app_id = key1
            return app_id
    error = "Application " + app_name + " does not exist in Astra Control"
    print("Error: " + error)
    raise AppDoesNotExistinAstraControl(error)


def getBackupID(app_name, backup_name):
    Backups = astraSDK.getBackups().main(appFilter=app_name)
    for key1 in Backups:
        for key2 in Backups[key1]:
            if key2 == backup_name:
                backup_id = Backups[key1][key2][0]
                return backup_id
    error = (
        "Backup "
        + backup_name
        + " does not exist with application "
        + app_name
        + " in Astra Control"
    )
    print("Error: " + error)
    raise BackupDoesNotExistinAstraControl(error)


def getSnapshotID(app_name, snap_name):
    Snapshots = astraSDK.getSnaps().main(appFilter=app_name)
    for key1 in Snapshots:
        for key2 in Snapshots[key1]:
            if key2 == snap_name:
                snapshot_id = Snapshots[key1][key2][0]
                return snapshot_id
    error = (
        "Snapshot "
        + snap_name
        + " does not exist with application "
        + app_name
        + " in Astra Control"
    )
    print("Error: " + error)
    raise SnapshotDoesNotExistinAstraControl(error)


def wait_for_restore(app_name):
    appInfo = astraSDK.getApps().main()
    for key1 in appInfo:
        if appInfo[key1][0] == app_name:
            while appInfo[key1][4] != "running":
                if appInfo[key1][4] == "removed" or appInfo[key1][4] == "failed":
                    print("\n Application restore failed! \n \n")
                    print(errorText)
                    return False
                print("Waiting for the restore to complete ... \n")
                time.sleep(30)
                appInfo = astraSDK.getApps().main()

            if appInfo[key1][4] == "running":
                print("Application restore completed! \n")
                return True


if __name__ == "__main__":
    timeout = 60 * 30  # Set the timeout to desired value based on the application.

    parser = argparse.ArgumentParser(
        prog="python3 restoreApp.py",
        description=(
            "restoreApp restores the app managed by "
            + "Astra Control to a previous backup or snapshot"
        ),
    )
    mutual_exclusive_group = parser.add_mutually_exclusive_group(required=True)

    parser.add_argument(
        "-a",
        "--application-name",
        type=str,
        required=True,
        dest="application",
        help="The name of the application which needs to be restored",
    )

    mutual_exclusive_group.add_argument(
        "-B",
        "--use-backup",
        type=str,
        required=False,
        dest="use_backup",
        help="The backup from which the application will be restored",
    )

    mutual_exclusive_group.add_argument(
        "-S",
        "--use-snapshot",
        type=str,
        required=False,
        dest="use_snapshot",
        help="The snapshot from which the application will be restored",
    )

    args = parser.parse_args()

    app_id = getAppID(args.application)

    if args.use_backup:
        source_backup_id = getBackupID(
            app_name=args.application, backup_name=args.use_backup
        )
        RestoreApp = astraSDK.restoreApp(quiet=False).main(
            appID=app_id, backupID=source_backup_id
        )

    elif args.use_snapshot:
        source_snapshot_id = getSnapshotID(
            app_name=args.application, snap_name=args.use_snapshot
        )
        RestoreApp = astraSDK.restoreApp(quiet=False).main(
            appID=app_id, snapshotID=source_snapshot_id
        )

    if RestoreApp == "False":
        print("\n \n Application restore failed! \n \n")
        print(errorText)
        print(RestoreApp)
    else:
        print("\nApplication restore initiated. \n")

    try:
        wait_for_restore_ret = func_timeout(
            timeout, wait_for_restore, kwargs={"app_name": args.application}
        )
    except FunctionTimedOut as timexc:
        print("\n Application restore timed out and terminated \n")
        print(timexc)
