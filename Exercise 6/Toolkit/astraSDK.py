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

import inspect
import os
import sys
import yaml
import json
import copy
from tabulate import tabulate
from termcolor import colored
import requests
from urllib3 import disable_warnings
from datetime import datetime, timedelta


class getConfig:
    """In order to make API calls to Astra Control we need to know which Astra Control instance
    to connect to, and the credentials to make calls.  This info is found in config.yaml,
    which we search for in the following four places:
    1) The directory that astraSDK.py is located in
    2) ~/.config/astra-toolkits/
    3) /etc/astra-toolkits/
    4) The directory pointed to by the shell env var ASTRATOOLKITS_CONF
    """

    def __init__(self):
        path = sys.argv[0] or inspect.getfile(getConfig)
        self.conf = None
        for loc in (
            os.path.realpath(os.path.dirname(path)),
            os.path.join(os.path.expanduser("~"), ".config", "astra-toolkits"),
            "/etc/astra-toolkits",
            os.environ.get("ASTRATOOLKITS_CONF"),
        ):
            # loc could be None, which would blow up os.path.join()
            if loc:
                configFile = os.path.join(loc, "config.yaml")
            else:
                continue
            try:
                if os.path.isfile(configFile):
                    with open(configFile, "r") as f:
                        self.conf = yaml.safe_load(f)
                        break
            except IOError:
                continue
            except yaml.YAMLError:
                print(f"{configFile} not valid YAML")
                continue

        if self.conf is None:
            print("config.yaml not found.")
            sys.exit(4)

        for item in ["astra_project", "uid", "headers"]:
            try:
                assert self.conf.get(item) is not None
            except AssertionError:
                print(f"{item} is a required field in {configFile}")
                sys.exit(3)

        if "." in self.conf.get("astra_project"):
            self.base = "https://%s/accounts/%s/" % (
                self.conf.get("astra_project"),
                self.conf.get("uid"),
            )
        else:
            self.base = "https://%s.astra.netapp.io/accounts/%s/" % (
                self.conf.get("astra_project"),
                self.conf.get("uid"),
            )
        self.headers = self.conf.get("headers")

        if self.conf.get("verifySSL") is False:
            disable_warnings()
            self.verifySSL = False
        else:
            self.verifySSL = True

    def main(self):
        return {
            "base": self.base,
            "headers": self.headers,
            "verifySSL": self.verifySSL,
        }


class SDKCommon:
    def __init__(self):
        self.conf = getConfig().main()
        self.base = self.conf.get("base")
        self.headers = self.conf.get("headers")
        self.verifySSL = self.conf.get("verifySSL")

    def apicall(self, method, url, data, headers, params, verify, quiet=False):
        """Make a call using the requests module.
        method can be get, put, post, patch, or delete"""
        try:
            r = getattr(requests, method)
        except AttributeError as e:
            raise SystemExit(e)
        try:
            ret = r(url, json=data, headers=headers, params=params, verify=verify)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)
        if not ret.ok and not quiet:
            if ret.status_code >= 400 and ret.status_code < 500:
                if "x-pcloud-accountid" in ret.text:
                    print("preflight API call to Astra Control failed (check uid in config.json)")
                elif ret.status_code == 401:
                    print(
                        "preflight API call to Astra Control failed "
                        "(check Authoriztion in config.json)"
                    )
                print(f"API HTTP Status Code: {ret.status_code} - {ret.reason}")
                print(f"text: {ret.text}")
            else:
                print("preflight API call to Astra Control failed (Internal Server Error)")
                print(f"API HTTP Status Code: {ret.status_code} - {ret.reason}")
                print(f"text: {ret.text}")
        return ret

    def jsonifyResults(self, requestsObject):
        try:
            results = requestsObject.json()
        except ValueError as e:
            print(f"response contained invalid JSON: {e}")
            results = None
        return results


class getApps(SDKCommon):
    """List all apps known to Astra.  With App 2.0 API spec in the Aug 2022 release, there's
    no longer a "discovered" or "ignored" construct with apps.  There's simply managed apps
    (which is what this class covers), or yet-to-be-managed (referred to as unmanaged) apps,
    which are handled by the getNamespaces class.

    Therefore this class cannot list all of the managed and unmanaged apps.
    """

    def __init__(self, quiet=True, verbose=False, output="json"):
        """quiet: Will there be CLI output or just return (datastructure)
        verbose: Print all of the ReST call info: URL, Method, Headers, Request Body
        output: table: pretty print the data
                json: (default) output in JSON
                yaml: output in yaml"""
        self.quiet = quiet
        self.verbose = verbose
        self.output = output
        super().__init__()

    def main(
        self,
        namespace=None,
        cluster=None,
    ):
        """namespace: Filter by the namespace the app is in
        cluster: Filter by a specific k8s cluster"""

        endpoint = "k8s/v2/apps"
        params = {}
        url = self.base + endpoint
        data = {}

        if self.verbose:
            print(colored(f"API URL: {url}", "green"))
            print(colored("API Method: GET", "green"))
            print(colored(f"API Headers: {self.headers}", "green"))
            print(colored(f"API data: {data}", "green"))
            print(colored(f"API params: {params}", "green"))

        ret = super().apicall("get", url, data, self.headers, params, self.verifySSL)

        if self.verbose:
            print(f"API HTTP Status Code: {ret.status_code}")
            print()

        if ret.ok:
            apps = super().jsonifyResults(ret)
            appsCooked = copy.deepcopy(apps)
            """
            self.results = {"items":[
                    {
                        "type": "application/astra-app",
                        "version": "2.0",
                        "id": "36ba2699-66dc-4ad1-949b-26c1108f42e2",
                        "name": "wordpress-app",
                        "namespaceScopedResources": [
                            {
                                "namespace": "wordpress",
                                "labelSelectors": []
                            }
                        ],
                        "state": "ready",
                        "lastResourceCollectionTimestamp": "2022-07-20T18:19:35Z",
                        "stateTransitions": [
                            { "to": ["pending"] },
                            { "to": ["provisioning"] },
                            { "from": "pending", "to": ["discovering", "failed"] },
                            { "from": "discovering", "to": ["ready", "failed"] },
                            {
                                "from": "ready",
                                "to": [ "discovering", "restoring", "unavailable", "failed"]
                            },
                            { "from": "unavailable", "to": ["ready", "restoring"] },
                            { "from": "provisioning", "to": ["discovering", "failed"] },
                            { "from": "restoring", "to": ["discovering", "failed"] }
                        ],
                        "stateDetails": [],
                        "protectionState": "none",
                        "protectionStateDetails": [],
                        "namespaces": [
                            "wordpress"
                        ],
                        "clusterName": "uscentral1-cluster",
                        "clusterID": "b81bdd8f-c2c7-40eb-a602-4af06d3c6e4d",
                        "clusterType": "gke",
                        "metadata": {
                            "labels": [],
                            "creationTimestamp": "2022-07-20T18:19:30Z",
                            "modificationTimestamp": "2022-07-20T18:20:36Z",
                            "createdBy": "12a5d9dd-851e-4235-af27-86c0b63bf3a9"
                        }
                    }],
                "metadata":{}
            }
            """

            # Loop through all apps and delete those that don't match filters
            for counter, app in enumerate(apps.get("items")):

                # If there's a given filter, delete non-matching values
                if namespace:
                    delApp = True
                    for ns in app["namespaces"]:
                        if ns == namespace:
                            delApp = False
                    if delApp:
                        appsCooked["items"].remove(apps["items"][counter])
                elif cluster and cluster != app["clusterName"]:
                    appsCooked["items"].remove(apps["items"][counter])

            if self.output == "json":
                dataReturn = appsCooked
            elif self.output == "yaml":
                dataReturn = yaml.dump(appsCooked)
            elif self.output == "table":
                tabHeader = [
                    "appName",
                    "appID",
                    "clusterName",
                    "namespace",
                    "state",
                ]
                tabData = []
                for app in appsCooked.get("items"):
                    tabData.append(
                        [
                            app["name"],
                            app["id"],
                            app["clusterName"],
                            ", ".join(app["namespaces"]),
                            app["state"],
                        ]
                    )
                dataReturn = tabulate(tabData, tabHeader, tablefmt="grid")

            if not self.quiet:
                print(json.dumps(dataReturn) if type(dataReturn) is dict else dataReturn)
            return dataReturn

        else:
            if not self.quiet:
                print(f"API HTTP Status Code: {ret.status_code} - {ret.reason}")
                if ret.text.strip():
                    print(f"Error text: {ret.text}")
            return False


class getBackups(SDKCommon):
    """Iterate over every managed app, and list all of it's backups.
    Failure reporting is not implimented, failure to list backups for
    one (or more) of N many apps just results in an empty list of backups
    for that app.
    """

    def __init__(self, quiet=True, verbose=False, output="json"):
        """quiet: Will there be CLI output or just return (datastructure)
        verbose: Print all of the ReST call info: URL, Method, Headers, Request Body
        output: table: pretty print the data
                json: (default) output in JSON
                yaml: output in yaml"""
        self.quiet = quiet
        self.verbose = verbose
        self.output = output
        super().__init__()
        self.apps = getApps().main()

    def main(self, appFilter=None):
        if self.apps is False:
            print("Call to getApps().main() failed")
            return False

        """self.apps = {"items":[{"appDefnSource":"namespace","appLabels":[],
            "clusterID":"420a9ab0-1608-4e2e-a5ed-ca5b26a7fe69","clusterName":"useast1-cluster",
            "clusterType":"gke","collectionState":"fullyCollected","collectionStateDetails":[],
            "collectionStateTransitions":[{"from":"notCollected","to":["partiallyCollected",
            "fullyCollected"]},{"from":"partiallyCollected","to":["fullyCollected"]},
            {"from":"fullyCollected","to":[]}],"id":"d8cf2f17-d8d6-4b9f-aa42-f945d43b9a87",
            "managedState":"managed","managedStateUnready":[],
            "managedTimestamp":"2022-05-12T14:35:36Z","metadata":{"createdBy":"system",
            "creationTimestamp":"2022-05-12T14:35:27Z","labels":[],
            "modificationTimestamp":"2022-05-12T18:47:45Z"},"name":"wordpress-ns",
            "namespace":"wordpress-ns","protectionState":"protected","protectionStateUnready":[],
            "state":"running","stateUnready":[],"system":"false","type":"application/astra-app",
            "version":"1.1"}],"metadata":{}}
        """
        backups = {}
        backups["items"] = []
        if self.output == "table":
            globaltabHeader = ["AppID", "backupName", "backupID", "backupState"]
            globaltabData = []

        for app in self.apps["items"]:
            if appFilter:
                if app["name"] != appFilter and app["id"] != appFilter:
                    continue
            endpoint = f"k8s/v1/apps/{app['id']}/appBackups"
            url = self.base + endpoint

            data = {}
            params = {}

            if self.verbose:
                print(f"Listing Backups for {app['id']} {app['name']}")
                print(colored(f"API URL: {url}", "green"))
                print(colored("API Method: GET", "green"))
                print(colored(f"API Headers: {self.headers}", "green"))
                print(colored(f"API data: {data}", "green"))
                print(colored(f"API params: {params}", "green"))

            ret = super().apicall("get", url, data, self.headers, params, self.verifySSL)

            if self.verbose:
                print(f"API HTTP Status Code: {ret.status_code}")
                print()

            if ret.ok:
                results = super().jsonifyResults(ret)
                if results is None:
                    continue
                # Remember this is on a per AppID basis
                """results:
                     {'items':
                        [['hourly-rlezp-xsxmz',
                          '493c862d-71a9-4d47-87d3-eab9006c726f',
                          'completed', {'labels': [],
                                        'creationTimestamp': '2021-08-16T17:00:01Z',
                                        'modificationTimestamp': '2021-08-16T17:00:01Z',
                                        'createdBy': '70fa19ad-eb95-4d1c-b5fb-76b7f4214e6c'}]],
                                        'metadata': {}}
                """
                for item in results["items"]:
                    # Adding custom 'appID' key/value pair
                    if not item.get("appID"):
                        item["appID"] = app["id"]
                    backups["items"].append(item)
                if self.output == "table":
                    tabHeader = ["backupName", "backupID", "backupState"]
                    tabData = []
                    for backup in results["items"]:
                        tabData.append(
                            [
                                backup["name"],
                                backup["id"],
                                backup["state"],
                            ]
                        )
                        globaltabData.append(
                            [
                                app["id"],
                                backup["name"],
                                backup["id"],
                                backup["state"],
                            ]
                        )
                if not self.quiet and self.verbose:
                    print(f"Backups for {app['id']}")
                    if self.output == "json":
                        print(json.dumps(results))
                    elif self.output == "yaml":
                        print(yaml.dump(results))
                    elif self.output == "table":
                        print(tabulate(tabData, tabHeader, tablefmt="grid"))
                        print()
            else:
                continue
        if self.output == "json":
            dataReturn = backups
        elif self.output == "yaml":
            dataReturn = yaml.dump(backups)
        elif self.output == "table":
            dataReturn = tabulate(globaltabData, globaltabHeader, tablefmt="grid")

        if not self.quiet:
            print(json.dumps(dataReturn) if type(dataReturn) is dict else dataReturn)
        return dataReturn


class takeBackup(SDKCommon):
    """Take a backup of an app.  An AppID and backupName is provided and
    either the result JSON is returned or the backupID of the newly created
    backup is returned."""

    def __init__(self, quiet=True, verbose=False):
        """quiet: Will there be CLI output or just return (datastructure)
        verbose: Print all of the ReST call info: URL, Method, Headers, Request Body"""
        self.quiet = quiet
        self.verbose = verbose
        super().__init__()
        self.headers["accept"] = "application/astra-appBackup+json"
        self.headers["Content-Type"] = "application/astra-appBackup+json"

    def main(self, appID, backupName):

        endpoint = f"k8s/v1/apps/{appID}/appBackups"
        url = self.base + endpoint
        params = {}
        data = {
            "type": "application/astra-appBackup",
            "version": "1.1",
            "name": backupName,
        }

        if self.verbose:
            print(f"Taking backup for {appID}")
            print(colored(f"API URL: {url}", "green"))
            print(colored("API Method: POST", "green"))
            print(colored(f"API Headers: {self.headers}", "green"))
            print(colored(f"API data: {data}", "green"))
            print(colored(f"API params: {params}", "green"))

        ret = super().apicall("post", url, data, self.headers, params, self.verifySSL)

        if self.verbose:
            print(f"API HTTP Status Code: {ret.status_code}")
            print()

        if ret.ok:
            results = super().jsonifyResults(ret)
            if not self.quiet:
                print(json.dumps(results))
            else:
                return results.get("id") or True
        else:
            print(f"API HTTP Status Code: {ret.status_code} - {ret.reason}")
            if ret.text.strip():
                print(f"Error text: {ret.text}")
            return False


class destroyBackup(SDKCommon):
    """Given an appID and backupID destroy the backup.  Note that this doesn't
    unmanage a backup, it actively destroys it. There is no coming back from this."""

    def __init__(self, quiet=True, verbose=False):
        """quiet: Will there be CLI output or just return (datastructure)
        verbose: Print all of the ReST call info: URL, Method, Headers, Request Body"""
        self.quiet = quiet
        self.verbose = verbose
        super().__init__()
        self.headers["accept"] = "application/astra-appBackup+json"
        self.headers["Content-Type"] = "application/astra-appBackup+json"

    def main(self, appID, backupID):

        endpoint = f"k8s/v1/apps/{appID}/appBackups/{backupID}"
        url = self.base + endpoint
        params = {}
        data = {
            "type": "application/astra-appBackup",
            "version": "1.1",
        }

        if self.verbose:
            print(f"Deleting backup {backupID} for {appID}")
            print(colored(f"API URL: {url}", "green"))
            print(colored("API Method: DELETE", "green"))
            print(colored(f"API Headers: {self.headers}", "green"))
            print(colored(f"API data: {data}", "green"))
            print(colored(f"API params: {params}", "green"))

        ret = super().apicall("delete", url, data, self.headers, params, self.verifySSL)

        if self.verbose:
            print(f"API HTTP Status Code: {ret.status_code}")
            print()

        if ret.ok:
            return True
        else:
            if not self.quiet:
                print(f"API HTTP Status Code: {ret.status_code} - {ret.reason}")
                if ret.text.strip():
                    print(f"Error text: {ret.text}")
            return False


class cloneApp(SDKCommon):
    """Clone an app to a new app and namespace.

    Either backupID, snapshotID, or sourceAppID is required.

    The sourceClusterID is required as well.

    clusterID identifies the cluster for the new clone.  It's perfectly legal to
    clone an app to the same cluster it is running on; in which case clusterID ==
    sourceClusterID.

    This class doesn't try to validate anything you pass it, if you give it garbage
    for any parameters the clone operation will fail.
    """

    def __init__(self, quiet=True, verbose=False):
        """quiet: Will there be CLI output or just return (datastructure)
        verbose: Print all of the ReST call info: URL, Method, Headers, Request Body"""
        self.quiet = quiet
        self.verbose = verbose
        super().__init__()
        self.headers["accept"] = "application/astra-app+json"
        self.headers["Content-Type"] = "application/astra-app+json"

    def main(
        self,
        cloneName,
        clusterID,
        sourceClusterID,
        cloneNamespace=None,
        backupID=None,
        snapshotID=None,
        sourceAppID=None,
    ):
        assert backupID or snapshotID or sourceAppID

        endpoint = "k8s/v2/apps"
        url = self.base + endpoint
        params = {}
        data = {
            "type": "application/astra-app",
            "version": "2.0",
            "name": cloneName,
            "clusterID": clusterID,
            "sourceClusterID": sourceClusterID,
        }
        if sourceAppID:
            data["sourceAppID"] = sourceAppID
        if backupID:
            data["backupID"] = backupID
        if snapshotID:
            data["snapshotID"] = snapshotID
        if cloneNamespace:
            data["namespaceScopedResources"] = [{"namespace": cloneNamespace, "labelSelectors": []}]

        if self.verbose:
            print("Cloning app")
            print(colored(f"API URL: {url}", "green"))
            print(colored("API Method: POST", "green"))
            print(colored(f"API Headers: {self.headers}", "green"))
            print(colored(f"API data: {data}", "green"))
            print(colored(f"API params: {params}", "green"))

        ret = super().apicall("post", url, data, self.headers, params, self.verifySSL)

        if self.verbose:
            print(f"API HTTP Status Code: {ret.status_code}")
            print()

        if ret.ok:
            results = super().jsonifyResults(ret)

            if not self.quiet:
                print(json.dumps(results))
            else:
                return results
        else:
            if not self.quiet:
                print(f"API HTTP Status Code: {ret.status_code} - {ret.reason}")
                if ret.text.strip():
                    print(f"Error text: {ret.text}")
            return False


class restoreApp(SDKCommon):
    """Restore a backup or snapshot of an app.
    Must pass in an AppID and either a snapshotID or a backupID
    Note that this is a destructive operation that overwrites the current AppID
    with the backup/snapshot.

    Also note that the return code this class returns is referring to submitting
    the restore job.  To know if the restore job itself succeeds or fails you
    need to monitor the state of the app, watching for it to switch from
    "restoring" to "running" or "failed".
    """

    def __init__(self, quiet=True, verbose=False):
        """quiet: Will there be CLI output or just return True/False
        verbose: Print all of the ReST call info: URL, Method, Headers, Request Body"""
        self.quiet = quiet
        self.verbose = verbose
        super().__init__()
        self.headers["accept"] = "application/astra-app+json"
        self.headers["Content-Type"] = "application/astra-app+json"
        self.headers["ForceUpdate"] = "true"

    def main(
        self,
        appID,
        backupID=None,
        snapshotID=None,
    ):
        assert backupID or snapshotID

        endpoint = f"k8s/v2/apps/{appID}"
        url = self.base + endpoint
        params = {}
        data = {
            "type": "application/astra-app",
            "version": "2.0",
        }
        if backupID:
            data["backupID"] = backupID
        elif snapshotID:
            data["snapshotID"] = snapshotID

        if self.verbose:
            print("Restoring app")
            print(colored(f"API URL: {url}", "green"))
            print(colored("API Method: PUT", "green"))
            print(colored(f"API Headers: {self.headers}", "green"))
            print(colored(f"API data: {data}", "green"))
            print(colored(f"API params: {params}" % params, "green"))

        ret = super().apicall("put", url, data, self.headers, params, self.verifySSL)

        if self.verbose:
            print(f"API HTTP Status Code: {ret.status_code}")
            print()

        if ret.ok:
            return True
        else:
            if not self.quiet:
                print(f"API HTTP Status Code: {ret.status_code} - {ret.reason}")
                if ret.text.strip():
                    print(f"Error text: {ret.text}")
            return False


class getClusters(SDKCommon):
    """Iterate over the clouds and list the clusters in each."""

    def __init__(self, quiet=True, verbose=False, output="json"):
        """quiet: Will there be CLI output or just return (datastructure)
        verbose: Print all of the ReST call info: URL, Method, Headers, Request Body
        output: table: pretty print the data
                json: (default) output in JSON
                yaml: output in yaml"""
        self.quiet = quiet
        self.verbose = verbose
        self.output = output
        super().__init__()
        self.clouds = getClouds(quiet=True).main()

    def main(self, hideManaged=False, hideUnmanaged=False):
        clusters = {}
        clusters["items"] = []
        if self.clouds is False:
            print("Call to get clouds failed")
            return False
        if len(self.clouds["items"]) == 0:
            print("No clouds found")
            return True
        for cloud in self.clouds["items"]:
            endpoint = f"topology/v1/clouds/{cloud['id']}/clusters"
            url = self.base + endpoint
            data = {}
            params = {}

            if self.verbose:
                print(f"Getting clusters in cloud {cloud['id']} ({cloud['name']})...")
                print(colored(f"API URL: {url}", "green"))
                print(colored("API Method: GET", "green"))
                print(colored(f"API Headers: {self.headers}", "green"))
                print(colored(f"API data: {data}", "green"))
                print(colored(f"API params: {params}", "green"))

            ret = super().apicall("get", url, data, self.headers, params, self.verifySSL)

            if self.verbose:
                print(f"API HTTP Status Code: {ret.status_code}")
                print()

            if ret.ok:
                results = super().jsonifyResults(ret)
                for item in results["items"]:
                    if hideManaged:
                        if item.get("managedState") == "managed":
                            continue
                    if hideUnmanaged:
                        if item.get("managedState") == "unmanaged":
                            continue
                    clusters["items"].append(item)

        if self.output == "json":
            dataReturn = clusters
        elif self.output == "yaml":
            dataReturn = yaml.dump(clusters)
        elif self.output == "table":
            tabHeader = ["clusterName", "clusterID", "clusterType", "managedState"]
            tabData = []
            for cluster in clusters["items"]:
                tabData.append(
                    [
                        cluster["name"],
                        cluster["id"],
                        cluster["clusterType"],
                        cluster["managedState"],
                    ]
                )
            dataReturn = tabulate(tabData, tabHeader, tablefmt="grid")

        if not self.quiet:
            print(json.dumps(dataReturn) if type(dataReturn) is dict else dataReturn)
        return dataReturn


class createProtectionpolicy(SDKCommon):
    """Create a backup or snapshot policy on an appID.
    The rules of how dayOfWeek, dayOfMonth, hour, and minute
    need to be set vary based on whether granularity is set to
    hourly, daily, weekly, or monthly
    This class does no validation of the arguments, leaving that
    to the API call itself.  toolkit.py can be used as a guide as to
    what the API requirements are in case the swagger isn't sufficient.
    """

    def __init__(self, quiet=True, verbose=False):
        """quiet: Will there be CLI output or just return (datastructure)
        verbose: Print all of the ReST call info: URL, Method, Headers, Request Body"""
        self.quiet = quiet
        self.verbose = verbose
        super().__init__()
        self.headers["accept"] = "application/astra-schedule+json"
        self.headers["Content-Type"] = "application/astra-schedule+json"

    def main(
        self,
        granularity,
        backupRetention,
        snapshotRetention,
        dayOfWeek,
        dayOfMonth,
        hour,
        minute,
        appID,
    ):

        endpoint = f"k8s/v1/apps/{appID}/schedules"
        url = self.base + endpoint
        params = {}
        data = {
            "type": "application/astra-schedule",
            "version": "1.2",
            "backupRetention": backupRetention,
            "dayOfMonth": dayOfMonth,
            "dayOfWeek": dayOfWeek,
            "enabled": "true",
            "granularity": granularity,
            "hour": hour,
            "minute": minute,
            "name": f"{granularity} schedule",
            "snapshotRetention": snapshotRetention,
        }

        if self.verbose:
            print(f"Creating {granularity} protection policy for app: {appID}")
            print(colored(f"API URL: {url}", "green"))
            print(colored("API Method: POST", "green"))
            print(colored(f"API Headers: {self.headers}", "green"))
            print(colored(f"API data: {data}", "green"))
            print(colored(f"API params: {params}", "green"))

        ret = super().apicall("post", url, data, self.headers, params, self.verifySSL)

        if self.verbose:
            print(f"API HTTP Status Code: {ret.status_code}")
            print()

        if ret.ok:
            results = super().jsonifyResults(ret)
            if not self.quiet:
                print(json.dumps(results))
            return results
        else:
            if not self.quiet:
                print(f"API HTTP Status Code: {ret.status_code} - {ret.reason}")
                if ret.text.strip():
                    print(f"Error text: {ret.text}")
            return False


class manageApp(SDKCommon):
    """This class switches an unmanaged (aka undefined) app to a managed (aka defined) app."""

    def __init__(self, quiet=True, verbose=False):
        """quiet: Will there be CLI output or just return (datastructure)
        verbose: Print all of the ReST call info: URL, Method, Headers, Request Body"""
        self.quiet = quiet
        self.verbose = verbose
        super().__init__()
        self.headers["accept"] = "application/astra-app+json"
        self.headers["Content-Type"] = "application/astra-app+json"

    def main(self, appName, namespace, clusterID, label=None):

        endpoint = "k8s/v2/apps"
        url = self.base + endpoint
        params = {}
        data = {
            "clusterID": clusterID,
            "name": appName,
            "namespaceScopedResources": [{"namespace": namespace}],
            "type": "application/astra-app",
            "version": "2.0",
        }
        if label:
            data["namespaceScopedResources"][0]["labelSelectors"] = [label]

        if self.verbose:
            print(f"Managing app: {appName}")
            print(colored(f"API URL: {url}", "green"))
            print(colored("API Method: POST", "green"))
            print(colored(f"API Headers: {self.headers}", "green"))
            print(colored(f"API data: {data}", "green"))
            print(colored(f"API params: {params}", "green"))

        ret = super().apicall("post", url, data, self.headers, params, self.verifySSL, self.quiet)

        if self.verbose:
            print(f"API HTTP Status Code: {ret.status_code}")
            print()

        if ret.ok:
            results = super().jsonifyResults(ret)
            if not self.quiet:
                print(json.dumps(results))
            return results
        else:
            if not self.quiet:
                print(f"API HTTP Status Code: {ret.status_code} - {ret.reason}")
                if ret.text.strip():
                    print(f"Error text: {ret.text}")
            return False


class unmanageApp(SDKCommon):
    """This class switches a managed app to a discovered app."""

    def __init__(self, quiet=True, verbose=False):
        """quiet: Will there be CLI output or just return (datastructure)
        verbose: Print all of the ReST call info: URL, Method, Headers, Request Body"""
        self.quiet = quiet
        self.verbose = verbose
        super().__init__()
        self.headers["accept"] = "application/astra-app+json"
        self.headers["Content-Type"] = "application/astra-app+json"

    def main(self, appID):

        endpoint = f"k8s/v2/apps/{appID}"
        url = self.base + endpoint
        params = {}
        data = {}

        if self.verbose:
            print(f"unmanaging app: {appID}")
            print(colored(f"API URL: {url}", "green"))
            print(colored("API Method: DELETE", "green"))
            print(colored(f"API Headers: {self.headers}", "green"))
            print(colored(f"API data: {data}", "green"))
            print(colored(f"API params: {params}", "green"))

        ret = super().apicall("delete", url, data, self.headers, params, self.verifySSL)

        if self.verbose:
            print(f"API HTTP Status Code: {ret.status_code}")
            print()

        if ret.ok:
            if not self.quiet:
                print("App unmanaged")
            return True
        else:
            if not self.quiet:
                print(f"API HTTP Status Code: {ret.status_code} - {ret.reason}")
                if ret.text.strip():
                    print(f"Error text: {ret.text}")
            return False


class takeSnap(SDKCommon):
    """Take a snapshot of an app.  An AppID and snapName are required and
    either the result JSON is returned or the snapID of the newly created
    backup is returned."""

    def __init__(self, quiet=True, verbose=False):
        """quiet: Will there be CLI output or just return (datastructure)
        verbose: Print all of the ReST call info: URL, Method, Headers, Request Body"""
        self.quiet = quiet
        self.verbose = verbose
        super().__init__()
        self.headers["accept"] = "application/astra-appSnap+json"
        self.headers["Content-Type"] = "application/astra-appSnap+json"

    def main(self, appID, snapName):

        endpoint = f"k8s/v1/apps/{appID}/appSnaps"
        url = self.base + endpoint
        params = {}
        data = {
            "type": "application/astra-appSnap",
            "version": "1.1",
            "name": snapName,
        }

        if self.verbose:
            print(f"Taking snapshot for {appID}")
            print(colored(f"API URL: {url}", "green"))
            print(colored("API Method: POST", "green"))
            print(colored(f"API Headers: {self.headers}", "green"))
            print(colored(f"API data: {data}", "green"))
            print(colored(f"API params: {params}", "green"))

        ret = super().apicall("post", url, data, self.headers, params, self.verifySSL)

        if self.verbose:
            print(f"API HTTP Status Code: {ret.status_code}")
            print()

        if ret.ok:
            results = super().jsonifyResults(ret)
            if not self.quiet:
                print(json.dumps(results))
            else:
                return results.get("id") or True
        else:
            print(f"API HTTP Status Code: {ret.status_code} - {ret.reason}")
            if ret.text.strip():
                print(f"Error text: {ret.text}")
            return False


class getSnaps(SDKCommon):
    """Iterate over every managed app, and list all of it's snapshots.
    Failure reporting is not implimented, failure to list snapshots for
    one (or more) of N many apps just results in an empty list of snapshots
    for that app.
    """

    def __init__(self, quiet=True, verbose=False, output="json"):
        """quiet: Will there be CLI output or just return (datastructure)
        verbose: Print all of the ReST call info: URL, Method, Headers, Request Body
        output: table: pretty print the data
                json: (default) output in JSON
                yaml: output in yaml"""
        self.quiet = quiet
        self.verbose = verbose
        self.output = output
        super().__init__()
        self.apps = getApps().main()

    def main(self, appFilter=None):
        if self.apps is False:
            print("Call to getApps() failed")
            return False

        snaps = {}
        snaps["items"] = []
        if self.output == "table":
            globaltabHeader = ["appID", "snapshotName", "snapshotID", "snapshotState"]
            globaltabData = []

        for app in self.apps["items"]:
            if appFilter:
                if app["name"] != appFilter and app["id"] != appFilter:
                    continue
            endpoint = f"k8s/v1/apps/{app['id']}/appSnaps"
            url = self.base + endpoint

            data = {}
            params = {}

            if self.verbose:
                print(f"Listing Snapshots for {app['id']} {app['name']}")
                print(colored(f"API URL: {url}", "green"))
                print(colored("API Method: GET", "green"))
                print(colored(f"API Headers: {self.headers}", "green"))
                print(colored(f"API data: {data}", "green"))
                print(colored(f"API params: {params}", "green"))

            ret = super().apicall("get", url, data, self.headers, params, self.verifySSL)

            if self.verbose:
                print(f"API HTTP Status Code: {ret.status_code}")
                print()

            if ret.ok:
                results = super().jsonifyResults(ret)
                if results is None:
                    continue
                for item in results["items"]:
                    # Adding custom 'appID' key/value pair
                    if not item.get("appID"):
                        item["appID"] = app["id"]
                    snaps["items"].append(item)
                if self.output == "table":
                    tabHeader = ["snapshotName", "snapshotID", "snapshotState"]
                    tabData = []
                    for snap in results["items"]:
                        tabData.append(
                            [
                                snap["name"],
                                snap["id"],
                                snap["state"],
                            ]
                        )
                        globaltabData.append(
                            [
                                app["id"],
                                snap["name"],
                                snap["id"],
                                snap["state"],
                            ]
                        )
                if not self.quiet and self.verbose:
                    print(f"Snapshots for {app['id']}")
                    if self.output == "json":
                        print(json.dumps(results))
                    elif self.output == "yaml":
                        print(yaml.dump(results))
                    elif self.output == "table":
                        print(tabulate(tabData, tabHeader, tablefmt="grid"))
                        print()
            else:
                continue
        if self.output == "json":
            dataReturn = snaps
        elif self.output == "yaml":
            dataReturn = yaml.dump(snaps)
        elif self.output == "table":
            dataReturn = tabulate(globaltabData, globaltabHeader, tablefmt="grid")

        if not self.quiet:
            print(json.dumps(dataReturn) if type(dataReturn) is dict else dataReturn)
        return dataReturn


class destroySnapshot(SDKCommon):
    """Given an appID and snapID destroy the snapshot.  Note that this doesn't
    unmanage a snapshot, it actively destroys it. There is no coming back from this."""

    def __init__(self, quiet=True, verbose=False):
        """quiet: Will there be CLI output or just return (datastructure)
        verbose: Print all of the ReST call info: URL, Method, Headers, Request Body"""
        self.quiet = quiet
        self.verbose = verbose
        super().__init__()
        self.headers["accept"] = "application/astra-appSnap+json"
        self.headers["Content-Type"] = "application/astra-appSnap+json"

    def main(self, appID, snapID):

        endpoint = f"k8s/v1/apps/{appID}/appSnaps/{snapID}"
        url = self.base + endpoint
        params = {}
        data = {
            "type": "application/astra-appSnap",
            "version": "1.1",
        }

        if self.verbose:
            print(f"Deleting snapshot {snapID} for {appID}")
            print(colored(f"API URL: {url}", "green"))
            print(colored("API Method: DELETE", "green"))
            print(colored(f"API Headers: {self.headers}", "green"))
            print(colored(f"API data: {data}", "green"))
            print(colored(f"API params: {params}", "green"))

        ret = super().apicall("delete", url, data, self.headers, params, self.verifySSL)

        if self.verbose:
            print(f"API HTTP Status Code: {ret.status_code}")
            print()

        if ret.ok:
            return True
        else:
            if not self.quiet:
                print(f"API HTTP Status Code: {ret.status_code} - {ret.reason}")
                if ret.text.strip():
                    print(f"Error text: {ret.text}")
            return False


class getClouds(SDKCommon):
    def __init__(self, quiet=True, verbose=False, output="json"):
        """quiet: Will there be CLI output or just return (datastructure)
        verbose: Print all of the ReST call info: URL, Method, Headers, Request Body
        output: table: pretty print the data
                json: (default) output in JSON
                yaml: output in yaml"""
        self.quiet = quiet
        self.verbose = verbose
        self.output = output
        super().__init__()

    def main(self):

        endpoint = "topology/v1/clouds"
        url = self.base + endpoint

        data = {}
        params = {}

        if self.verbose:
            print("Getting clouds...")
            print(colored(f"API URL: {url}", "green"))
            print(colored("API Method: GET", "green"))
            print(colored(f"API Headers: {self.headers}", "green"))
            print(colored(f"API data: {data}", "green"))
            print(colored(f"API params: {params}", "green"))

        ret = super().apicall("get", url, data, self.headers, params, self.verifySSL)

        if self.verbose:
            print(f"API HTTP Status Code: {ret.status_code}")
            print()

        if ret.ok:
            results = super().jsonifyResults(ret)
            if self.output == "json":
                dataReturn = results
            elif self.output == "yaml":
                dataReturn = yaml.dump(results)
            elif self.output == "table":
                tabHeader = ["cloudName", "cloudID", "cloudType"]
                tabData = []
                for cloud in results["items"]:
                    tabData.append(
                        [
                            cloud["name"],
                            cloud["id"],
                            cloud["cloudType"],
                        ]
                    )
                dataReturn = tabulate(tabData, tabHeader, tablefmt="grid")
            if not self.quiet:
                print(json.dumps(dataReturn) if type(dataReturn) is dict else dataReturn)
            return dataReturn

        else:
            if not self.quiet:
                print(f"API HTTP Status Code: {ret.status_code} - {ret.reason}")
                if ret.text.strip():
                    print(f"Error text: {ret.text}")
            return False


class getStorageClasses(SDKCommon):
    def __init__(self, quiet=True, verbose=False, output="json"):
        """quiet: Will there be CLI output or just return (datastructure)
        verbose: Print all of the ReST call info: URL, Method, Headers, Request Body
        output: table: pretty print the data
                json: (default) output in JSON
                yaml: output in yaml"""
        self.quiet = quiet
        self.verbose = verbose
        self.output = output
        super().__init__()
        self.clouds = getClouds().main()
        self.clusters = getClusters().main()

    def main(self):
        if self.clouds is False:
            print("getClouds().main() failed")
            return False
        if self.clusters is False:
            print("getClusters().main() failed")
            return False
        if len(self.clouds["items"]) == 0:
            print("No clouds found")
            return True
        if len(self.clusters["items"]) == 0:
            print("No clusters found")
            return True

        storageClasses = {}
        storageClasses["items"] = []
        for cloud in self.clouds["items"]:
            for cluster in self.clusters["items"]:
                # exclude invalid combinations of cloud/cluster
                if cluster["cloudID"] != cloud["id"] or cluster["managedState"] == "ineligible":
                    continue
                endpoint = (
                    f"topology/v1/clouds/{cloud['id']}/clusters/{cluster['id']}/storageClasses"
                )
                url = self.base + endpoint

                data = {}
                params = {}

                if self.verbose:
                    print()
                    print(
                        f"Listing StorageClasses for cluster: {cluster['id']} in cloud: {cloud['id']}"
                    )
                    print()
                    print(colored(f"API URL: {url}", "green"))
                    print(colored("API Method: GET", "green"))
                    print(colored(f"API Headers: {self.headers}", "green"))
                    print(colored(f"API data: {data}", "green"))
                    print(colored(f"API params: {params}", "green"))
                    print()

                ret = super().apicall("get", url, data, self.headers, params, self.verifySSL)

                if self.verbose:
                    print(f"API HTTP Status Code: {ret.status_code}")
                    print()
                if ret.ok:
                    results = super().jsonifyResults(ret)
                    if results is None:
                        continue
                    for entry in results.get("items"):
                        # Adding three custom key/value pairs since the storageClasses API response
                        # doesn't contain cloud or cluster info
                        if not entry.get("cloudID"):
                            entry["cloudID"] = cloud["id"]
                        if not entry.get("cloudType"):
                            entry["cloudType"] = cloud["cloudType"]
                        if not entry.get("clusterID"):
                            entry["clusterID"] = cluster["id"]
                        if not entry.get("clusterName"):
                            entry["clusterName"] = cluster["name"]
                        storageClasses["items"].append(entry)

        if self.output == "json":
            dataReturn = storageClasses
        elif self.output == "yaml":
            dataReturn = yaml.dump(storageClasses)
        elif self.output == "table":
            tabData = []
            tabHeader = ["cloud", "cluster", "storageclassID", "storageclassName"]
            for storageClass in storageClasses["items"]:
                tabData.append(
                    [
                        storageClass["cloudType"],
                        storageClass["clusterName"],
                        storageClass["id"],
                        storageClass["name"],
                    ]
                )
            dataReturn = tabulate(tabData, tabHeader, tablefmt="grid")

        if not self.quiet:
            print(json.dumps(dataReturn) if type(dataReturn) is dict else dataReturn)
        return dataReturn


class manageCluster(SDKCommon):
    """This class switches an unmanaged cluster to a managed cluster"""

    def __init__(self, quiet=True, verbose=False):
        """quiet: Will there be CLI output or just return (datastructure)
        verbose: Print all of the ReST call info: URL, Method, Headers, Request Body"""
        self.quiet = quiet
        self.verbose = verbose
        super().__init__()
        self.headers["accept"] = "application/astra-managedCluster+json"
        self.headers["Content-Type"] = "application/managedCluster+json"

    def main(self, clusterID, storageClassID):

        endpoint = "topology/v1/managedClusters"
        url = self.base + endpoint
        params = {}
        data = {
            "defaultStorageClass": storageClassID,
            "id": clusterID,
            "type": "application/astra-managedCluster",
            "version": "1.0",
        }

        if self.verbose:
            print()
            print(f"Managing: {clusterID}")
            print()
            print(colored(f"API URL: {url}", "green"))
            print(colored("API Method: POST", "green"))
            print(colored(f"API Headers: {self.headers}", "green"))
            print(colored(f"API data: {data}", "green"))
            print(colored(f"API params: {params}", "green"))
            print()

        ret = super().apicall("post", url, data, self.headers, params, self.verifySSL)

        if self.verbose:
            print(f"API HTTP Status Code: {ret.status_code}")
            print()

        if ret.ok:
            results = super().jsonifyResults(ret)
            if not self.quiet:
                print(json.dumps(results))
            return results
        else:
            if not self.quiet:
                print(f"API HTTP Status Code: {ret.status_code} - {ret.reason}")
                if ret.text.strip():
                    print(f"Error text: {ret.text}")
            return False


class unmanageCluster(SDKCommon):
    """This class switches a managed cluster to an un managed cluster"""

    def __init__(self, quiet=True, verbose=False):
        """quiet: Will there be CLI output or just return (datastructure)
        verbose: Print all of the ReST call info: URL, Method, Headers, Request Body"""
        self.quiet = quiet
        self.verbose = verbose
        super().__init__()
        self.headers["accept"] = "application/astra-managedCluster+json"
        self.headers["Content-Type"] = "application/managedCluster+json"

    def main(self, clusterID):

        endpoint = f"topology/v1/managedClusters/{clusterID}"
        url = self.base + endpoint
        params = {}
        data = {}

        if self.verbose:
            print()
            print(f"Unmanaging: {clusterID}")
            print()
            print(colored(f"API URL: {url}", "green"))
            print(colored("API Method: DELETE", "green"))
            print(colored(f"API Headers: {self.headers}", "green"))
            print(colored(f"API data: {data}", "green"))
            print(colored(f"API params: {params}", "green"))
            print()

        ret = super().apicall("delete", url, data, self.headers, params, self.verifySSL)

        if self.verbose:
            print(f"API HTTP Status Code: {ret.status_code}")
            print()

        if ret.ok:
            if not self.quiet:
                print("Cluster unmanaged")
            return True
        else:
            if not self.quiet:
                print(f"API HTTP Status Code: {ret.status_code} - {ret.reason}")
                if ret.text.strip():
                    print(f"Error text: {ret.text}")
            return False


class getNamespaces(SDKCommon):
    def __init__(self, quiet=True, verbose=False, output="json"):
        """quiet: Will there be CLI output or just return (datastructure)
        verbose: Print all of the ReST call info: URL, Method, Headers, Request Body
        output: table: pretty print the data
                json: (default) output in JSON
                yaml: output in yaml"""
        self.quiet = quiet
        self.verbose = verbose
        self.output = output
        super().__init__()
        self.apps = getApps().main()
        self.clusters = getClusters().main()

    def main(self, clusterID=None, nameFilter=None, showRemoved=False, minuteFilter=False):
        if self.apps is False:
            print("Call to getApps().main() failed")
            return False

        if clusterID:
            endpoint = f"topology/v1/clusters/{clusterID}/namespaces"
        else:
            endpoint = "topology/v1/namespaces"
        url = self.base + endpoint

        data = {}
        params = {}

        if self.verbose:
            print("Getting namespaces...")
            print(colored(f"API URL: {url}", "green"))
            print(colored("API Method: GET", "green"))
            print(colored(f"API Headers: {self.headers}", "green"))
            print(colored(f"API data: {data}", "green"))
            print(colored(f"API params: {params}", "green"))

        ret = super().apicall("get", url, data, self.headers, params, self.verifySSL)

        if self.verbose:
            print(f"API HTTP Status Code: {ret.status_code}")
            print()

        if ret.ok:
            systemNS = ["kube-node-lease", "kube-public", "kube-system", "trident"]
            namespaces = super().jsonifyResults(ret)
            # Add in a custom key/value "associatedApps"
            for ns in namespaces["items"]:
                ns["associatedApps"] = []
                for app in self.apps["items"]:
                    if ns["clusterID"] == app["clusterID"]:
                        for nsr in app["namespaceScopedResources"]:
                            if ns["name"] == nsr["namespace"]:
                                ns["associatedApps"].append(app["name"])
            # Delete the unneeded namespaces based on filters
            namespacesCooked = copy.deepcopy(namespaces)
            clusterList = []
            for cluster in self.clusters["items"]:
                if cluster["managedState"] == "managed":
                    clusterList.append(cluster["id"])
            for counter, namespace in enumerate(namespaces.get("items")):
                if namespace.get("systemType") or namespace.get("name") in systemNS:
                    namespacesCooked["items"].remove(namespaces["items"][counter])
                elif nameFilter and nameFilter not in namespace.get("name"):
                    namespacesCooked["items"].remove(namespaces["items"][counter])
                elif not showRemoved and namespace.get("namespaceState") == "removed":
                    namespacesCooked["items"].remove(namespaces["items"][counter])
                elif namespace["clusterID"] not in clusterList:
                    namespacesCooked["items"].remove(namespaces["items"][counter])
                elif minuteFilter and (
                    datetime.utcnow()
                    - datetime.strptime(
                        namespace.get("metadata").get("creationTimestamp"), "%Y-%m-%dT%H:%M:%SZ"
                    )
                    > timedelta(minutes=minuteFilter)
                ):
                    namespacesCooked["items"].remove(namespaces["items"][counter])

            if self.output == "json":
                dataReturn = namespacesCooked
            elif self.output == "yaml":
                dataReturn = yaml.dump(namespacesCooked)
            elif self.output == "table":
                tabHeader = ["name", "namespaceID", "namespaceState", "associatedApps", "clusterID"]
                tabData = []
                for namespace in namespacesCooked["items"]:
                    tabData.append(
                        [
                            namespace["name"],
                            namespace["id"],
                            namespace["namespaceState"],
                            ", ".join(namespace["associatedApps"]),
                            namespace["clusterID"],
                        ]
                    )
                dataReturn = tabulate(tabData, tabHeader, tablefmt="grid")
            if not self.quiet:
                print(json.dumps(dataReturn) if type(dataReturn) is dict else dataReturn)
            return dataReturn

        else:
            if not self.quiet:
                print(f"API HTTP Status Code: {ret.status_code} - {ret.reason}")
                if ret.text.strip():
                    print(f"Error text: {ret.text}")
            return False


class getScripts(SDKCommon):
    """Get all the scripts (aka hook sources) for the Astra Control account"""

    def __init__(self, quiet=True, verbose=False, output="json"):
        """quiet: Will there be CLI output or just return (datastructure)
        verbose: Print all of the ReST call info: URL, Method, Headers, Request Body
        output: table: pretty print the data
                json: (default) output in JSON
                yaml: output in yaml"""
        self.quiet = quiet
        self.verbose = verbose
        self.output = output
        super().__init__()

    def main(self, scriptSourceName=None):

        endpoint = "core/v1/hookSources"
        url = self.base + endpoint

        data = {}
        params = {}

        if self.verbose:
            print("Getting scripts...")
            print(colored(f"API URL: {url}", "green"))
            print(colored("API Method: GET", "green"))
            print(colored(f"API Headers: {self.headers}", "green"))
            print(colored(f"API data: {data}", "green"))
            print(colored(f"API params: {params}", "green"))

        ret = super().apicall("get", url, data, self.headers, params, self.verifySSL)

        if self.verbose:
            print(f"API HTTP Status Code: {ret.status_code}")
            print()

        if ret.ok:
            scripts = super().jsonifyResults(ret)
            scriptsCooked = copy.deepcopy(scripts)
            if scriptSourceName:
                for counter, script in enumerate(scripts.get("items")):
                    if script.get("name") != scriptSourceName:
                        scriptsCooked["items"].remove(scripts["items"][counter])

            if self.output == "json":
                dataReturn = scriptsCooked
            elif self.output == "yaml":
                dataReturn = yaml.dump(scriptsCooked)
            elif self.output == "table":
                tabHeader = ["scriptName", "scriptID", "description"]
                tabData = []
                for script in scriptsCooked["items"]:
                    tabData.append(
                        [
                            script["name"],
                            script["id"],
                            script.get("description"),
                        ]
                    )
                dataReturn = tabulate(tabData, tabHeader, tablefmt="grid")
            if not self.quiet:
                print(json.dumps(dataReturn) if type(dataReturn) is dict else dataReturn)
            return dataReturn

        else:
            if not self.quiet:
                print(f"API HTTP Status Code: {ret.status_code} - {ret.reason}")
                if ret.text.strip():
                    print(f"Error text: {ret.text}")
            return False


class createScript(SDKCommon):
    """Create a script (aka hook source)"""

    def __init__(self, quiet=True, verbose=False):
        """quiet: Will there be CLI output or just return (datastructure)
        verbose: Print all of the ReST call info: URL, Method, Headers, Request Body"""
        self.quiet = quiet
        self.verbose = verbose
        super().__init__()
        self.headers["accept"] = "application/astra-hookSource+json"
        self.headers["Content-Type"] = "application/astra-hookSource+json"

    def main(
        self,
        name,
        source,
        description=None,
    ):

        endpoint = f"core/v1/hookSources"
        url = self.base + endpoint
        params = {}
        data = {
            "type": "application/astra-hookSource",
            "version": "1.0",
            "name": name,
            "source": source,
            "sourceType": "script",
        }
        if description:
            data["description"] = description

        if self.verbose:
            print(f"Creating script {name}")
            print(colored(f"API URL: {url}", "green"))
            print(colored("API Method: POST", "green"))
            print(colored(f"API Headers: {self.headers}", "green"))
            print(colored(f"API data: {data}", "green"))
            print(colored(f"API params: {params}", "green"))

        ret = super().apicall("post", url, data, self.headers, params, self.verifySSL)

        if self.verbose:
            print(f"API HTTP Status Code: {ret.status_code}")
            print()

        if ret.ok:
            results = super().jsonifyResults(ret)
            if not self.quiet:
                print(json.dumps(results))
            return results
        else:
            if not self.quiet:
                print(f"API HTTP Status Code: {ret.status_code} - {ret.reason}")
                if ret.text.strip():
                    print(f"Error text: {ret.text}")
            return False


class destroyScript(SDKCommon):
    """Given a scriptID destroy the script.  Note that this doesn't unmanage
    a script, it actively destroys it. There is no coming back from this."""

    def __init__(self, quiet=True, verbose=False):
        """quiet: Will there be CLI output or just return (datastructure)
        verbose: Print all of the ReST call info: URL, Method, Headers, Request Body"""
        self.quiet = quiet
        self.verbose = verbose
        super().__init__()
        self.headers["accept"] = "application/astra-hookSource+json"
        self.headers["Content-Type"] = "application/astra-hookSource+json"

    def main(self, scriptID):

        endpoint = f"core/v1/hookSources/{scriptID}"
        url = self.base + endpoint
        params = {}
        data = {
            "type": "application/astra-hookSource",
            "version": "1.0",
        }

        if self.verbose:
            print(f"Deleting scriptID {scriptID}")
            print(colored(f"API URL: {url}", "green"))
            print(colored("API Method: DELETE", "green"))
            print(colored(f"API Headers: {self.headers}", "green"))
            print(colored(f"API data: {data}", "green"))
            print(colored(f"API params: {params}", "green"))

        ret = super().apicall("delete", url, data, self.headers, params, self.verifySSL)

        if self.verbose:
            print(f"API HTTP Status Code: {ret.status_code}")
            print()

        if ret.ok:
            return True
        else:
            if not self.quiet:
                print(f"API HTTP Status Code: {ret.status_code} - {ret.reason}")
                if ret.text.strip():
                    print(f"Error text: {ret.text}")
            return False


class getAppAssets(SDKCommon):
    def __init__(self, quiet=True, verbose=False, output="json"):
        """quiet: Will there be CLI output or just return (datastructure)
        verbose: Print all of the ReST call info: URL, Method, Headers, Request Body
        output: table: pretty print the data
                json: (default) output in JSON
                yaml: output in yaml"""
        self.quiet = quiet
        self.verbose = verbose
        self.output = output
        super().__init__()

    def main(self, appID):

        endpoint = f"k8s/v1/apps/{appID}/appAssets"
        url = self.base + endpoint

        data = {}
        params = {}

        if self.verbose:
            print("Getting app assets...")
            print(colored(f"API URL: {url}", "green"))
            print(colored("API Method: GET", "green"))
            print(colored(f"API Headers: {self.headers}", "green"))
            print(colored(f"API data: {data}", "green"))
            print(colored(f"API params: {params}", "green"))

        ret = super().apicall("get", url, data, self.headers, params, self.verifySSL)

        if self.verbose:
            print(f"API HTTP Status Code: {ret.status_code}")
            print()

        if ret.ok:
            assets = super().jsonifyResults(ret)

            if self.output == "json":
                dataReturn = assets
            elif self.output == "yaml":
                dataReturn = yaml.dump(assets)
            elif self.output == "table":
                tabHeader = ["assetName", "assetType"]
                tabData = []
                for asset in assets["items"]:
                    tabData.append(
                        [
                            asset.get("assetName"),
                            asset.get("assetType"),
                        ]
                    )
                dataReturn = tabulate(tabData, tabHeader, tablefmt="grid")
            if not self.quiet:
                print(json.dumps(dataReturn) if type(dataReturn) is dict else dataReturn)
            return dataReturn

        else:
            if not self.quiet:
                print(f"API HTTP Status Code: {ret.status_code} - {ret.reason}")
                if ret.text.strip():
                    print(f"Error text: {ret.text}")
            return False


class getHooks(SDKCommon):
    """Get all the execution hooks for every app"""

    def __init__(self, quiet=True, verbose=False, output="json"):
        """quiet: Will there be CLI output or just return (datastructure)
        verbose: Print all of the ReST call info: URL, Method, Headers, Request Body
        output: table: pretty print the data
                json: (default) output in JSON
                yaml: output in yaml"""
        self.quiet = quiet
        self.verbose = verbose
        self.output = output
        super().__init__()
        self.apps = getApps().main()

    def main(self, appFilter=None):
        if self.apps is False:
            print("Call to getApps() failed")
            return False

        hooks = {}
        hooks["items"] = []
        if self.output == "table":
            globaltabHeader = ["appID", "hookName", "hookID", "matchingImages"]
            globaltabData = []

        for app in self.apps["items"]:
            if appFilter:
                if app["name"] != appFilter and app["id"] != appFilter:
                    continue
            endpoint = f"k8s/v1/apps/{app['id']}/executionHooks"
            url = self.base + endpoint

            data = {}
            params = {}

            if self.verbose:
                print("Getting execution hooks...")
                print(colored(f"API URL: {url}", "green"))
                print(colored("API Method: GET", "green"))
                print(colored(f"API Headers: {self.headers}", "green"))
                print(colored(f"API data: {data}", "green"))
                print(colored(f"API params: {params}", "green"))

            ret = super().apicall("get", url, data, self.headers, params, self.verifySSL)

            if self.verbose:
                print(f"API HTTP Status Code: {ret.status_code}")
                print()

            if ret.ok:
                results = super().jsonifyResults(ret)
                if results is None:
                    continue
                for item in results["items"]:
                    hooks["items"].append(item)
                if self.output == "table":
                    tabHeader = ["hookName", "hookID", "matchingImages"]
                    tabData = []
                    for hook in results["items"]:
                        tabData.append(
                            [
                                hook["name"],
                                hook["id"],
                                ", ".join(hook["matchingImages"]),
                            ]
                        )
                        globaltabData.append(
                            [
                                app["id"],
                                hook["name"],
                                hook["id"],
                                ", ".join(hook["matchingImages"]),
                            ]
                        )
                if not self.quiet and self.verbose:
                    print(f"Execution hooks for {app['id']}")
                    if self.output == "json":
                        print(json.dumps(results))
                    elif self.output == "yaml":
                        print(yaml.dump(results))
                    elif self.output == "table":
                        print(tabulate(tabData, tabHeader, tablefmt="grid"))
                        print()
            else:
                if not self.quiet:
                    print(f"API HTTP Status Code: {ret.status_code} - {ret.reason}")
                    if ret.text.strip():
                        print(f"Error text: {ret.text}")
                continue
        if self.output == "json":
            dataReturn = hooks
        elif self.output == "yaml":
            dataReturn = yaml.dump(hooks)
        elif self.output == "table":
            dataReturn = tabulate(globaltabData, globaltabHeader, tablefmt="grid")

        if not self.quiet:
            print(json.dumps(dataReturn) if type(dataReturn) is dict else dataReturn)
        return dataReturn


class createHook(SDKCommon):
    """Create an execution hook"""

    def __init__(self, quiet=True, verbose=False):
        """quiet: Will there be CLI output or just return (datastructure)
        verbose: Print all of the ReST call info: URL, Method, Headers, Request Body"""
        self.quiet = quiet
        self.verbose = verbose
        super().__init__()
        self.headers["accept"] = "application/astra-executionHook+json"
        self.headers["Content-Type"] = "application/astra-executionHook+json"

    def main(
        self,
        appID,
        name,
        scriptID,
        stage,
        action,
        arguments,
        containerRegex=None,
        description=None,
    ):

        # endpoint = f"k8s/v1/apps/{appID}/executionHooks"
        endpoint = f"core/v1/executionHooks"
        url = self.base + endpoint
        params = {}
        data = {
            "type": "application/astra-executionHook",
            "version": "1.0",
            "name": name,
            "hookType": "custom",
            "action": action,
            "stage": stage,
            "hookSourceID": scriptID,
            "arguments": arguments,
            "appID": appID,
            "enabled": "true",
        }
        if description:
            data["description"] = description
        if containerRegex:
            data["matchingCriteria"] = [{"type": "containerImage", "value": containerRegex}]

        if self.verbose:
            print(f"Creating executionHook {name}")
            print(colored(f"API URL: {url}", "green"))
            print(colored("API Method: POST", "green"))
            print(colored(f"API Headers: {self.headers}", "green"))
            print(colored(f"API data: {data}", "green"))
            print(colored(f"API params: {params}", "green"))

        ret = super().apicall("post", url, data, self.headers, params, self.verifySSL)

        if self.verbose:
            print(f"API HTTP Status Code: {ret.status_code}")
            print()

        if ret.ok:
            results = super().jsonifyResults(ret)
            if not self.quiet:
                print(json.dumps(results))
            return results
        else:
            if not self.quiet:
                print(f"API HTTP Status Code: {ret.status_code} - {ret.reason}")
                if ret.text.strip():
                    print(f"Error text: {ret.text}")
            return False


class destroyHook(SDKCommon):
    """Given an appID and hookID destroy the hook.  Note that this doesn't unmanage
    a hook, it actively destroys it. There is no coming back from this."""

    def __init__(self, quiet=True, verbose=False):
        """quiet: Will there be CLI output or just return (datastructure)
        verbose: Print all of the ReST call info: URL, Method, Headers, Request Body"""
        self.quiet = quiet
        self.verbose = verbose
        super().__init__()
        self.headers["accept"] = "application/astra-executionHook+json"
        self.headers["Content-Type"] = "application/astra-executionHook+json"

    def main(self, appID, hookID):

        # endpoint = f"k8s/v1/apps/{appID}/executionHooks/{hookID}"
        endpoint = f"core/v1/executionHooks/{hookID}"
        url = self.base + endpoint
        params = {}
        data = {
            "type": "application/astra-hookSource",
            "version": "1.0",
            "appID": appID,  # Not strictly required at this time
        }

        if self.verbose:
            print(f"Deleting hookID {hookID}")
            print(colored(f"API URL: {url}", "green"))
            print(colored("API Method: DELETE", "green"))
            print(colored(f"API Headers: {self.headers}", "green"))
            print(colored(f"API data: {data}", "green"))
            print(colored(f"API params: {params}", "green"))

        ret = super().apicall("delete", url, data, self.headers, params, self.verifySSL)

        if self.verbose:
            print(f"API HTTP Status Code: {ret.status_code}")
            print()

        if ret.ok:
            return True
        else:
            if not self.quiet:
                print(f"API HTTP Status Code: {ret.status_code} - {ret.reason}")
                if ret.text.strip():
                    print(f"Error text: {ret.text}")
            return False
