# Integrated protection in Jenkins Pipeline using NetApp Astra Control Center

This example involves taking the backup of the staging and production environments of the application and its stateful data using NetApp Astra Control Center in the same pipeline that builds and deploys the application to those environments. These backups could later be relied upon in case of any technical issues.

The application we consider in this example is an e-commerce application based on Magento which is installed in Red Hat OpenShift cluster. The data for the application is hosted on NetApp ONTAP while provisioned and interfaced by NetApp Astra Trident. 

## Pre-requisites for using the pipeline example:
	
	1. Docker installed Jenkins worker node
	2. Enable docker plugin in Jenkins
	3. Enable OpenShift plugin in Jenkins

## Snippet of Jenkinsfile that covers installing/configuring NetApp Astra Toolkit and taking backups of the application:

    stage("Download & Configure Astra Toolkit") {
        steps {
            sh "wget https://github.com/NetApp/netapp-astra-toolkits/archive/refs/tags/v${ASTRA_TOOLKIT_VERSION}.tar.gz"
            sh "tar -xvzf v${ASTRA_TOOLKIT_VERSION}.tar.gz"
            sh "cp netapp-astra-toolkits-${ASTRA_TOOLKIT_VERSION}/jenkins_examples/scripts/* netapp-astra-toolkits-${ASTRA_TOOLKIT_VERSION}/"
            sh "chmod +x netapp-astra-toolkits-${ASTRA_TOOLKIT_VERSION}/astra_toolkit_setup.sh"
            sh "./netapp-astra-toolkits-${ASTRA_TOOLKIT_VERSION}/astra_toolkit_setup.sh -t AHvyfAfhr97dtfO9POumMhaWscqjs_sdwPBH0= -a fe134efa-9c50-654d-b207-9gf175d17gf0 -f netapp-astra-control-center.cie.netapp.com"
        }
    }
    stage("Backup of Staging Env") {
        steps {
            dir("netapp-astra-toolkits-${ASTRA_TOOLKIT_VERSION}") {
                sh "pip3 install -r requirements.txt --user"
                sh "python3 createBackup.py -c ocp-vmw -a magento-staging -b upgrade-stag-${MAGENTO_VERSION.replaceAll("\\.", "-")}"
                sh "python3 waitforBackup.py -c ocp-vmw -a magento-staging -b upgrade-stag-${MAGENTO_VERSION.replaceAll("\\.", "-")}"
            }
        }
    }
    stage("Backup of Production Env") {
        steps {
            dir("netapp-astra-toolkits-${ASTRA_TOOLKIT_VERSION}") {
                sh "pip3 install -r requirements.txt --user"
                sh "python3 createBackup.py -c ocp-vmw -a magento-prod -b upgrade-prod-${MAGENTO_VERSION.replaceAll("\\.", "-")}"
                sh "python3 waitforBackup.py -c ocp-vmw -a magento-prod -b upgrade-prod-${MAGENTO_VERSION.replaceAll("\\.", "-")}"
            }
        }
    }
    
## Authors

- [Alan Cowles](mailto:alan.cowles@netapp.com) - NetApp Hybrid Cloud Solutions Team
- [Nikhil M Kulkarni](mailto:nikhil.kulkarni@netapp.com) - NetApp Hybrid Cloud Solutions Team
