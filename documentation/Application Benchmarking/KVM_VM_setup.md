# Run these commands to install ubuntu in headless server with netboot image

## Download ISO

Download non live server iso (non live is important for tty0 console functionality)

    wget http://cdimage.ubuntu.com/ubuntu/releases/18.04/release/ubuntu-18.04.6-server-amd64.iso


## Bridge

Follow steps at: 

    https://linuxconfig.org/how-to-use-bridged-networking-with-libvirt-and-kvm

If br0 already present on worker node just follow the "Creating a new virtual network" steps.

## KVM Setup

    sudo apt -y install bridge-utils cpu-checker libvirt-clients libvirt-daemon qemu qemu-kvm


## Installation with ubuntu server iso 18:

Here we setup a VM with 8GB ram and 4 vCPUs. The parameters are pretty self explanatory and can be modified as per needs.    
    
    sudo virt-install \
    --name=vm_name \
    --memory=8192 \
    --vcpus=4 \
    --location=/var/lib/libvirt/boot/ubuntu-18.04.6-server-amd64.iso \
    --disk /var/lib/libvirt/images/vm_name.qcow2,device=disk,bus=virtio,size=50 \
    --network network:bridged-network \
    --os-type=linux  \
    --graphics none \
    --extra-args='console=tty0 console=ttyS0,115200n8 serial'


After this it will give a network error.

Select manual network setup

Assign an ip in 192.168.0.x

Mask : 255.255.255.0

Gateway : 192.168.0.10

Name server : find in /etc/resolv.conf 

***Note: IPs can be modified as per need.***


Use arrows to navigate, tab to switch options, spacebar to select options.

Select OpenSSH and Basic Ubuntu in extra tools. (Important)

After installation completes, pres Ctrl+Shift+] to exit.

## Final Steps

    sudo virsh destroy vm-name
    sudo virsh start vm-name

To get the mac address:

    sudo virsh domiflist vm-name 
    
To get ip address:    
    
    arp -an | grep mac-address 
    
Login using ssh username@ip




