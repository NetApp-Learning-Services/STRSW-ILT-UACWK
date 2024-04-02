# This script has been written for this exercise environment 
# and is not intented to be used in a production enviroment
# Execute by: ./exercise1Task5-5.sh

#!/bin/bash
REGISTRY_NAME="docker-registry" 

sudo apt install sshpass

for x in $(kubectl get nodes -o jsonpath='{ $.items[*].status.addresses[?(@.type=="InternalIP")].address }'); 
do 
  echo "Working on node:  $x"
  sshpass -p Netapp1! scp -o "StrictHostKeyChecking=no" tls.crt root@$x:/etc/containerd/certs.d/$REGISTRY_NAME:30001/ca.crt;
done