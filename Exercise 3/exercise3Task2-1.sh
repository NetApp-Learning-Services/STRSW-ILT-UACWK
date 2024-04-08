# This script has been written for this exercise environment 
# and is not intented to be used in a production enviroment
# Execute by: ./exercise3Task2-1.sh

#!/bin/bash
sudo apt install sshpass
sshpass -p Netapp1! scp -o "StrictHostKeyChecking=no" root@kubmas1-1:/root/.kube/config config1 
sshpass -p Netapp1! scp -o "StrictHostKeyChecking=no" root@kubmas2-1:/root/.kube/config config2 
