# Leverage NetApp Astra Control to Perform Post-mortem Analysis and Restore Your Application

This example involves cloning the production environment of the application when in a broken state and restoring the production to a previous backup using NetApp Astra Control Center in a Jenkins pipeline.
 
The application we consider in this example is an e-commerce application based on Magento which is installed in Red Hat OpenShift cluster. The data for the application is hosted on NetApp ONTAP while provisioned and interfaced by NetApp Astra Trident.

## Pre-requisites for using the pipeline example:
	
    1. Enable OpenShift plugin in Jenkins

## Snippet of Jenkinsfile that covers cloning and restoring the application:
    stage("Clone production environment") {
        steps {
            dir("netapp-astra-toolkits-${ASTRA_TOOLKIT_VERSION}") {
                sh 'pip3 install -r requirements.txt --user'
                sh "python3 cloneApp.py --clone-name ${DEBUG_APP_NAME} --clone-namespace ${DEBUG_NAMESPACE} 
            }
            script {
                openshift.withCluster('ocp-vmw') {
                    def CLONE_LB_IP = sh (script: "oc get svc magento -n magento-prod | grep LoadBalancer | awk '{print 
                    echo "${CLONE_LB_IP}"
                    sh "helm upgrade --reuse-values magento bitnami/magento --namespace ${DEBUG_NAMESPACE} --wait --timeout 
                }
            }
        }
    }

    stage("Restore production environment") {
        steps {
            dir("netapp-astra-toolkits-${ASTRA_TOOLKIT_VERSION}") {
                sh 'pip3 install -r requirements.txt --user'
                sh "python3 restoreApp.py --application-name ${PROD_APP_NAME} --use-backup 
            }
        }
    }   
    
    
## Authors
- [Alan Cowles](mailto:alan.cowles@netapp.com) - NetApp Hybrid Cloud Solutions Team 
- [Nikhil M Kulkarni](mailto:nikhil.kulkarni@netapp.com) - NetApp Hybrid Cloud Solutions Team
