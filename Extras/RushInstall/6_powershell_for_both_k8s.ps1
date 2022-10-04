

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
$command = "mpathconf --enable; sudo systemctl restart iscsid multipathd"
$validation = " sudo systemctl status iscsid multpathd"

$REGISTRY_NAME="docker-registry"
$REGISTRY_IP="192.168.0.96"  
$command2 = "echo '$REGISTRY_IP $REGISTRY_NAME' >> /etc/hosts"
$validation2 = "cat /etc/hosts"

$command3 = "rm -rf /etc/docker/certs.d/'$REGISTRY_NAME':30001;mkdir -p /etc/docker/certs.d/'$REGISTRY_NAME':30001"
$validation3 = "ls -ld /etc/docker/certs.d/'$REGISTRY_NAME':30001"

$file = "tls.crt"
$destination = "/etc/docker/certs.d/'$REGISTRY_NAME':30001"
$newName = "ca.crt"
$validation4 = "ls -ld /etc/docker/certs.d/'$REGISTRY_NAME':30001/ca.crt"

# Executing commands and reporting back
foreach ($IPAddress in $IPAddresses) {
    $ssh=New-SSHSession -ComputerName $IPAddress -Credential $credential -AcceptKey 

    $commandResult = Invoke-SSHCommand -SSHSession $ssh -Command $command
    $validationResult = Invoke-SSHCommand -SSHSession $ssh -Command $validation
    Write-Output($IPAddress + " result:")
    Write-Output($validationResult.Output)
    Write-Output('')

    $commandResult2 = Invoke-SSHCommand -SSHSession $ssh -Command $command2
    $validationResult2 = Invoke-SSHCommand -SSHSession $ssh -Command $validation2
    Write-Output($IPAddress + " result:")
    Write-Output($validationResult2.Output)
    Write-Output('')

    $commandResult3 = Invoke-SSHCommand -SSHSession $ssh -Command $command3
    $validationResult3 = Invoke-SSHCommand -SSHSession $ssh -Command $validation3
    Write-Output($IPAddress + " result:")
    Write-Output($validationResult3.Output)
    Write-Output('')

    Set-SCPItem -ComputerName $IPAddress -Credential $credential -Path $file -Destination $destination -NewName $newName -AcceptKey
    $validationResult4 = Invoke-SSHCommand -SSHSession $ssh -Command $validation4
    Write-Output($IPAddress + " result:")
    Write-Output($validationResult4.Output)
    Write-Output('')

    $removeResult = Remove-SSHSession -SSHSession $ssh


}

# End
Write-Output('end')

