# This script has been written for this exercise environment 
# and is not intented to be used in a production enviroment

# Install the module required
Install-Module -Name Posh-SSH -Scope CurrentUser

# Get the IPAddress for kubmas2
$IPAddress = "192.168.0.96"

# Create credentials to login into the Kubernetes node
$password = ConvertTo-SecureString "Netapp1!" -AsPlainText -Force
$credential= New-Object System.Management.Automation.PSCredential ("root", $password)

# Variables and commands to execute on each Kubernetes nodes
$file = "C:\Users\Administrator.DEMO\Desktop\CourseFiles\astra-control-center-22.08.1-26.tar.gz"
$destination = "/root"
$command1 = "tar -vxzf /root/astra-control-center-22.08.1-26.tar.gz"
$command2 = "cp /root/kubectl-astra/astra_linux_amd64 /usr/bin/kubectl-astra"
$command3 = "kubectl astra packages push-images -m /root/acc/acc.manifest.yaml -r docker-registry:30001 -u admin -p Netapp1!"
$validation = "curl https://'$IPAddress':30001/v2/_catalog --insecure --user admin:Netapp1!"

# Executing commands and reporting back

    $ssh=New-SSHSession -ComputerName $IPAddress -Credential $credential -AcceptKey 
    Set-SCPItem -ComputerName $IPAddress -Credential $credential -Path $file -Destination $destination -AcceptKey | Out-Default
    Write-Output("Starting untar")
    $commandResult1 = Invoke-SSHCommand -SSHSession $ssh -Command $command1 -TimeOut 900 | Out-Default  
    Write-Output ($commandResult1)
    Write-Output("Starting copy")
    $commandResult2 = Invoke-SSHCommand -SSHSession $ssh -Command $command2 | Out-Default  
    Write-Output ($commandResult2)
    Write-Output("Starting push images")
    $commandResult3 = Invoke-SSHCommand -SSHSession $ssh -Command $command3 -TimeOut 900 | Out-Default    
    Write-Output ($commandResult3)
    $validationResult = Invoke-SSHCommand -SSHSession $ssh -Command $validation
    Write-Output($IPAddress + " result:")
    Write-Output($validationResult.Output)
    Write-Output('')
    $removeResult = Remove-SSHSession -SSHSession $ssh


# End
Write-Output('end')