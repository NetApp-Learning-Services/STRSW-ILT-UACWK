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

try:
    from . import astraSDK
except ImportError:
    import astraSDK


import argparse
import dns.resolver
import json
import os
import subprocess
import sys
import tempfile
import time
import yaml
import kubernetes
import base64
from datetime import datetime, timedelta


def subKeys(subObject, key):
    """Short recursion function for when the userSelect dict object has another
    dict as one of its key's values"""
    subKey = key.split("/", maxsplit=1)
    if len(subKey) == 1:
        return subObject[subKey[0]]
    else:
        return subKeys(subObject[subKey[0]], subKey[1])


def userSelect(pickList, keys):
    """pickList is a dictionary with an 'items' array of dicts.  Print the values
    that match the 'keys' array, have the user pick one and then return the value
    of index 0 of the keys array"""
    # pickList = {"items": [{"id": "123", "name": "webapp",  "state": "running"},
    #                       {"id": "345", "name": "mongodb", "state": "stopped"}]}
    # keys = ["id", "name"]
    # Output:
    # 1:    123         webapp
    # 2:    345         mongodb
    # User enters 2, "id" (index 0) is returned, so "345"

    if not isinstance(pickList, dict) or not isinstance(keys, list):
        return False

    for counter, item in enumerate(pickList["items"], start=1):
        outputStr = str(counter) + ":\t"
        for key in keys:
            if item.get(key):
                outputStr += str(item[key]) + "\t"
            elif "/" in key:
                outputStr += subKeys(item, key) + "\t"
        print(outputStr)

    while True:
        ret = input(f"Select a line (1-{counter}): ")
        try:
            # try/except catches errors thrown from non-valid input
            objectValue = pickList["items"][int(ret) - 1][keys[0]]
            if int(ret) > 0 and int(ret) <= counter and objectValue:
                return objectValue
            else:
                continue
        except (IndexError, TypeError, ValueError):
            continue


def createHelmStr(flagName, values):
    """Create a string to be appended to a helm command which contains a list
    of --set {value} and/or --values {file} arguments"""
    returnStr = ""
    if values:
        for value in values:
            if type(value) == list:
                for v in value:
                    returnStr += f" --{flagName} {v}"
            else:
                returnStr += f" --{flagName} {value}"
    return returnStr


def createHookList(hookArguments):
    """Create a list of strings to be used for --hookArguments, as nargs="*" can provide
    a variety of different types of lists of lists depending on how the user ueses it.
    User Input                    argParse Value                      createHookList Return
    ----------                    --------------                      ---------------------
    -a arg1                       [['arg1']]                          ['arg1']
    -a arg1 arg2                  [['arg1', 'arg2']]                  ['arg1', 'arg2']
    -a arg1 -a arg2               [['arg1'], ['arg2']]                ['arg1', 'arg2']
    -a "arg1 s_arg" arg2          [['arg1 s_arg', 'arg2']]            ['arg1 s_arg', 'arg2']
    -a "arg1 s_arg" arg2 -a arg3  [['arg1 s_arg', 'arg2'], ['arg3']]  ['arg1 s_arg', 'arg2', 'arg3']
    """
    returnList = []
    if hookArguments:
        for arg in hookArguments:
            if type(arg) == list:
                for a in arg:
                    returnList.append(a)
            else:
                returnList.append(arg)
    return returnList


def updateHelm():
    """Check to see if the bitnami helm repo is installed
    If it is, get the name of the repo
    otherwise install it
    ignore_errors=True here because helm repo list returns 1 if there are no
    repos configured"""
    ret = run("helm repo list -o yaml", captureOutput=True, ignoreErrors=True)
    repos = {
        "https://charts.gitlab.io": None,
        "https://charts.bitnami.com/bitnami": None,
        "https://charts.cloudbees.com/public/cloudbees": None,
    }
    if ret != 1:
        retYaml = yaml.load(ret, Loader=yaml.SafeLoader)
        # Adding support for user-defined repos
        for item in retYaml:
            if item.get("url") not in repos:
                repos[item.get("url")] = None
        for repoUrlToMatch in repos:
            for item in retYaml:
                if item.get("url") == repoUrlToMatch:
                    repos[repoUrlToMatch] = item.get("name")
    for k, v in repos.items():
        if not v:
            repoName = k.split(".")[1]
            run(f"helm repo add {repoName} {k}")
            repos[k] = repoName

    run("helm repo update")
    chartsDict = {}
    chartsDict["items"] = []
    for val in repos.values():
        charts = run(f"helm -o json search repo {val}", captureOutput=True)
        for chart in json.loads(charts.decode("utf-8")):
            chartsDict["items"].append(chart)
    return chartsDict


def run(command, captureOutput=False, ignoreErrors=False):
    """Run an arbitrary shell command.  Our API is terrible.  If ignore_errors=False
    raise the SystemExit exception if the commands returns != 0 (e.g.: failure)
    If ignore_errors=True, return the shell return code if it is != 0
    If the shell return code is 0 (success) either return True or the contents of stdout, depending
    on whether capture_output is set to True or False"""
    command = command.split(" ")
    try:
        ret = subprocess.run(command, capture_output=captureOutput)
    except OSError as e:
        raise SystemExit(f"{command} OSError: {e}")
    # Shell returns 0 for success, a positive int for an error
    # inverted from python True/False
    if ret.returncode:
        if ignoreErrors:
            return ret.returncode
        else:
            raise SystemExit(f"{command} returned failure: {ret.returncode}")
    else:
        if captureOutput:
            return ret.stdout
        else:
            return True


def doProtectionTask(protectionType, appID, name, background):
    """Take a snapshot/backup of appID giving it name <name>
    Return the snapshotID/backupID of the backup taken or False if the protection task fails"""
    if protectionType == "backup":
        protectionID = astraSDK.takeBackup().main(appID, name)
    elif protectionType == "snapshot":
        protectionID = astraSDK.takeSnap().main(appID, name)
    if protectionID == False:
        sys.exit(1)

    print(f"Starting {protectionType} of {appID}")
    if background:
        print(
            f"Background {protectionType} flag selected, run 'list {protectionType}s' to get status"
        )
        return True

    print(f"Waiting for {protectionType} to complete.", end="")
    sys.stdout.flush()
    while True:
        if protectionType == "backup":
            objects = astraSDK.getBackups().main()
        elif protectionType == "snapshot":
            objects = astraSDK.getSnaps().main()
        if not objects:
            # This isn't technically true.  Trying to list the backups/snapshots after taking the
            # protection job failed.  The protection job itself may eventually succeed.
            print(f"Taking {protectionType} failed")
            return False
        for obj in objects["items"]:
            # There's no API for monitoring long running tasks.  Just because
            # the API call to create a backup/snapshot succeeded, that doesn't mean the
            # actual backup will succeed as well.  So we spin on checking the backups/snapshots
            # waiting for our backupsnapshot to either show completed or failed.
            if obj["id"] == protectionID:
                if obj["state"] == "completed":
                    print("complete!")
                    sys.stdout.flush()
                    return protectionID
                elif obj["state"] == "failed":
                    print(f"{protectionType} job failed")
                    return False
        time.sleep(5)
        print(".", end="")
        sys.stdout.flush()


def stsPatch(patch, stsName):
    """Patch and restart a statefulset"""
    patchYaml = yaml.dump(patch)
    tmp = tempfile.NamedTemporaryFile()
    tmp.write(bytes(patchYaml, "utf-8"))
    tmp.seek(0)
    # Use os.system a few times because the home rolled run() simply isn't up to the task
    try:
        # TODO: I suspect these gymnastics wouldn't be needed if the py-k8s module
        # were used
        ret = os.system(f'kubectl patch statefulset.apps/{stsName} -p "$(cat {tmp.name})"')
    except OSError as e:
        print(f"Exception: {e}")
        sys.exit(11)
    if ret:
        print(f"os.system exited with RC: {ret}")
        sys.exit(12)
    tmp.close()
    try:
        os.system(
            f"kubectl scale sts {stsName} --replicas=0 && "
            f"sleep 10 && kubectl scale sts {stsName} --replicas=1"
        )
    except OSError as e:
        print(f"Exception: {e}")
        sys.exit(13)
    if ret:
        print(f"os.system exited with RC: {ret}")
        sys.exit(14)


class toolkit:
    def __init__(self):
        self.conf = astraSDK.getConfig().main()

    def deploy(self, chart, appName, namespace, setValues, fileValues, verbose):
        """Deploy a helm chart <chart>, naming the app <appName> into <namespace>"""

        setStr = createHelmStr("set", setValues)
        valueStr = createHelmStr("values", fileValues)

        nsObj = astraSDK.getNamespaces(verbose=verbose)
        retval = run("kubectl get ns -o json", captureOutput=True)
        retvalJSON = json.loads(retval)
        for item in retvalJSON["items"]:
            if item["metadata"]["name"] == namespace:
                print(f"Namespace {namespace} already exists!")
                sys.exit(24)
        run(f"kubectl create namespace {namespace}")
        run(f"kubectl config set-context --current --namespace={namespace}")
        """if chartName == "gitlab":
            gitalyStorageClass = None
            # Are we running on GKE?
            # If we are running on GKE and installing gitlab, we'll use google persistant disk
            # for the gitaly PV
            # We can't use run() here as it splits args incorrectly
            command = [
                "kubectl",
                "run",
                "curl",
                "--rm",
                "--restart=Never",
                "-it",
                "--image=appropriate/curl",
                "--",
                "-H",
                "Metadata-Flavor: Google",
                "http://metadata.google.internal/"
                "computeMetadata/v1/instance/attributes/cluster-name",
            ]
            try:
                ret = subprocess.run(command, capture_output=True)
            except OSError:
                gitalyStorageClass = False
            if gitalyStorageClass is not False and not ret.returncode:
                # Shell command returned 0 RC (success)
                # ret.stdout = b'cluster-1-jppod "curl" deleted\n'
                # If this is GKE the first part of the returned value will
                # be the cluster name
                # TODO: Fragile, replace this whole bit with something robust
                retString = ret.stdout.decode("utf-8").strip()
                if 'pod "curl" deleted' in retString:
                    kubeHost = retString.split('pod "curl" deleted')[0]
                    clusters = astraSDK.getClusters().main()
                    for cluster in clusters:
                        if clusters[cluster][0] == kubeHost and clusters[cluster][1] == "gke":
                            gitalyStorageClass = "standard-rwo"

            myResolver = dns.resolver.Resolver()
            myResolver.nameservers = ["8.8.8.8"]
            try:
                answer = myResolver.resolve(f"gitlab.{domain}")
            except dns.resolver.NXDOMAIN as e:
                print(f"Can't resolve gitlab.{domain}: {e}")
                sys.exit(17)
            for i in answer:
                ip = i
            if ssl:
                glhelmCmd = (
                    f"helm install {appName} {repoName}/{chartName} --timeout 600s "
                    f"--set certmanager-issuer.email={email} "
                    f"--set global.hosts.domain={domain} "
                    "--set prometheus.alertmanager.persistentVolume.enabled=false "
                    "--set prometheus.server.persistentVolume.enabled=false "
                    f"--set global.hosts.externalIP={ip} "
                )
            else:
                glhelmCmd = (
                    f"helm install {appName} {repoName}/{chartName} --timeout 600s "
                    f"--set certmanager-issuer.email={email} "
                    f"--set global.hosts.domain={domain} "
                    "--set prometheus.alertmanager.persistentVolume.enabled=false "
                    "--set prometheus.server.persistentVolume.enabled=false "
                    f"--set global.hosts.externalIP={ip} "
                    "--set certmanager.install=false "
                    "--set global.ingress.configureCertmanager=false "
                    "--set gitlab-runner.install=false "
                )
            if gitalyStorageClass:
                glhelmCmd += f"--set gitlab.gitaly.persistence.storageClass={gitalyStorageClass}"
            run(glhelmCmd)

            # I could've included straight up YAML here but that seemed..the opposite of elegent.
            gitalyPatch = {
                "kind": "StatefulSet",
                "spec": {
                    "template": {
                        "spec": {
                            "containers": [
                                {
                                    "name": "gitaly",
                                    "securityContext": {"runAsUser": 1000},
                                }
                            ],
                            "initContainers": [
                                {
                                    "name": "init-chown",
                                    "image": "alpine",
                                    "securityContext": {"runAsUser": 0},
                                    "env": [
                                        {
                                            "name": "REPOS_HOME",
                                            "value": "/home/git/repositories",
                                        },
                                        {"name": "MARKER", "value": ".cplt2-5503"},
                                        {"name": "UID", "value": "1000"},
                                    ],
                                    "command": [
                                        "sh",
                                        "-c",
                                        "if [ ! -f $REPOS_HOME/$MARKER ]; "
                                        "then chown $UID:$UID -R $REPOS_HOME; "
                                        "touch $REPOS_HOME/$MARKER; "
                                        "chown $UID:$UID $REPOS_HOME/$MARKER; fi",
                                    ],
                                    "volumeMounts": [
                                        {
                                            "mountPath": "/home/git/repositories",
                                            "name": "repo-data",
                                        }
                                    ],
                                }
                            ],
                        }
                    }
                },
            }
            stsPatch(gitalyPatch, f"{appName}-gitaly")

        else:"""
        run(f"helm install {appName} {chart}{setStr}{valueStr}")
        print("Waiting for Astra to discover the namespace.", end="")
        sys.stdout.flush()

        appID = ""
        while not appID:
            # It takes Astra some time to realize new apps have been installed
            time.sleep(3)
            print(".", end="")
            sys.stdout.flush()
            namespaces = nsObj.main()
            # Cycle through the apps and see if one matches our new namespace
            for ns in namespaces["items"]:
                # Check to make sure our namespace name matches, it's in a discovered state,
                # and that it's a recently created namespace (less than 10 minutes old)
                if (
                    ns["name"] == namespace
                    and ns["namespaceState"] == "discovered"
                    and (
                        datetime.utcnow()
                        - datetime.strptime(
                            ns["metadata"]["creationTimestamp"], "%Y-%m-%dT%H:%M:%SZ"
                        )
                    )
                    < timedelta(minutes=10)
                ):
                    print(" Namespace discovered!")
                    sys.stdout.flush()
                    time.sleep(3)
                    print(f"Managing app: {ns['name']}.", end="")
                    sys.stdout.flush()
                    rc = astraSDK.manageApp(verbose=verbose).main(
                        ns["name"], ns["name"], ns["clusterID"]
                    )
                    appID = rc["id"]
                    print(" Success!")
                    sys.stdout.flush()
                    break

        # Create a protection policy on that namespace (using its appID)
        backupRetention = "1"
        snapshotRetention = "1"
        minute = "0"
        cpp = astraSDK.createProtectionpolicy(quiet=True)
        cppData = {
            "hourly": {"dayOfWeek": "*", "dayOfMonth": "*", "hour": "*"},
            "daily": {"dayOfWeek": "*", "dayOfMonth": "*", "hour": "2"},
            "weekly": {"dayOfWeek": "0", "dayOfMonth": "*", "hour": "2"},
            "monthly": {"dayOfWeek": "*", "dayOfMonth": "1", "hour": "2"},
        }
        for period in cppData:
            print(f"Setting {period} protection policy on {appID}")
            dayOfWeek = cppData[period]["dayOfWeek"]
            dayOfMonth = cppData[period]["dayOfMonth"]
            hour = cppData[period]["hour"]
            cppRet = cpp.main(
                period,
                snapshotRetention,
                backupRetention,
                dayOfWeek,
                dayOfMonth,
                hour,
                minute,
                appID,
            )
            if cppRet is False:
                raise SystemExit(f"cpp.main({period}...) returned False")

    def clone(
        self,
        cloneAppName,
        clusterID,
        sourceClusterID,
        appIDstr,
        cloneNamespace,
        backupID,
        snapshotID,
        sourceAppID,
        background,
        verbose,
    ):
        """Create a clone."""
        # Check to see if cluster-level resources are needed to be manually created
        needsIngressclass = False
        appAssets = astraSDK.getAppAssets(verbose=verbose).main(appIDstr)
        for asset in appAssets["items"]:
            if asset["assetName"] == "cjoc" and asset["assetType"] == "Ingress":
                needsIngressclass = True
        # Clone 'ingressclass' cluster object
        if needsIngressclass and sourceClusterID != clusterID:
            if not cloneNamespace:
                cloneNamespace = cloneAppName
            clusters = astraSDK.getClusters().main(hideUnmanaged=True)
            contexts, _ = kubernetes.config.list_kube_config_contexts()
            # Loop through clusters and contexts, find matches and open api_client
            for cluster in clusters["items"]:
                for context in contexts:
                    if cluster["id"] == clusterID:
                        if cluster["name"] in context["name"]:
                            destClient = kubernetes.client.NetworkingV1Api(
                                api_client=kubernetes.config.new_client_from_config(
                                    context=context["name"]
                                )
                            )
                    elif cluster["id"] == sourceClusterID:
                        if cluster["name"] in context["name"]:
                            sourceClient = kubernetes.client.NetworkingV1Api(
                                api_client=kubernetes.config.new_client_from_config(
                                    context=context["name"]
                                )
                            )
            try:
                # Get the source cluster ingressclass and apply it to the dest cluster
                sourceResp = sourceClient.read_ingress_class(
                    "nginx", _preload_content=False, _request_timeout=5
                )
                sourceIngress = json.loads(sourceResp.data)
                del sourceIngress["metadata"]["resourceVersion"]
                del sourceIngress["metadata"]["creationTimestamp"]
                sourceIngress["metadata"]["labels"]["app.kubernetes.io/instance"] = cloneNamespace
                sourceIngress["metadata"]["annotations"][
                    "meta.helm.sh/release-name"
                ] = cloneNamespace
                sourceIngress["metadata"]["annotations"][
                    "meta.helm.sh/release-namespace"
                ] = cloneNamespace
            except:
                # In the event the sourceCluster no longer exists or isn't in kubeconfig
                sourceIngress = {
                    "kind": "IngressClass",
                    "apiVersion": "networking.k8s.io/v1",
                    "metadata": {
                        "name": "nginx",
                        "generation": 1,
                        "labels": {
                            "app.kubernetes.io/component": "controller",
                            "app.kubernetes.io/instance": cloneNamespace,
                            "app.kubernetes.io/managed-by": "Helm",
                            "app.kubernetes.io/name": "ingress-nginx",
                            "app.kubernetes.io/version": "1.1.0",
                            "helm.sh/chart": "ingress-nginx-4.0.13",
                        },
                        "annotations": {
                            "meta.helm.sh/release-name": cloneNamespace,
                            "meta.helm.sh/release-namespace": cloneNamespace,
                        },
                        "managedFields": [
                            {
                                "manager": "helm",
                                "operation": "Update",
                                "apiVersion": "networking.k8s.io/v1",
                                "fieldsType": "FieldsV1",
                                "fieldsV1": {
                                    "f:metadata": {
                                        "f:annotations": {
                                            ".": {},
                                            "f:meta.helm.sh/release-name": {},
                                            "f:meta.helm.sh/release-namespace": {},
                                        },
                                        "f:labels": {
                                            ".": {},
                                            "f:app.kubernetes.io/component": {},
                                            "f:app.kubernetes.io/instance": {},
                                            "f:app.kubernetes.io/managed-by": {},
                                            "f:app.kubernetes.io/name": {},
                                            "f:app.kubernetes.io/version": {},
                                            "f:helm.sh/chart": {},
                                        },
                                    },
                                    "f:spec": {"f:controller": {}},
                                },
                            }
                        ],
                    },
                    "spec": {"controller": "k8s.io/ingress-nginx"},
                }
            try:
                # Add the ingressclass to the new cluster
                destClient.create_ingress_class(sourceIngress, _request_timeout=10)
            except NameError:
                raise SystemExit(f"Error: {clusterID} not found in kubeconfig")
            except kubernetes.client.rest.ApiException as e:
                # If the failure is due to the resource already existing, then we're all set,
                # otherwise it's more serious and we must raise an exception
                body = json.loads(e.body)
                if not (body.get("reason") == "AlreadyExists"):
                    raise SystemExit(f"Error: Kubernetes resource creation failed\n{e}")

        cloneRet = astraSDK.cloneApp(verbose=verbose).main(
            cloneAppName,
            clusterID,
            sourceClusterID,
            cloneNamespace=cloneNamespace,
            backupID=backupID,
            snapshotID=snapshotID,
            sourceAppID=sourceAppID,
        )
        if cloneRet:
            print("Submitting clone succeeded.")
            if background:
                print(f"Background clone flag selected, run 'list apps' to get status.")
                return True
            print("Waiting for clone to become available.", end="")
            sys.stdout.flush()
            appID = cloneRet.get("id")
            state = cloneRet.get("state")
            while state != "ready":
                apps = astraSDK.getApps().main()
                for app in apps["items"]:
                    if app["id"] == appID:
                        if app["state"] == "ready":
                            state = app["state"]
                            print("Cloning operation complete.")
                            sys.stdout.flush()
                        else:
                            print(".", end="")
                            sys.stdout.flush()
                            time.sleep(3)
        else:
            print("Submitting clone failed.")


def main():
    # This is a pretty big hack.  The various functions to populate the lists
    # used for choices() in the options are expensive.  argparse provides no
    # way to know what subcommand was selected prior to parsing the options.
    # By then it's too late to decide which functions to run to populate
    # the various choices the differing options for each subcommand needs.
    # So we just go around argparse's back and introspect sys.argv directly
    appList = []
    backupList = []
    chartsList = []
    clusterList = []
    destclusterList = []
    hookList = []
    namespaceList = []
    scriptList = []
    snapshotList = []
    storageClassList = []

    if len(sys.argv) > 1:

        # verbs must manually be kept in sync with the top level subcommands in the argparse
        # section of this code.
        verbs = {
            "deploy": False,
            "clone": False,
            "restore": False,
            "list": False,
            "get": False,
            "create": False,
            "manage": False,
            "define": False,
            "destroy": False,
            "unmanage": False,
        }

        firstverbfoundPosition = None
        verbPosition = None
        cookedlistofVerbs = [x for x in verbs]
        for verb in verbs:
            if verb not in sys.argv:
                # no need to iterate over the arg list for a verb that isn't in there
                continue
            if verbPosition:
                # once we've found the first verb we can stop looking
                break
            for counter, item in enumerate(sys.argv):
                if item == verb:
                    if firstverbfoundPosition is None:
                        # firstverbfoundPosition exists to prevent
                        # "toolkit.py create deploy create deploy" from deciding the second create
                        # is the first verb found
                        firstverbfoundPosition = counter
                    else:
                        if counter > firstverbfoundPosition:
                            continue
                        else:
                            firstverbfoundPosition = counter
                    # Why are we jumping through hoops here to remove the verb we found
                    # from the list of verbs?  Consider the input "toolkit.py deploy deploy"
                    # When we loop over the args we find the first "deploy"
                    # verb["deploy"] gets set to True, we loop over the slice of sys.argv
                    # previous to "deploy" and find no other verbs so verb["deploy"] remains True
                    # Then we find the second deploy.  We loop over the slice of sys.argv previous
                    # to *that* and sure enough, the first "deploy" is in verbs so
                    # verb["deploy"] gets set to False
                    try:
                        cookedlistofVerbs.remove(item)
                    except ValueError:
                        pass
                    verbs[verb] = True
                    verbPosition = counter
                    for item2 in sys.argv[:(counter)]:
                        # sys.argv[:(counter)] is a slice of sys.argv of all the items
                        # before the one we found
                        if item2 in cookedlistofVerbs:
                            # deploy wasn't the verb, it was a symbolic name of an object
                            verbs[verb] = False
                            verbPosition = None

        # Turn off verification to speed things up if true
        plaidMode = False
        for counter, item in enumerate(sys.argv):
            if verbPosition and counter < verbPosition and (item == "-f" or item == "--fast"):
                plaidMode = True

        if not plaidMode:
            # It isn't intuitive, however only one key in verbs can be True
            if verbs["deploy"]:
                chartsDict = updateHelm()
                for chart in chartsDict["items"]:
                    chartsList.append(chart["name"])

            elif verbs["clone"]:
                apps = astraSDK.getApps().main()
                for app in apps["items"]:
                    appList.append(app["id"])
                destCluster = astraSDK.getClusters().main(hideUnmanaged=True)
                for cluster in destCluster["items"]:
                    destclusterList.append(cluster["id"])
                backups = astraSDK.getBackups().main()
                for backup in backups["items"]:
                    backupList.append(backup["id"])
                snapshots = astraSDK.getSnaps().main()
                for snap in snapshots["items"]:
                    snapshotList.append(snap["id"])

            elif verbs["restore"]:
                for app in astraSDK.getApps().main()["items"]:
                    appList.append(app["id"])

                # This expression translates to "Is there an arg after the verb we found?"
                if len(sys.argv) - verbPosition >= 2:
                    # If that arg after the verb "restore" matches an appID then
                    # populate the lists of backups and snapshots for that appID
                    backups = astraSDK.getBackups().main()
                    for backup in backups["items"]:
                        if backup["appID"] == sys.argv[verbPosition + 1] or (
                            len(sys.argv) > verbPosition + 2
                            and backup["appID"] == sys.argv[verbPosition + 2]
                        ):
                            backupList.append(backup["id"])
                    snapshots = astraSDK.getSnaps().main()
                    for snapshot in snapshots["items"]:
                        if snapshot["appID"] == sys.argv[verbPosition + 1] or (
                            len(sys.argv) > verbPosition + 2
                            and snapshot["appID"] == sys.argv[verbPosition + 2]
                        ):
                            snapshotList.append(snapshot["id"])
            elif (
                verbs["create"]
                and len(sys.argv) - verbPosition >= 2
                and (
                    sys.argv[verbPosition + 1] == "backup"
                    or sys.argv[verbPosition + 1] == "hook"
                    or sys.argv[verbPosition + 1] == "protectionpolicy"
                    or sys.argv[verbPosition + 1] == "snapshot"
                )
            ):
                for app in astraSDK.getApps().main()["items"]:
                    appList.append(app["id"])
                if sys.argv[verbPosition + 1] == "hook":
                    for script in astraSDK.getScripts().main()["items"]:
                        scriptList.append(script["id"])

            elif (
                verbs["list"]
                and len(sys.argv) - verbPosition >= 2
                and sys.argv[verbPosition + 1] == "assets"
            ):
                for app in astraSDK.getApps().main()["items"]:
                    appList.append(app["id"])

            elif (verbs["manage"] or verbs["define"]) and len(sys.argv) - verbPosition >= 2:
                if sys.argv[verbPosition + 1] == "app":
                    namespaceDict = astraSDK.getNamespaces().main()
                    for namespace in namespaceDict["items"]:
                        namespaceList.append(namespace["name"])
                        clusterList.append(namespace["clusterID"])
                    clusterList = list(set(clusterList))
                elif sys.argv[verbPosition + 1] == "cluster":
                    clusterDict = astraSDK.getClusters(quiet=True).main()
                    for cluster in clusterDict["items"]:
                        if cluster["managedState"] == "unmanaged":
                            clusterList.append(cluster["id"])
                    storageClassDict = astraSDK.getStorageClasses(quiet=True).main()
                    if isinstance(storageClassDict, bool):
                        # astraSDK.getStorageClasses(quiet=True).main() returns either True
                        # or False if it doesn't work, or if there are no clouds or clusters
                        sys.exit(1)
                    for storageClass in storageClassDict["items"]:
                        if (
                            len(sys.argv) - verbPosition >= 3
                            and sys.argv[verbPosition + 2] in clusterList
                            and storageClass["clusterID"] != sys.argv[verbPosition + 2]
                        ):
                            continue
                        storageClassList.append(storageClass["id"])

            elif verbs["destroy"] and len(sys.argv) - verbPosition >= 2:
                if sys.argv[verbPosition + 1] == "backup" and len(sys.argv) - verbPosition >= 3:
                    for app in astraSDK.getApps().main()["items"]:
                        appList.append(app["id"])
                    backups = astraSDK.getBackups().main()
                    for backup in backups["items"]:
                        if backup["appID"] == sys.argv[verbPosition + 2]:
                            backupList.append(backup["id"])
                if sys.argv[verbPosition + 1] == "hook" and len(sys.argv) - verbPosition >= 3:
                    for app in astraSDK.getApps().main()["items"]:
                        appList.append(app["id"])
                    hooks = astraSDK.getHooks().main()
                    for hook in hooks["items"]:
                        if hook["appID"] == sys.argv[verbPosition + 2]:
                            hookList.append(hook["id"])
                elif sys.argv[verbPosition + 1] == "snapshot" and len(sys.argv) - verbPosition >= 3:
                    for app in astraSDK.getApps().main()["items"]:
                        appList.append(app["id"])
                    snapshots = astraSDK.getSnaps().main()
                    for snapshot in snapshots["items"]:
                        if snapshot["appID"] == sys.argv[verbPosition + 2]:
                            snapshotList.append(snapshot["id"])
                elif sys.argv[verbPosition + 1] == "script" and len(sys.argv) - verbPosition >= 3:
                    for script in astraSDK.getScripts().main()["items"]:
                        scriptList.append(script["id"])

            elif verbs["unmanage"] and len(sys.argv) - verbPosition >= 2:
                if sys.argv[verbPosition + 1] == "app":
                    for app in astraSDK.getApps().main()["items"]:
                        appList.append(app["id"])

                elif sys.argv[verbPosition + 1] == "cluster":
                    clusterDict = astraSDK.getClusters(quiet=True).main()
                    for cluster in clusterDict["items"]:
                        if cluster["managedState"] == "managed":
                            clusterList.append(cluster["id"])

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        "--verbose",
        default=False,
        action="store_true",
        help="print verbose/verbose output",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="table",
        choices=["json", "yaml", "table"],
        help="command output format",
    )
    parser.add_argument("-q", "--quiet", default=False, action="store_true", help="supress output")
    parser.add_argument(
        "-f",
        "--fast",
        default=False,
        action="store_true",
        help="prioritize speed over validation (using this will not validate arguments, which "
        + "may have unintended consequences)",
    )
    subparsers = parser.add_subparsers(dest="subcommand", required=True, help="subcommand help")
    #######
    # Top level subcommands
    # # Be sure to keep these in sync with verbs{}
    #######
    parserDeploy = subparsers.add_parser(
        "deploy",
        help="Deploy a helm chart",
    )
    parserClone = subparsers.add_parser(
        "clone",
        help="Clone an app",
    )
    parserRestore = subparsers.add_parser(
        "restore",
        help="Restore an app from a backup or snapshot",
    )
    parserList = subparsers.add_parser(
        "list",
        aliases=["get"],
        help="List all items in a class",
    )
    parserCreate = subparsers.add_parser(
        "create",
        help="Create an object",
    )
    parserManage = subparsers.add_parser(
        "manage",
        aliases=["define"],
        help="Manage an object",
    )
    parserDestroy = subparsers.add_parser(
        "destroy",
        help="Destroy an object",
    )
    parserUnmanage = subparsers.add_parser(
        "unmanage",
        help="Unmanage an object",
    )
    #######
    # End of top level subcommands
    #######

    #######
    # subcommands "list", "create", "manage", "destroy", and "unmanage" have subcommands as well
    #######
    subparserList = parserList.add_subparsers(title="objectType", dest="objectType", required=True)
    subparserCreate = parserCreate.add_subparsers(
        title="objectType", dest="objectType", required=True
    )
    subparserManage = parserManage.add_subparsers(
        title="objectType", dest="objectType", required=True
    )
    subparserDestroy = parserDestroy.add_subparsers(
        title="objectType", dest="objectType", required=True
    )
    subparserUnmanage = parserUnmanage.add_subparsers(
        title="objectType", dest="objectType", required=True
    )
    #######
    # end of subcommand "list", "create", "manage", "destroy", and "unmanage" subcommands
    #######

    #######
    # list 'X'
    #######
    subparserListApps = subparserList.add_parser(
        "apps",
        help="list apps",
    )
    subparserListAssets = subparserList.add_parser(
        "assets",
        help="list app assets",
    )
    subparserListBackups = subparserList.add_parser(
        "backups",
        help="list backups",
    )
    subparserListClouds = subparserList.add_parser(
        "clouds",
        help="list clouds",
    )
    subparserListClusters = subparserList.add_parser(
        "clusters",
        help="list clusters",
    )
    subparserListHooks = subparserList.add_parser("hooks", help="list hooks (executionHooks)")
    subparserListNamespaces = subparserList.add_parser(
        "namespaces",
        help="list namespaces",
    )
    subparserListScripts = subparserList.add_parser(
        "scripts",
        help="list scripts (hookSources)",
    )
    subparserListSnapshots = subparserList.add_parser(
        "snapshots",
        help="list snapshots",
    )
    subparserListStorageClasses = subparserList.add_parser(
        "storageclasses",
        help="list storageclasses",
    )
    #######
    # end of list 'X'
    #######

    #######
    # list apps args and flags
    #######
    subparserListApps.add_argument(
        "-n", "--namespace", default=None, help="Only show apps from this namespace"
    )
    subparserListApps.add_argument(
        "-c", "--cluster", default=None, help="Only show apps from this cluster"
    )
    #######
    # end of list apps args and flags
    #######

    #######
    # list assets args and flags
    #######
    subparserListAssets.add_argument(
        "appID",
        choices=(None if plaidMode else appList),
        help="The appID from which to display the assets",
    )
    #######
    # end of list assets args and flags
    #######

    #######
    # list backups args and flags
    #######
    subparserListBackups.add_argument(
        "-a", "--app", default=None, help="Only show backups from this app"
    )
    #######
    # end of list backups args and flags
    #######

    #######
    # list clouds args and flags
    #######

    #######
    # end of list clouds args and flags
    #######

    #######
    # list clusters args and flags
    #######
    subparserListClusters.add_argument(
        "-m",
        "--hideManaged",
        default=False,
        action="store_true",
        help="Hide managed clusters",
    )
    subparserListClusters.add_argument(
        "-u",
        "--hideUnmanaged",
        default=False,
        action="store_true",
        help="Hide unmanaged clusters",
    )
    #######
    # end of list clusters args and flags
    #######

    #######
    # list hooks args and flags
    #######
    subparserListHooks.add_argument(
        "-a", "--app", default=None, help="Only show execution hooks from this app"
    )
    #######
    # end of list hooks args and flags
    #######

    #######
    # list namespaces args and flags
    #######
    subparserListNamespaces.add_argument(
        "-c", "--clusterID", default=None, help="Only show namespaces from this clusterID"
    )
    subparserListNamespaces.add_argument(
        "-f",
        "--nameFilter",
        default=None,
        help="Filter namespaces by this value to minimize output",
    )
    subparserListNamespaces.add_argument(
        "-r",
        "--showRemoved",
        default=False,
        action="store_true",
        help="Show namespaces in a 'removed' state",
    )
    subparserListNamespaces.add_argument(
        "-m",
        "--minutes",
        default=False,
        type=int,
        help="Only show namespaces created within the last X minutes",
    )
    #######
    # end of list namespaces args and flags
    #######

    #######
    # list scripts args and flags
    #######
    subparserListScripts.add_argument(
        "-s",
        "--getScriptSource",
        default=None,
        help="Provide a script name to view the script source code",
    )
    #######
    # end of list scripts args and flags
    #######

    #######
    # list snapshots args and flags
    #######
    subparserListSnapshots.add_argument(
        "-a", "--app", default=None, help="Only show snapshots from this app"
    )
    #######
    # end of list snapshots args and flags
    #######

    #######
    # list storageclasses args and flags
    #######

    #######
    # end of list storageclasses args and flags
    #######

    #######
    # create 'X'
    #######
    subparserCreateBackup = subparserCreate.add_parser(
        "backup",
        help="create backup",
    )
    subparserCreateHook = subparserCreate.add_parser(
        "hook",
        help="create hook (executionHook)",
    )
    subparserCreateProtectionpolicy = subparserCreate.add_parser(
        "protectionpolicy",
        help="create protectionpolicy",
    )
    subparserCreateScript = subparserCreate.add_parser(
        "script",
        help="create script (hookSource)",
    )
    subparserCreateSnapshot = subparserCreate.add_parser(
        "snapshot",
        help="create snapshot",
    )
    #######
    # end of create 'X'
    #######

    #######
    # create backups args and flags
    #######
    subparserCreateBackup.add_argument(
        "appID",
        choices=(None if plaidMode else appList),
        help="appID to backup",
    )
    subparserCreateBackup.add_argument(
        "name",
        help="Name of backup to be taken",
    )
    subparserCreateBackup.add_argument(
        "-b",
        "--background",
        default=False,
        action="store_true",
        help="Run backup operation in the background",
    )
    #######
    # end of create backups args and flags
    #######

    #######
    # create hooks args and flags
    #######
    subparserCreateHook.add_argument(
        "appID",
        choices=(None if plaidMode else appList),
        help="appID to create an execution hook for",
    )
    subparserCreateHook.add_argument(
        "name",
        help="Name of the execution hook to be created",
    )
    subparserCreateHook.add_argument(
        "scriptID",
        choices=(None if plaidMode else scriptList),
        help="scriptID to use for the execution hook",
    )
    subparserCreateHook.add_argument(
        "-o",
        "--operation",
        choices=["pre-snapshot", "post-snapshot", "pre-backup", "post-backup", "post-restore"],
        required=True,
        type=str.lower,
        help="The operation type for the execution hook",
    )
    subparserCreateHook.add_argument(
        "-a",
        "--hookArguments",
        required=False,
        default=None,
        action="append",
        nargs="*",
        help="The (optional) arguments for the execution hook script",
    )
    subparserCreateHook.add_argument(
        "-r",
        "--containerRegex",
        default=None,
        # type=ascii,
        help="The (optional) container image name regex to match "
        + "(do not specify to match on all images)",
    )
    #######
    # end of create hooks args and flags
    #######

    #######
    # create protectionpolicy args and flags
    #######
    granArg = subparserCreateProtectionpolicy.add_argument(
        "-g",
        "--granularity",
        required=True,
        choices=["hourly", "daily", "weekly", "monthly"],
        help="Must choose one of the four options for the schedule",
    )
    subparserCreateProtectionpolicy.add_argument(
        "-b",
        "--backupRetention",
        type=int,
        required=True,
        choices=range(60),
        help="Number of backups to retain",
    )
    subparserCreateProtectionpolicy.add_argument(
        "-s",
        "--snapshotRetention",
        type=int,
        required=True,
        choices=range(60),
        help="Number of snapshots to retain",
    )
    subparserCreateProtectionpolicy.add_argument(
        "-M", "--dayOfMonth", type=int, choices=range(1, 32), help="Day of the month"
    )
    subparserCreateProtectionpolicy.add_argument(
        "-W",
        "--dayOfWeek",
        type=int,
        choices=range(7),
        help="0 = Sunday ... 6 = Saturday",
    )
    subparserCreateProtectionpolicy.add_argument(
        "-H", "--hour", type=int, choices=range(24), help="Hour in military time"
    )
    subparserCreateProtectionpolicy.add_argument(
        "-m", "--minute", default=0, type=int, choices=range(60), help="Minute"
    )
    subparserCreateProtectionpolicy.add_argument(
        "appID",
        choices=(None if plaidMode else appList),
        help="appID of the application to create protection schecule for",
    )
    #######
    # end of create protectionpolicy args and flags
    #######

    #######
    # create script args and flags
    #######
    subparserCreateScript.add_argument(
        "name",
        help="Name of the script",
    )
    subparserCreateScript.add_argument(
        "filePath",
        help="the local filesystem path to the script",
    )
    subparserCreateScript.add_argument(
        "-d",
        "--description",
        default=None,
        help="The optional description of the script",
    )
    #######
    # end of create script args and flags
    #######

    #######
    # create snapshot args and flags
    #######
    subparserCreateSnapshot.add_argument(
        "appID",
        choices=(None if plaidMode else appList),
        help="appID to snapshot",
    )
    subparserCreateSnapshot.add_argument(
        "name",
        help="Name of snapshot to be taken",
    )
    subparserCreateSnapshot.add_argument(
        "-b",
        "--background",
        default=False,
        action="store_true",
        help="Run snapshot operation in the background",
    )
    #######
    # end of create snapshot args and flags
    #######

    #######
    # manage 'X'
    #######
    subparserManageApp = subparserManage.add_parser(
        "app",
        help="manage app",
    )
    subparserManageCluster = subparserManage.add_parser(
        "cluster",
        help="manage cluster",
    )
    #######
    # end of manage 'X'
    #######

    #######
    # manage app args and flags
    #######
    subparserManageApp.add_argument("appName", help="The logical name of the newly defined app")
    subparserManageApp.add_argument(
        "namespace",
        choices=(None if plaidMode else namespaceList),
        help="The namespace to move from undefined (aka unmanaged) to defined (aka managed)",
    )
    subparserManageApp.add_argument(
        "-l",
        "--labelSelectors",
        required=False,
        default=None,
        help="Optional label selectors to filter resources to be included or excluded from "
        + "the application definition",
    )
    subparserManageApp.add_argument(
        "clusterID",
        choices=(None if plaidMode else clusterList),
        help="The clusterID hosting the newly defined app",
    )
    #######
    # end of manage app args and flags
    #######

    #######
    # manage cluster args and flags
    #######
    subparserManageCluster.add_argument(
        "clusterID",
        choices=(None if plaidMode else clusterList),
        help="clusterID of the cluster to manage",
    )
    subparserManageCluster.add_argument(
        "storageClassID",
        choices=(None if plaidMode else storageClassList),
        help="Default storage class ID",
    )
    #######
    # end of manage cluster args and flags
    #######

    #######
    # destroy 'X'
    #######
    subparserDestroyBackup = subparserDestroy.add_parser(
        "backup",
        help="destroy backup",
    )
    subparserDestroyHook = subparserDestroy.add_parser(
        "hook",
        help="destroy hook (executionHook)",
    )
    subparserDestroyScript = subparserDestroy.add_parser(
        "script",
        help="destroy script (hookSource)",
    )
    subparserDestroySnapshot = subparserDestroy.add_parser(
        "snapshot",
        help="destroy snapshot",
    )
    #######
    # end of destroy 'X'
    #######

    #######

    #######
    # destroy backup args and flags
    #######
    subparserDestroyBackup.add_argument(
        "appID",
        choices=(None if plaidMode else appList),
        help="appID of app to destroy backups from",
    )
    subparserDestroyBackup.add_argument(
        "backupID",
        choices=(None if plaidMode else backupList),
        help="backupID to destroy",
    )
    #######
    # end of destroy backup args and flags
    #######

    # destroy hook args and flags
    #######
    subparserDestroyHook.add_argument(
        "appID",
        choices=(None if plaidMode else appList),
        help="appID of app to destroy hooks from",
    )
    subparserDestroyHook.add_argument(
        "hookID",
        choices=(None if plaidMode else hookList),
        help="hookID to destroy",
    )
    #######
    # end of destroy backup args and flags
    #######

    #######
    # destroy script args and flags
    #######
    subparserDestroyScript.add_argument(
        "scriptID",
        choices=(None if plaidMode else scriptList),
        help="scriptID of script to destroy",
    )
    #######
    # end of destroy script args and flags
    #######

    #######
    # destroy snapshot args and flags
    #######
    subparserDestroySnapshot.add_argument(
        "appID",
        choices=(None if plaidMode else appList),
        help="appID of app to destroy snapshot from",
    )
    subparserDestroySnapshot.add_argument(
        "snapshotID",
        choices=(None if plaidMode else snapshotList),
        help="snapshotID to destroy",
    )
    #######
    # end of destroy snapshot args and flags
    #######

    #######
    # unmanage 'X'
    #######
    subparserUnmanageApp = subparserUnmanage.add_parser(
        "app",
        help="unmanage app",
    )
    subparserUnmanageCluster = subparserUnmanage.add_parser(
        "cluster",
        help="unmanage cluster",
    )
    #######
    # end of unmanage 'X'
    #######

    #######
    # unmanage app args and flags
    #######
    subparserUnmanageApp.add_argument(
        "appID",
        choices=(None if plaidMode else appList),
        help="appID of app to move from managed to unmanaged",
    )
    #######
    # end of unmanage app args and flags
    #######

    #######
    # unmanage cluster args and flags
    #######
    subparserUnmanageCluster.add_argument(
        "clusterID",
        choices=(None if plaidMode else clusterList),
        help="clusterID of the cluster to unmanage",
    )
    #######
    # end of unmanage cluster args and flags
    #######

    #######
    # deploy args and flags
    #######
    parserDeploy.add_argument(
        "app",
        help="name of app",
    )
    parserDeploy.add_argument(
        "chart",
        choices=(None if plaidMode else chartsList),
        help="chart to deploy",
    )
    parserDeploy.add_argument(
        "-n", "--namespace", required=True, help="Namespace to deploy into (must not already exist)"
    )
    parserDeploy.add_argument(
        "-f",
        "--values",
        required=False,
        action="append",
        nargs="*",
        help="Specify Helm values in a YAML file",
    )
    parserDeploy.add_argument(
        "--set",
        required=False,
        action="append",
        nargs="*",
        help="Individual helm chart parameters",
    )
    #######
    # end of deploy args and flags
    #######

    #######
    # clone args and flags
    #######
    parserClone.add_argument(
        "-b",
        "--background",
        default=False,
        action="store_true",
        help="Run clone operation in the background",
    )
    parserClone.add_argument(
        "--cloneAppName",
        required=False,
        default=None,
        help="Clone app name",
    )
    parserClone.add_argument(
        "--cloneNamespace",
        required=False,
        default=None,
        help="Clone namespace name (optional, if not specified cloneAppName is used)",
    )
    parserClone.add_argument(
        "--clusterID",
        choices=(None if plaidMode else destclusterList),
        required=False,
        default=None,
        help="Cluster to clone into (can be same as source)",
    )
    group = parserClone.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--backupID",
        choices=(None if plaidMode else backupList),
        required=False,
        default=None,
        help="Source backup to clone",
    )
    group.add_argument(
        "--snapshotID",
        choices=(None if plaidMode else snapshotList),
        required=False,
        default=None,
        help="Source snapshot to restore from",
    )
    group.add_argument(
        "--sourceAppID",
        choices=(None if plaidMode else appList),
        required=False,
        default=None,
        help="Source app to clone",
    )
    #######
    # end of clone args and flags
    #######

    #######
    # restore args and flags
    #######
    parserRestore.add_argument(
        "-b",
        "--background",
        default=False,
        action="store_true",
        help="Run restore operation in the background",
    )
    parserRestore.add_argument(
        "appID",
        choices=(None if plaidMode else appList),
        help="appID to restore",
    )
    group = parserRestore.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--backupID",
        choices=(None if plaidMode else backupList),
        required=False,
        default=None,
        help="Source backup to restore from",
    )
    group.add_argument(
        "--snapshotID",
        choices=(None if plaidMode else snapshotList),
        required=False,
        default=None,
        help="Source snapshot to restore from",
    )
    #######
    # end of restore args and flags
    #######

    args = parser.parse_args()
    # print(f"args: {args}")
    if hasattr(args, "granularity"):
        if args.granularity == "hourly":
            if args.hour:
                raise argparse.ArgumentError(granArg, " hourly must not specify -H / --hour")
            if not hasattr(args, "minute"):
                raise argparse.ArgumentError(granArg, " hourly requires -m / --minute")
            args.hour = "*"
            args.dayOfWeek = "*"
            args.dayOfMonth = "*"
        elif args.granularity == "daily":
            if type(args.hour) != int and not args.hour:
                raise argparse.ArgumentError(granArg, " daily requires -H / --hour")
            args.dayOfWeek = "*"
            args.dayOfMonth = "*"
        elif args.granularity == "weekly":
            if type(args.hour) != int and not args.hour:
                raise argparse.ArgumentError(granArg, " weekly requires -H / --hour")
            if type(args.dayOfWeek) != int and not args.dayOfWeek:
                raise argparse.ArgumentError(granArg, " weekly requires -W / --dayOfWeek")
            args.dayOfMonth = "*"
        elif args.granularity == "monthly":
            if type(args.hour) != int and not args.hour:
                raise argparse.ArgumentError(granArg, " monthly requires -H / --hour")
            if args.dayOfWeek:
                raise argparse.ArgumentError(granArg, " monthly must not specify -W / --dayOfWeek")
            if not args.dayOfMonth:
                raise argparse.ArgumentError(granArg, " monthly requires -M / --dayOfMonth")
            args.dayOfWeek = "*"

    tk = toolkit()
    if args.subcommand == "deploy":
        tk.deploy(
            args.chart,
            args.app,
            args.namespace,
            args.set,
            args.values,
            args.verbose,
        )
    elif args.subcommand == "list" or args.subcommand == "get":
        if args.objectType == "apps":
            rc = astraSDK.getApps(quiet=args.quiet, verbose=args.verbose, output=args.output).main(
                namespace=args.namespace,
                cluster=args.cluster,
            )
            if rc is False:
                print("astraSDK.getApps() failed")
                sys.exit(1)
            else:
                sys.exit(0)
        elif args.objectType == "assets":
            rc = astraSDK.getAppAssets(
                quiet=args.quiet, verbose=args.verbose, output=args.output
            ).main(args.appID)
            if rc is False:
                print("astraSDK.getAppAssets() failed")
            else:
                sys.exit(0)
        elif args.objectType == "backups":
            rc = astraSDK.getBackups(
                quiet=args.quiet, verbose=args.verbose, output=args.output
            ).main(appFilter=args.app)
            if rc is False:
                print("astraSDK.getBackups() failed")
                sys.exit(1)
            else:
                sys.exit(0)
        elif args.objectType == "clouds":
            rc = astraSDK.getClouds(
                quiet=args.quiet, verbose=args.verbose, output=args.output
            ).main()
            if rc is False:
                print("astraSDK.getClouds() failed")
                sys.exit(1)
            else:
                sys.exit(0)
        elif args.objectType == "clusters":
            rc = astraSDK.getClusters(
                quiet=args.quiet, verbose=args.verbose, output=args.output
            ).main(hideManaged=args.hideManaged, hideUnmanaged=args.hideUnmanaged)
            if rc is False:
                print("astraSDK.getClusters() failed")
                sys.exit(1)
            else:
                sys.exit(0)
        elif args.objectType == "hooks":
            rc = astraSDK.getHooks(quiet=args.quiet, verbose=args.verbose, output=args.output).main(
                appFilter=args.app
            )
            if rc is False:
                print("astraSDK.getHooks() failed")
                sys.exit(1)
            else:
                sys.exit(0)
        elif args.objectType == "namespaces":
            rc = astraSDK.getNamespaces(
                quiet=args.quiet, verbose=args.verbose, output=args.output
            ).main(
                clusterID=args.clusterID,
                nameFilter=args.nameFilter,
                showRemoved=args.showRemoved,
                minuteFilter=args.minutes,
            )
            if rc is False:
                print("astraSDK.getNamespaces() failed")
                sys.exit(1)
            else:
                sys.exit(0)
        elif args.objectType == "scripts":
            if args.getScriptSource:
                args.quiet = True
                args.output = "json"
            rc = astraSDK.getScripts(
                quiet=args.quiet, verbose=args.verbose, output=args.output
            ).main(scriptSourceName=args.getScriptSource)
            if rc is False:
                print("astraSDK.getScripts() failed")
                sys.exit(1)
            else:
                if args.getScriptSource:
                    if len(rc["items"]) == 0:
                        print(f"Script of name '{args.getScriptSource}' not found.")
                    for script in rc["items"]:
                        print(base64.b64decode(script["source"]).decode("utf-8"))
                sys.exit(0)
        elif args.objectType == "snapshots":
            rc = astraSDK.getSnaps(quiet=args.quiet, verbose=args.verbose, output=args.output).main(
                appFilter=args.app
            )
            if rc is False:
                print("astraSDK.getSnaps() failed")
                sys.exit(1)
            else:
                sys.exit(0)
        elif args.objectType == "storageclasses":
            rc = astraSDK.getStorageClasses(
                quiet=args.quiet, verbose=args.verbose, output=args.output
            ).main()
            if rc is False:
                print("astraSDK.getStorageClasses() failed")
                sys.exit(1)
            else:
                sys.exit(0)
    elif args.subcommand == "create":
        if args.objectType == "backup":
            rc = doProtectionTask(args.objectType, args.appID, args.name, args.background)
            if rc is False:
                print("doProtectionTask() failed")
                sys.exit(1)
            else:
                sys.exit(0)
        elif args.objectType == "hook":
            rc = astraSDK.createHook(quiet=args.quiet, verbose=args.verbose).main(
                args.appID,
                args.name,
                args.scriptID,
                args.operation.split("-")[0],
                args.operation.split("-")[1],
                createHookList(args.hookArguments),
                args.containerRegex,
            )
            if rc is False:
                print("astraSDK.createHook() failed")
            else:
                sys.exit(0)
        elif args.objectType == "protectionpolicy":
            rc = astraSDK.createProtectionpolicy(quiet=args.quiet, verbose=args.verbose).main(
                args.granularity,
                str(args.backupRetention),
                str(args.snapshotRetention),
                str(args.dayOfWeek),
                str(args.dayOfMonth),
                str(args.hour),
                str(args.minute),
                args.appID,
            )
            if rc is False:
                print("astraSDK.createProtectionpolicy() failed")
                sys.exit(1)
            else:
                sys.exit(0)
        elif args.objectType == "script":
            with open(args.filePath, encoding="utf8") as f:
                encodedStr = base64.b64encode(f.read().rstrip().encode("utf-8")).decode("utf-8")
            rc = astraSDK.createScript(quiet=args.quiet, verbose=args.verbose).main(
                name=args.name, source=encodedStr, description=args.description
            )
            if rc is False:
                print("astraSDK.createScript() failed")
            else:
                sys.exit(0)
        elif args.objectType == "snapshot":
            rc = doProtectionTask(args.objectType, args.appID, args.name, args.background)
            if rc is False:
                print("doProtectionTask() failed")
                sys.exit(1)
            else:
                sys.exit(0)

    elif args.subcommand == "manage" or args.subcommand == "define":
        if args.objectType == "app":
            rc = astraSDK.manageApp(quiet=args.quiet, verbose=args.verbose).main(
                args.appName, args.namespace, args.clusterID, args.labelSelectors
            )
            if rc is False:
                print("astraSDK.manageApp() failed")
                sys.exit(1)
            else:
                sys.exit(0)
        if args.objectType == "cluster":
            rc = astraSDK.manageCluster(quiet=args.quiet, verbose=args.verbose).main(
                args.clusterID, args.storageClassID
            )
            if rc is False:
                print("astraSDK.manageCluster() failed")
                sys.exit(1)
            else:
                sys.exit(0)
    elif args.subcommand == "destroy":
        if args.objectType == "backup":
            rc = astraSDK.destroyBackup(quiet=args.quiet, verbose=args.verbose).main(
                args.appID, args.backupID
            )
            if rc:
                print(f"Backup {args.backupID} destroyed")
            else:
                print(f"Failed destroying backup: {args.backupID}")
        if args.objectType == "hook":
            rc = astraSDK.destroyHook(quiet=args.quiet, verbose=args.verbose).main(
                args.appID, args.hookID
            )
            if rc:
                print(f"Hook {args.hookID} destroyed")
            else:
                print(f"Failed destroying hook: {args.hookID}")
        elif args.objectType == "script":
            rc = astraSDK.destroyScript(quiet=args.quiet, verbose=args.verbose).main(args.scriptID)
            if rc:
                print(f"Script {args.scriptID} destroyed")
            else:
                print(f"Failed destroying script: {args.scriptID}")
        elif args.objectType == "snapshot":
            rc = astraSDK.destroySnapshot(quiet=args.quiet, verbose=args.verbose).main(
                args.appID, args.snapshotID
            )
            if rc:
                print(f"Snapshot {args.snapshotID} destroyed")
            else:
                print(f"Failed destroying snapshot: {args.snapshotID}")
    elif args.subcommand == "unmanage":
        if args.objectType == "app":
            rc = astraSDK.unmanageApp(quiet=args.quiet, verbose=args.verbose).main(args.appID)
            if rc is False:
                print("astraSDK.unmanageApp() failed")
                sys.exit(1)
            else:
                sys.exit(0)
        if args.objectType == "cluster":
            rc = astraSDK.unmanageCluster(quiet=args.quiet, verbose=args.verbose).main(
                args.clusterID
            )
            if rc is False:
                print("astraSDK.unmanageCluster() failed")
                sys.exit(1)
            else:
                sys.exit(0)
    elif args.subcommand == "restore":
        rc = astraSDK.restoreApp(quiet=args.quiet, verbose=args.verbose).main(
            args.appID, backupID=args.backupID, snapshotID=args.snapshotID
        )
        if rc:
            if args.background:
                print("Restore job submitted successfully")
                print("Background restore flag selected, run 'list apps' to get status")
                sys.exit(0)
            print("Restore job in progress...", end="")
            sys.stdout.flush()
            while True:
                restoreApps = astraSDK.getApps().main()
                state = None
                for restoreApp in restoreApps["items"]:
                    if restoreApp["id"] == args.appID:
                        state = restoreApp["state"]
                if state == "restoring":
                    print(".", end="")
                    sys.stdout.flush()
                elif state == "ready":
                    print("Success!")
                    break
                elif state == "failed":
                    print("Failed!")
                    sys.exit(2)
                time.sleep(5)
        else:
            print("Submitting restore job failed.")
            sys.exit(3)

    elif args.subcommand == "clone":
        if not args.cloneAppName:
            args.cloneAppName = input("App name for the clone: ")
        if not args.clusterID:
            print("Select destination cluster for the clone")
            print("Index\tClusterID\t\t\t\tclusterName\tclusterPlatform")
            args.clusterID = userSelect(destCluster, ["id", "name", "clusterType"])

        # Determine sourceClusterID and the appID (appID could be provided by args.sourceAppID,
        # however if it's not that value will be 'None', and if so it needs to stay 'None' when
        # a backup or snapshot ID is provided for the app to be cloned from the correctly).
        sourceClusterID = ""
        appIDstr = ""
        # Handle -f/--fast/plaidMode cases
        if plaidMode:
            apps = astraSDK.getApps().main()
        if args.sourceAppID:
            for app in apps["items"]:
                if app["id"] == args.sourceAppID:
                    sourceClusterID = app["clusterID"]
                    appIDstr = app["id"]
        elif args.backupID:
            if plaidMode:
                backups = astraSDK.getBackups().main()
            for app in apps["items"]:
                for backup in backups["items"]:
                    if app["id"] == backup["appID"] and backup["id"] == args.backupID:
                        sourceClusterID = app["clusterID"]
                        appIDstr = app["id"]
        elif args.snapshotID:
            if plaidMode:
                snapshots = astraSDK.getSnaps().main()
            for app in apps["items"]:
                for snapshot in snapshots["items"]:
                    if app["id"] == snapshot["appID"] and snapshot["id"] == args.snapshotID:
                        sourceClusterID = app["clusterID"]
                        appIDstr = app["id"]
        # Ensure appIDstr is not equal to "", if so bad values were passed in with plaidMode
        if appIDstr == "":
            print(
                "Error: the corresponding appID was not found in the system, please check "
                + "your inputs and try again."
            )
            sys.exit(1)

        tk.clone(
            args.cloneAppName,
            args.clusterID,
            sourceClusterID,
            appIDstr,
            args.cloneNamespace,
            backupID=args.backupID,
            snapshotID=args.snapshotID,
            sourceAppID=args.sourceAppID,
            background=args.background,
            verbose=args.verbose,
        )


if __name__ == "__main__":
    main()
