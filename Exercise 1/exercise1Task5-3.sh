# This script has been written for this exercise environment 
# and is not intented to be used in a production enviroment
# Execute by: ./exercise1Task5-3.sh

#!/bin/bash
REGISTRY_NAME="docker-registry"
REGISTRY_IP="192.168.0.61"  

sudo apt install sshpass

for x in $(kubectl get nodes -o jsonpath='{ $.items[*].status.addresses[?(@.type=="InternalIP")].address }'); 
do 
  echo "Working on node:  $x"
  sshpass -p Netapp1! ssh -o "StrictHostKeyChecking=no" root@$x "echo '$REGISTRY_IP $REGISTRY_NAME' >> /etc/hosts";
  echo "Result: "
  sshpass -p Netapp1! ssh -o "StrictHostKeyChecking=no" root@$x "cat /etc/hosts";
done