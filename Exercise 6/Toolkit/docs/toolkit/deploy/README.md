# Deploy

The `deploy` command has the following command syntax:

```text
./toolkit.py deploy <chartname> <appname> <namespacename> -f/--values <values.yaml> \
    --set <value1> --set <value2>
```

This command will carry out the following operations on your *current kubeconfig context*:

1. Installs the bitnami, gitlab, and cloudbees helm repositories if they're not already installed
1. Updates all the helm repositories (the three listed in step 1, and any user-defined repos)
1. Checks to ensure that \<namespacename\> does not currently exist on the Kubernetes cluster
1. Creates the \<namespacename\> namespace on the Kubernetes cluster
1. Sets the kubeconfig context to utilize the \<namespacename\>
1. Runs a `helm install` command deploying \<chartname\> with the name of \<appname\>
  1. *Optionally* specify any number of [values files](https://helm.sh/docs/chart_template_guide/values_files/) with `-f`/`--values`
  1. *Optionally* specify any number of individual [values](https://helm.sh/docs/chart_template_guide/values_files/) with `--set`
1. Waits for Astra Control to discover the newly deployed \<appname\>
1. Has Astra Control manage the newly discovered \<appname\>
1. Creates a basic protection policy for the newly managed \<appname\>

Sample output:

```text
$ ./toolkit.py deploy cloudbees-core cloudbees-core cloudbees-core \
    -f values.yaml \
    --set OperationsCenter.HostName=cloudbees-core.netapp.com \
    --set ingress-nginx.Enabled=true
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "gitlab" chart repository
...Successfully got an update from the "jfrog" chart repository
...Successfully got an update from the "cloudbees" chart repository
...Successfully got an update from the "bitnami" chart repository
Update Complete. ⎈Happy Helming!⎈
namespace/cloudbees-core created
Context "gke_astracontroltoolkitdev_us-east1-b_useast1-cluster" modified.
NAME: cloudbees-core
LAST DEPLOYED: Fri May 27 15:25:00 2022
NAMESPACE: cloudbees-core
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
1. Once Operations Center is up and running, get your initial admin user password by running:
  kubectl rollout status sts cjoc --namespace cloudbees-core
  kubectl exec cjoc-0 --namespace cloudbees-core -- cat /var/jenkins_home/secrets/initialAdminPassword
2. Visit http://cloudbees-core.netapp.com/cjoc/


3. Login with the password from step 1.

For more information on running CloudBees Core on Kubernetes, visit:
https://go.cloudbees.com/docs/cloudbees-core/cloud-admin-guide/
Waiting for Astra to discover apps............Discovery complete!
Managing: cloudbees-core.....Success.
Setting hourly protection policy on 855d7fb2-5a7f-494f-ab0b-aea35344ad86
Setting daily protection policy on 855d7fb2-5a7f-494f-ab0b-aea35344ad86
Setting weekly protection policy on 855d7fb2-5a7f-494f-ab0b-aea35344ad86
Setting monthly protection policy on 855d7fb2-5a7f-494f-ab0b-aea35344ad86
```
