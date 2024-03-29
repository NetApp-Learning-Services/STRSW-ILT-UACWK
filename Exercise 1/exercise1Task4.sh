# This script has been written for this exercise environment 
# and is not intented to be used in a production enviroment

#!/bin/bash
sudo apt install sshpass

for x in $(kubectl get nodes -o jsonpath='{ $.items[*].status.addresses[?(@.type=="InternalIP")].address }'); 
do
 echo "Working on node:  $x"
 sshpass -p Netapp1! ssh root@$x -o "StrictHostKeyChecking=no" "mpathconf --enable; sudo systemctl restart iscsid multipathd"; 
done