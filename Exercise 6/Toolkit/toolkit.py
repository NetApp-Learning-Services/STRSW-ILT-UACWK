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
        outputStr = str(counter) + ":\t\t"
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
        # [{'name': 'stable', 'url': 'https://charts.helm.sh/stable'},
        #  {'name': 'bitnami', 'url': 'https://charts.bitnami.com/bitnami'}
        # ]
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
    for val in repos.values():
        charts = run(f"helm -o yaml search repo {val}", captureOutput=True)
        chartsYaml = yaml.load(charts, Loader=yaml.SafeLoader)
        for line in chartsYaml:
            chartsDict[(line.get("name").split("/")[1])] = val
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

    def deploy(
        self, chartName, repoName, appName, nameSpace, domain, email, ssl, setValues, fileValues
    ):
        """Deploy a helm chart <chartName>, from helm repo <repoName>
        naming the app <appName> into <nameSpace>"""

        setStr = createHelmStr("set", setValues)
        valueStr = createHelmStr("values", fileValues)

        if chartName == "gitlab":
            assert domain is not None
            assert email is not None

        getAppsObj = astraSDK.getApps()
        retval = run("kubectl get ns -o json", captureOutput=True)
        retvalJSON = json.loads(retval)
        for item in retvalJSON["items"]:
            if item["metadata"]["name"] == nameSpace:
                print(f"Namespace {nameSpace} already exists!")
                sys.exit(24)
        run(f"kubectl create namespace {nameSpace}")
        run(f"kubectl config set-context --current --namespace={nameSpace}")
        if chartName == "gitlab":
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

        else:
            run(f"helm install {appName} {repoName}/{chartName}{setStr}{valueStr}")
        print("Waiting for Astra to discover apps.", end="")
        sys.stdout.flush()

        appID = ""
        while not appID:
            # It takes Astra some time to realize new apps have been installed
            time.sleep(3)
            print(".", end="")
            sys.stdout.flush()
            apps = getAppsObj.main(discovered=True, namespace=nameSpace)
            # Cycle through the apps and see if one matches our new namespace
            for app in apps["items"]:
                if app["name"] == nameSpace and app["namespace"] == nameSpace:
                    print("Discovery complete!")
                    sys.stdout.flush()
                    appID = app["id"]
                    # Spin on managing apps.  Astra Control won't allow switching an
                    # app that is in the pending state to managed.  So we retry endlessly
                    # with the assumption that eventually the app will switch from
                    # pending to running and the manageapp call will succeed.
                    print(f"Managing: {app['name']}.", end="")
                    sys.stdout.flush()
                    rv = astraSDK.manageApp().main(appID)
                    while not rv:
                        print(".", end="")
                        sys.stdout.flush()
                        time.sleep(3)
                        rv = astraSDK.manageApp().main(appID)
                    print("Success.")
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
        clusterID,
        destNamespace,
        cloneName,
        namespaces,
        sourceAppID,
        backupID,
        background,
    ):
        """Create a clone."""
        # The REST API for cloning requires the sourceClusterID, we look that
        # up from the passed in namespaces var.
        #         appID
        needsIngressclass = False
        for app in namespaces["items"]:
            if sourceAppID == app["id"]:
                sourceClusterID = app["clusterID"]
                for pod in app["pods"]:
                    for container in pod["containers"]:
                        if "cloudbees/cloudbees-cloud-core-oc" in container["image"]:
                            needsIngressclass = True

        # Clone 'ingressclass' cluster object
        if needsIngressclass and sourceClusterID != clusterID:
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
                sourceIngress["metadata"]["labels"]["app.kubernetes.io/instance"] = destNamespace
                sourceIngress["metadata"]["annotations"][
                    "meta.helm.sh/release-name"
                ] = destNamespace
                sourceIngress["metadata"]["annotations"][
                    "meta.helm.sh/release-namespace"
                ] = destNamespace
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
                            "app.kubernetes.io/instance": destNamespace,
                            "app.kubernetes.io/managed-by": "Helm",
                            "app.kubernetes.io/name": "ingress-nginx",
                            "app.kubernetes.io/version": "1.1.0",
                            "helm.sh/chart": "ingress-nginx-4.0.13",
                        },
                        "annotations": {
                            "meta.helm.sh/release-name": destNamespace,
                            "meta.helm.sh/release-namespace": destNamespace,
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

        cloneRet = astraSDK.cloneApp().main(
            cloneName,
            clusterID,
            sourceClusterID,
            destNamespace,
            backupID=backupID,
            snapshotID=None,
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
            while state != "running":
                apps = astraSDK.getApps().main()
                for app in apps["items"]:
                    if app["id"] == appID:
                        if app["state"] == "running":
                            state = app["state"]
                            print("Cloning operation complete.")
                            sys.stdout.flush()
                        else:
                            print(".", end="")
                            sys.stdout.flush()
                            time.sleep(3)
        else:
            print("Submitting clone failed.")


if __name__ == "__main__":
    # This is a pretty big hack.  The various functions to populate the lists
    # used for choices() in the options are expensive.  argparse provides no
    # way to know what subcommand was selected prior to parsing the options.
    # By then it's too late to decide which functions to run to populate
    # the various choices the differing options for each subcommand needs.
    # So we just go around argparse's back and introspect sys.argv directly
    chartsList = []
    namespacesList = []
    backupList = []
    snapshotList = []
    destclusterList = []
    appList = []
    clusterList = []
    storageClassList = []
    if len(sys.argv) > 1:
        returnNames = False
        if "-s" in sys.argv or "--symbolicnames" in sys.argv:
            returnNames = True
        # since we support symbolic names we have to guard against
        # commands like ./toolkit.py -s create backup clone backupname
        # where the toolkit verbs are also used as object names.

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

        # It isn't intuitive, however only one key in verbs can be True

        if verbs["deploy"]:
            chartsDict = updateHelm()
            for k in chartsDict:
                chartsList.append(k)

        elif verbs["clone"]:
            namespaces = astraSDK.getApps().main(source="namespace", delPods=False)
            for app in namespaces["items"]:
                namespacesList.append(app["id"])
            destCluster = astraSDK.getClusters().main(hideUnmanaged=True)
            for cluster in destCluster["items"]:
                destclusterList.append(cluster["id"])
            backups = astraSDK.getBackups().main()
            if backups is False:
                print("astraSDK.getBackups().main() failed")
                sys.exit(1)
            elif backups is True:
                print("No apps found")
                sys.exit(1)
            for backup in backups["items"]:
                backupList.append(backup["id"])

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
                or sys.argv[verbPosition + 1] == "protectionpolicy"
                or sys.argv[verbPosition + 1] == "snapshot"
            )
        ):
            for app in astraSDK.getApps().main()["items"]:
                appList.append(app["id"])

        elif verbs["manage"] and len(sys.argv) - verbPosition >= 2:
            if sys.argv[verbPosition + 1] == "app":
                for app in astraSDK.getApps().main(discovered=True)["items"]:
                    appList.append(app["id"])
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
            elif sys.argv[verbPosition + 1] == "snapshot" and len(sys.argv) - verbPosition >= 3:
                for app in astraSDK.getApps().main()["items"]:
                    appList.append(app["id"])
                snapshots = astraSDK.getSnaps().main()
                for snapshot in snapshots["items"]:
                    if snapshot["appID"] == sys.argv[verbPosition + 2]:
                        snapshotList.append(snapshot["id"])

        elif verbs["unmanage"] and len(sys.argv) - verbPosition >= 2:
            if sys.argv[verbPosition + 1] == "app":
                for app in astraSDK.getApps().main(discovered=False)["items"]:
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
    # Note that this is just to integrate with argparse
    # The actual work done by this flag is done before
    # the argparse object is instantiated
    parser.add_argument(
        "-s",
        "--symbolicnames",
        default=False,
        action="store_true",
        help="list choices using names not UUIDs",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="table",
        choices=["json", "yaml", "table"],
        help="command output format",
    )
    parser.add_argument("-q", "--quiet", default=False, action="store_true", help="supress output")
    subparsers = parser.add_subparsers(dest="subcommand", required=True, help="subcommand help")
    #######
    # Top level subcommands
    # # Be sure to keep these in sync with verbs{}
    #######
    parserDeploy = subparsers.add_parser(
        "deploy",
        help="deploy a bitnami chart",
    )
    parserClone = subparsers.add_parser(
        "clone",
        help="clone a namespace to a destination cluster",
    )
    parserRestore = subparsers.add_parser(
        "restore",
        help="restore an app from a backup or snapshot",
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
    group = subparserListApps.add_mutually_exclusive_group(required=False)
    group.add_argument(
        "-u",
        "--unmanaged",
        default=False,
        action="store_true",
        help="Show only unmanaged apps",
    )
    group.add_argument(
        "-i",
        "--ignored",
        default=False,
        action="store_true",
        help="Show ignored apps",
    )
    subparserListApps.add_argument("-s", "--source", help="app source")
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
    subparserCreateProtectionpolicy = subparserCreate.add_parser(
        "protectionpolicy",
        help="create protectionpolicy",
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
        choices=appList,
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
        choices=appList,
        help="appID of the application to create protection schecule for",
    )
    #######
    # end of create protectionpolicy args and flags
    #######

    #######
    # create snapshot args and flags
    #######
    subparserCreateSnapshot.add_argument(
        "appID",
        choices=appList,
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
    subparserManageApp.add_argument(
        "appID",
        choices=appList,
        help="appID of app to move from discovered to managed",
    )
    #######
    # end of manage app args and flags
    #######

    #######
    # manage cluster args and flags
    #######
    subparserManageCluster.add_argument(
        "clusterID",
        choices=clusterList,
        help="clusterID of the cluster to manage",
    )
    subparserManageCluster.add_argument(
        "storageClassID",
        choices=storageClassList,
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
    subparserDestroySnapshot = subparserDestroy.add_parser(
        "snapshot",
        help="destroy snapshot",
    )
    #######
    # end of destroy 'X'
    #######

    #######
    # destroy backup args and flags
    #######
    subparserDestroyBackup.add_argument(
        "appID",
        choices=appList,
        help="appID of app to destroy backups from",
    )
    subparserDestroyBackup.add_argument(
        "backupID",
        choices=backupList,
        help="backupID to destroy",
    )
    #######
    # end of destroy backup args and flags
    #######

    #######
    # destroy snapshot args and flags
    #######
    subparserDestroySnapshot.add_argument(
        "appID",
        choices=appList,
        help="appID of app to destroy snapshot from",
    )
    subparserDestroySnapshot.add_argument(
        "snapshotID",
        choices=snapshotList,
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
        choices=appList,
        help="appID of app to move from managed to discovered",
    )
    #######
    # end of unmanage app args and flags
    #######

    #######
    # unmanage cluster args and flags
    #######
    subparserUnmanageCluster.add_argument(
        "clusterID",
        choices=clusterList,
        help="clusterID of the cluster to unmanage",
    )
    #######
    # end of unmanage cluster args and flags
    #######

    #######
    # deploy args and flags
    #######
    parserDeploy.add_argument(
        "chart",
        choices=chartsList,
        help="chart to deploy",
    )
    parserDeploy.add_argument(
        "app",
        help="name of app",
    )
    parserDeploy.add_argument("namespace", help="Namespace to deploy into (must not already exist)")
    parserDeploy.add_argument(
        "--domain",
        "-d",
        required=False,
        help="Default domain to pass gitlab deployment",
    )
    parserDeploy.add_argument(
        "--email",
        "-e",
        required=False,
        help="Email address for self-signed certs (gitlab only)",
    )
    parserDeploy.add_argument(
        "-s",
        "--ssl",
        default=True,
        action="store_false",
        help="Create self signed SSL certs",
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
        "--sourceNamespace",
        choices=namespacesList,
        required=False,
        default=None,
        help="Source namespace to clone",
    )
    parserClone.add_argument(
        "--backupID",
        choices=backupList,
        required=False,
        default=None,
        help="Source backup to clone",
    )
    parserClone.add_argument(
        "--clusterID",
        choices=destclusterList,
        required=False,
        default=None,
        help="Cluster to clone to",
    )
    parserClone.add_argument(
        "--destName",
        required=False,
        default=None,
        help="clone name",
    )
    parserClone.add_argument(
        "--destNamespace",
        required=False,
        default=None,
        help="Destination namespace",
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
        choices=appList,
        help="appID to restore",
    )
    group = parserRestore.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--backupID",
        choices=backupList,
        required=False,
        default=None,
        help="Source backup to restore from",
    )
    group.add_argument(
        "--snapshotID",
        choices=snapshotList,
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
        if hasattr(args, "domain"):
            domain = args.domain
        else:
            domain = None
        if hasattr(args, "email"):
            email = args.email
        else:
            email = None
        if hasattr(args, "ssl"):
            ssl = args.ssl
        else:
            ssl = True
        tk.deploy(
            args.chart,
            chartsDict[args.chart],
            args.app,
            args.namespace,
            domain,
            email,
            ssl,
            args.set,
            args.values,
        )
    elif args.subcommand == "list" or args.subcommand == "get":
        if args.objectType == "apps" or args.objectType == "app":
            rc = astraSDK.getApps(quiet=args.quiet, verbose=args.verbose, output=args.output).main(
                discovered=args.unmanaged,
                source=args.source,
                namespace=args.namespace,
                cluster=args.cluster,
                ignored=args.ignored,
            )
            if rc is False:
                print("astraSDK.getApps() failed")
                sys.exit(1)
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
                print("astraSDK.getClusters() Failed")
                sys.exit(1)
            else:
                sys.exit(0)
        elif args.objectType == "snapshots":
            rc = astraSDK.getSnaps(quiet=args.quiet, verbose=args.verbose, output=args.output).main(
                appFilter=args.app
            )
            if rc is False:
                print("astraSDK.getSnaps() Failed")
                sys.exit(1)
            else:
                sys.exit(0)
        elif args.objectType == "storageclasses":
            rc = astraSDK.getStorageClasses(
                quiet=args.quiet, verbose=args.verbose, output=args.output
            ).main()
            if rc is False:
                print("astraSDK.getStorageClasses() Failed")
                sys.exit(1)
            else:
                sys.exit(0)
    elif args.subcommand == "create":
        if args.objectType == "backup":
            rc = doProtectionTask(args.objectType, args.appID, args.name, args.background)
            if rc is False:
                print("doProtectionTask() Failed")
                sys.exit(1)
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
                print("astraSDK.createProtectionpolicy() Failed")
                sys.exit(1)
            else:
                sys.exit(0)
        elif args.objectType == "snapshot":
            rc = doProtectionTask(args.objectType, args.appID, args.name, args.background)
            if rc is False:
                print("doProtectionTask() Failed")
                sys.exit(1)
            else:
                sys.exit(0)

    elif args.subcommand == "manage":
        if args.objectType == "app":
            rc = astraSDK.manageApp(quiet=args.quiet, verbose=args.verbose).main(args.appID)
            if rc is False:
                print("astraSDK.manageApp() Failed")
                sys.exit(1)
            else:
                sys.exit(0)
        if args.objectType == "cluster":
            rc = astraSDK.manageCluster(quiet=args.quiet, verbose=args.verbose).main(
                args.clusterID, args.storageClassID
            )
            if rc is False:
                print("astraSDK.manageCluster() Failed")
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
                print("astraSDK.unmanageApp() Failed")
                sys.exit(1)
            else:
                sys.exit(0)
        if args.objectType == "cluster":
            rc = astraSDK.unmanageCluster(quiet=args.quiet, verbose=args.verbose).main(
                args.clusterID
            )
            if rc is False:
                print("astraSDK.unmanageCluster() Failed")
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
                elif state == "running":
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
        if not args.clusterID:
            print("Select destination cluster for the clone")
            print("Index\tClusterID\t\t\t\tclusterName\tclusterPlatform")
            args.clusterID = userSelect(destCluster, ["id", "name", "clusterType"])
        if not args.destNamespace:
            args.destNamespace = input(
                "Namespace for the clone "
                "(This must not be a namespace that currently exists on the destination cluster): "
            )
        if not args.destName:
            args.destName = input("Name for the clone: ")
        if not args.sourceNamespace:
            if not args.backupID:
                # no source namespace/app or source backup
                print(
                    "sourceNamespace and backupID are unspecified, you can pick a"
                    " sourceNamespace, then select a backup of that sourceNamespace."
                    " (If a backup of that namespace doesn't exist one"
                    " will be created.  Or you can specify a backupID to use directly."
                )
                while True:
                    retval = input("sourceNamespace or backupID: ")
                    if retval.lower().startswith("s"):
                        retval = "sourceNamespace"
                        break
                    elif retval.lower().startswith("b"):
                        retval = "backupID"
                        break
                    else:
                        print("Enter sourceNamespace or backupID")
                if retval == "sourceNamespace":
                    print("Select source namespace to be cloned")
                    print("Index\tAppID\t\t\t\t\tappName\t\tclusterName\tClusterID")
                    args.sourceNamespace = userSelect(
                        namespaces, ["id", "name", "clusterName", "clusterID"]
                    )
                    appBackupscooked = {}
                    appBackupscooked["items"] = []
                    for backup in backups["items"]:
                        if (
                            backup["appID"] == args.sourceNamespace
                            and backup["state"] == "completed"
                        ):
                            appBackupscooked["items"].append(backup)
                    if len(appBackupscooked["items"]) > 0:
                        print("Select source backup")
                        print("Index\tBackupID\t\t\t\tBackupName\t\tTimestamp\t\tAppID")
                        args.backupID = userSelect(
                            appBackupscooked, ["id", "name", "metadata/creationTimestamp", "appID"]
                        )
                    else:
                        # Take a backup
                        print("No backups found, taking backup.")
                        backupRetval = doProtectionTask(
                            "backup", args.sourceNamespace, f"toolkit-{args.destName}", False
                        )
                        if not backupRetval:
                            print("Exiting due to backup task failing.")
                            sys.exit(7)
                elif retval == "backupID":
                    # No namespace or backupID was specified on the CLI
                    # user opted to specify a backupID, from there we
                    # can work backwards to get the namespace.
                    appBackupscooked = {}
                    appBackupscooked["items"] = []
                    for backup in backups["items"]:
                        if backup["state"] == "completed":
                            appBackupscooked["items"].append(backup)
                    if len(appBackupscooked["items"]) == 0:
                        print("No backups found.")
                        sys.exit(6)
                    print("Index\tBackupID\t\t\t\tBackupName\t\tTimestamp\t\tAppID")
                    args.backupID = userSelect(
                        appBackupscooked, ["id", "name", "metadata/creationTimestamp", "appID"]
                    )
                    for backup in backups["items"]:
                        if backup["id"] == args.backupID:
                            args.sourceNamespace = backup["appID"]

            else:
                # no source namespace/app but we have a backupID
                # work backwards to get the appID
                for backup in backups["items"]:
                    if backup["id"] == args.backupID:
                        args.sourceNamespace = backup["appID"]
                if not args.sourceNamespace:
                    print("Can't determine appID from backupID")
                    sys.exit(9)
        else:
            # we have a source namespace/app
            # if we have a backupID we have everything we need
            if not args.backupID:
                appBackupscooked = {}
                appBackupscooked["items"] = []
                for backup in backups["items"]:
                    if backup["appID"] == args.sourceNamespace and backup["state"] == "completed":
                        appBackupscooked["items"].append(backup)
                if len(appBackupscooked["items"]) > 0:
                    print("Select source backup")
                    print("Index\tBackupID\t\t\t\tBackupName\t\tTimestamp\t\tAppID")
                    args.backupID = userSelect(
                        appBackupscooked, ["id", "name", "metadata/creationTimestamp", "appID"]
                    )
                    print(f"args.backupID: {args.backupID}")
                else:
                    # Take a backup
                    backupRetval = doProtectionTask(
                        "backup", args.sourceNamespace, f"toolkit-{args.destName}", False
                    )
                    if not backupRetval:
                        print("Exiting due to backup task failing.")
                        sys.exit(7)
        tk.clone(
            args.clusterID,
            args.destNamespace,
            args.destName,
            namespaces,
            sourceAppID=args.sourceNamespace,
            backupID=args.backupID,
            background=args.background,
        )
