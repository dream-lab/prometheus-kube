# ESXi Setup

#### Recommended configuration
* Cores: 4+
* Memory: 8 GiB+
* HDD: 512 GiB+
* Hyperthreading disabled

## Problem
The server on which ESXi needed to be installed had a desktop-grade NIC and processor which is deemed incompatible with any version of ESXi. Possible approaches included waiting for vmware developers to release the official signed packages or change the NIC into a server-grade variant after bypassing CPU compatibility checks.

## Machine specifications (incompatible components)
- Processor: Intel i9-11900K @ 3.50GHz
- NIC: Intel(R) Ethernet Connection (14) I219-V

## Solution
The drivers for the unsupported hardware components needed to be manually bundled with a base ESXi image to create a final ISO.

[VMWare flings](https://flings.vmware.com/) is a developer maintained repository of drivers for desktop-grade hardware components that are not officially supported by VMWare releases. It houses ESXi Native Drivers which enables ESXi to recognize and consume various PCIe-based network adapters. The drivers for the aforementioned NIC was available in the [e1000-community](https://flings.vmware.com/community-networking-driver-for-esxi#requirements).

## Script
The following script can be used to create a custom ESXi image for unsupported components. Changes to package and profile names can be made (after thorough compatibility checks) to try different versions.

Open a PowerShell window in Administrator mode
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine
Install-Module -Name VMware.PowerCLI -SkipPublisherCheck
```
The above snippet installs powercli (suite of modules that help in executing commands in esxcli). Note that this needs to be executed only once per system and not every time an image is built.

Open a Powershell windows (not in Administrator mode)
```powershell
# Make powerCLI functional (in user mode)
Set-PowerCLIConfiguration -Scope User -ParticipateInCEIP $false

# Add ESXi's official image depot. This helps in listing the available profiles and images
Add-EsxSoftwareDepot https://hostupdate.vmware.com/software/VUM/PRODUCTION/main/vmw-depot-index.xml

# List the available profiles and choose one
Get-EsxImageProfile

# Download the desired ESXi image and assign it a profile name. Export it into zip format
Export-ESXImageProfile -ImageProfile "ESXi-7.0.1-16850804-standard" -ExportToBundle -filepath ESXi-7.0.1-16850804-standard.zip

# Remove the depot (not needed anymore as image is downloaded)
Remove-EsxSoftwareDepot https://hostupdate.vmware.com/software/VUM/PRODUCTION/main/vmw-depot-index.xml

# Add the downloaded default ESXi image file to the installation media
Add-EsxSoftwareDepot .\ESXi-7.0.1-16850804-standard.zip

# Download additional drivers (link attached under the "Drivers" field in references) and place it in current working directory. There are 2 drivers necessary for our use case
# 1. Community Networking Driver
# 2. USB Network Native Driver

# Add the community networking driver
Add-EsxSoftwareDepot .\Net-Community-Driver_1.2.0.0-1vmw.700.1.0.15843807_18028830.zip

# Add USB Network Native Driver
Add-EsxSoftwareDepot .\ESXi701-VMKUSB-NIC-FLING-40599856-component-17078334.zip

# Create a new, custom installation media profile
New-EsxImageProfile -CloneProfile "ESXi-7.0.1-16850804-standard" -name "ESXi-7.0.1-16850804-standard-CSL" -Vendor "saswat"

# Add community networking driver and USB Network Native driver to the newly created profile
Add-EsxSoftwarePackage -ImageProfile "ESXi-7.0.1-16850804-standard-CSL" -SoftwarePackage "net-community"
Add-EsxSoftwarePackage -ImageProfile "ESXi-7.0.1-16850804-standard-CSL" -SoftwarePackage "vmkusb-nic-fling"

# The string following the 'SoftwarePackage' flag is the same as the folder name in the vib20 folder of each driver's .zip file

# Export the installation profile to an ISO
Export-ESXImageProfile -ImageProfile "ESXi-7.0.1-16850804-standard-CSL" -ExportToIso -filepath ESXi-7.0.1-16850804-standard-CSL.iso
```
Burn the created iso file into a USB stick and boot the system from it

## Instructions while booting up
The above instructions are necessary for handling the NIC incompatbility issue. ESXi doesn't support desktop grade intel-i9 processor and a small tweak to the kernel's boot parameters is necessary to bypass the check

During the initial boot, a small delay of 5s is allowed to make kernel changes. Press "Shift+O" at this time and add the following parameter to the already available options (take extra care in spacing and spelling while doing so)
```bash
cpuUniformityHardCheckPanic=FALSE
```
Alternatively, this line can also be added to the boot.cfg file while creating the installation media

The above line will bypass the CPU uniformity check and avoid a PSOD (purple screen of death) due to the different CPU properties across both the P-Cores and E-Cores. 

## References
- [Reddit forum](https://www.reddit.com/r/vmware/comments/njaiam/problem_installing_vsphere_70_with_i219v_11_nic/gz6gp6c/)
- [vSphere ESXi Image Builder Overview](https://docs.vmware.com/en/VMware-vSphere/7.0/com.vmware.esxi.install.doc/GUID-C84C5113-3111-4A27-9096-D61EED29EF45.html)
- [Adding a Software Depot in vSphere
](https://docs.vmware.com/en/VMware-vSphere/7.0/com.vmware.esxi.install.doc/GUID-AEE9B22B-6D97-4875-8593-FBE6992D9E28.html)
- [William's blog on using vCentre's auto deploy feature](https://williamlam.com/2021/03/easily-create-custom-esxi-images-from-patch-releases-using-vsphere-image-builder-ui.html)
- Drivers
    -  [USB Network Native Driver](https://flings.vmware.com/usb-network-native-driver-for-esxi)
    -  [Community Networking Driver](https://flings.vmware.com/community-networking-driver-for-esxi)
- [Guide on creating custom ESXi bundles](https://www.virten.net/2020/04/how-to-add-the-usb-nic-fling-to-esxi-7-0-base-image/)

### VM Configuration
* Download CentOS 7 iso from [here](http://isoredirect.centos.org/centos/7/isos/x86_64/)
* Copy the above iso file into the attached datastore
* Create a new virtual machine from ESXi console
* Set the Guest OS family and version to "Linux" and "Centos 7 (64-bit)" respectively
* Select the default datastore for mounting the filestore
* Set number of CPUs to 2 (2 per socket)
* Under the CPU tab, check "Expose hardware assisted virtualization to the guest OS" and "Enable virtualized CPU performance counters"
* Set scheduling affinity to cores other than 0 and 1 as most system calls are preferably sreviced by these cores. Set the field to 4,5 or 2,3.
* Assign 4096MB of memory (uncheck dynamic memory allocation)
* Check on "Reserve all guest memory (All locked)"
* Change "CD/DVD Drive 1" to "Datastore ISO file". Select the iso that was previously copied (step 2)
* Finish the VM creation process

### OS Installation
* Choose the newly installed virtual machine and install the OS
* Set correct timezone (**very important for prometheus to sync**)
* Set software selection to **Compute Node**
* Disable kdump
* Connect network to the default ethernet