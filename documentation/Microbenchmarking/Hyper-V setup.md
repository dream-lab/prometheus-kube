### Hyper-V Setup

#### Recommended configuration
* OS: Windows 10
* Cores: 4+
* Memory: 8 GiB+
* HDD: 512 GiB+
* Hyperthreading disabled

#### Installation steps
Hyper-V is not enabled by default in recent windows builds. We need to enable it manually via powershell. Open a PowerShell console and run the following command
```powershell
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
```

We have to virtualise the performance counters and forward them into the virtual machine. Open a Powershell console and run the following command
```powershell
Set-VMProcessor MyVMName -Perfmon @("pmu")
```

### Hyper-V Configuration
We need to create an external software-enabled switch which will then be attached to the VMs that are spun on Hyper-V. To do so, open a Powershell console and run the following command
```powershell
Get-NetAdapter # Note the network adapter name in the above list

New-VMSwitch -name ExternalSwitch  -NetAdapterName <Name of the adapter> -AllowManagementOS $true
```

### VM Configuration
* Download CentOS 7 iso from [here](http://isoredirect.centos.org/centos/7/isos/x86_64/)
* Create a new virtual machine from hyper-v manager
* Set the generation of the VM as 1
* Assign 4096MB of memory (uncheck dynamic memory allocation)
* Select the newly created virtual switch as the preferred networking option
* Connect a new virtual disk with atleast 100G capacity
* Select the previously downloaded iso to boot/install from

### OS Installation
* Choose the newly installed virtual machine and install the OS
* Set correct timezone (**very important for prometheus to sync**)
* Set software selection to **Compute Node**
* Disable kdump
* Connect network to the default ethernet