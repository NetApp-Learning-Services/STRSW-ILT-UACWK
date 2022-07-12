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

import getopt
import astraSDK
import time
import sys

# Define HelpText
helpTextInfo = """
For information on the arguments to be used, use -h or --help.
NetApp DevOps Toolkit file: waitforBackup.py

createBackup creates the backup of the application managed by Astra Control.

This script requires -a/--application, -c/--cluster and -b/--backup-name parameters to be specified.

Required/Allowed Arguments:
\t-a, --application \t Name of the application whose backup is to be captured.
\t-c, --cluster \t Name of the cluster the application belongs to.
\t-b, --backup-name \t Name of the backup.

Examples:
\t python3 createBackup.py -c cluster-a -a app-a -b backup-10
\t python3 createBackup.py --cluster cluster-1 --application app-1 --backup-name backup-1
"""

timeout = (
    time.time() + 60 * 15
)  # Timeout for our example is 15 minutes, set accordingly
argumentList = sys.argv[1:]
options = "ha:b:c:"
long_options = ["help", "application=", "cluster=", "backup-name="]

try:
    arguments, values = getopt.getopt(argumentList, options, long_options)
except getopt.error:
    print("\n--------------------------------------------")
    print("Error: Invalid arguments")
    print("--------------------------------------------")
    print(helpTextInfo)
    sys.exit(0)

for arg, val in arguments:
    if arg in ("-h", "--help"):
        print(helpTextInfo)
        sys.exit(0)
    elif arg in ("-a", "--application"):
        application_name = val
    elif arg in ("-c", "--cluster"):
        cluster_name = val
    elif arg in ("-b", "--backup-name"):
        backup_name = val

try:
    print(application_name + "-" + cluster_name + "-" + backup_name)
except NameError:
    print("\n--------------------------------------------")
    print("Error: All required arguments are not passed")
    print("--------------------------------------------")
    print(helpTextInfo)
    sys.exit(0)

try:
    backupInfo = astraSDK.getBackups().main(appFilter=application_name)

    for key1 in backupInfo:
        for key2 in backupInfo[key1]:
            if key2 == backup_name:
                while backupInfo[key1][key2][1] != "completed":
                    if time.time() < timeout:
                        print("\n Waiting for the Backup to complete \n")
                        time.sleep(30)
                        backupInfo = astraSDK.getBackups().main(
                            appFilter=application_name
                        )
                if backupInfo[key1][key2][1] == "completed":
                    print("\n \n Backup Completed \n \n")
except Exception:
    print("\n----Error----")
    print("Possible Issues: ")
    print("\t1. Astra Control API is not reachable")
    print("\t2. The specified cluster is not managed by Astra Control")
    print("\t3. The specified application is not managed by Astra Control")
    print("\t4. The specified backup name is violating the naming convention")
    print("\t5. The specified backup failed or timed out")
