# This is the bash script that is the equivalent to this script 
# that could be on the kubmas2.demo.netapp.com:

# for x in $(kubectl get nodes -o jsonpath='{ $.items[*].status.addresses[?(@.type=="InternalIP")].address }'); 
# do scp /registry/certs/tls.crt root@$x:/etc/docker/certs.d/$REGISTRY_NAME:5000/ca.crt;
# done

# This script has been written for this exercise environment 
# and is not intented to be used in a production enviroment

# Install the module required
Install-Module -Name Posh-SSH -Scope CurrentUser

# Get the nodes and get the IPAddress for each node
$collection = (kubectl get nodes -o json | convertfrom-Json)
$IPAddresses = [System.Collections.ArrayList]::new()

foreach ($item in $collection.items) {
    $addresses = $item.status.addresses
    foreach ($address in $addresses) {
        if ($address.type -eq "InternalIP"){
            [void]$IPAddresses.Add($address.address)
        }           
    }  
}
Write-Output('Nodes found:')
$IPAddresses  | Format-Table -AutoSize
Write-Output('')

# Create credentials to login into the Kubernetes nodes
$password = ConvertTo-SecureString "Netapp1!" -AsPlainText -Force
$credential= New-Object System.Management.Automation.PSCredential ("root", $password)

# Variables and commands to execute on each Kubernetes nodes
$REGISTRY_NAME="docker-registry" 
$file = "tls.crt"
$destination = "/etc/docker/certs.d/'$REGISTRY_NAME':30001"
$newName = "ca.crt"
$validation = "ls -ld /etc/docker/certs.d/'$REGISTRY_NAME':30001/ca.crt"

# Executing commands and reporting back
foreach ($IPAddress in $IPAddresses) {
    $ssh=New-SSHSession -ComputerName $IPAddress -Credential $credential -AcceptKey 
    Set-SCPItem -ComputerName $IPAddress -Credential $credential -Path $file -Destination $destination -NewName $newName -AcceptKey
    $validationResult = Invoke-SSHCommand -SSHSession $ssh -Command $validation
    Write-Output($IPAddress + " result:")
    Write-Output($validationResult.Output)
    Write-Output('')
    $removeResult = Remove-SSHSession -SSHSession $ssh
}

# End
Write-Output('end')