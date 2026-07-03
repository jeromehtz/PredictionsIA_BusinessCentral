#Activer Hyper V
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All

Enable-WindowsOptionalFeature -Online -FeatureName $("Microsoft-Hyper-V", "Containers") -All


Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
Install-Module -Name BcContainerHelper -Force

Import-Module BcContainerHelper -Verbose


$credential = Get-Credential


#version 26
$ServerName = 'bc26fr'    
$artifactUrl = Get-BCArtifactUrl -type OnPrem -select Latest -country fr
New-BcContainer `
    -containerName 'bc26-6080' `
    -imageName 'businesscentral:ltsc2025' `
    -accept_eula `
    -artifactUrl (Get-BcArtifactUrl `
      -type Sandbox `
      -country fr `
      -version 26.0) `
    -auth UserPassword `
    -Credential (Get-Credential) `
    -updateHosts `
    -includeAL `
    -assignPremiumPlan `
    -assignPorts `
    -isolation hyperv `
    -shortcuts Desktop `
    -includeTestToolkit `
    -additionalParameters @(
      "--publish 8081:80",           # Web client
      "--publish 6443:443",          # HTTPS
      "--publish 7046-7049:7046-7049"
    )
   
Get-BcContainerWebClientUrl -containerName $ServerName
Uninstall-Module BcContainerHelper -Force -AllVersions
Install-Module BcContainerHelper -Force
Import-Module BcContainerHelper



#Controle
Get-NAVServerLicenseInformation -ServerInstance BC260

Enter-BcContainer -containerName bc260
Open-BcContainer -containerName BC260

Invoke-ScriptInBcContainer -containerName bc260fr -scriptBlock {
    Import-Module 'C:\Program Files\Microsoft Dynamics 365 Business Central\240\Service\Microsoft.Dynamics.Nav.Management.psm1'
    Get-NAVServerLicenseInformation -ServerInstance BC
}

Docker images
dcker ps
docker ps -a #Liste les conteneurs arrêtés
docker start nom_du_conteneur
docker rm nom_du_conteneur #supprime


//NAV 2016
Get-NavContainer -containerName "bc160fr"

docker exec -it bc160fr powershell
cd "C:\Program Files (x86)\Microsoft Dynamics 365 Business Central\90\RoleTailored Client"
.\finsql.exe


$containerName = "bc160Fr"
$localFobPath = "C:\BCAL\DUAP V9.fob"
$containerFobPath = "c:\run\DUAP.fob"

Copy-FileToBcContainer -containerName $containerName -localPath $localFobPath -containerPath $containerFobPath
Import-ObjectsToNavContainer -objectsFile $containerFobPath -containerName $containerName -ImportAction Overwrite

Get-BcContainerEventLog -containerName bc260Fr to retrieve a snapshot of the event log from the container
Get-BcContainerDebugInfo -containerName bc260Fr to get debug information about the container
Open-BcContainer -containerName bc260Fr to open a PowerShell prompt inside the container
Enter-BcContainer -containerName bc260Fr to open a PowerShell prompt inside the container
Remove-BcContainer -containerName bc260Fr to remove the container again
docker logs bc260Fr to retrieve information about URL's again