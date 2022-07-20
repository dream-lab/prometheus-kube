##  Kubernetes cluster setup ##

A comprehensive step by step K8s cluster setup can be found here:

> https://devopscube.com/setup-kubernetes-cluster-kubeadm/

Simply follow the steps.

When adding workers, you might receive an error that looks like:

    [ERROR CRI]: container runtime is not running

To resolve this enter:
    
    sudo rm /etc/containerd/config.toml
    sudo systemctl restart containerd
    sudo kubeadm init
    
The re enter the join command. 

## Basic Kubernetes commands ##

Initially, when we do kubectl get nodes, the roles for the worker nodes will be shown as <none>. To change role to <worker>:
  
    kubectl label node <node-name> node-role.kubernetes.io/worker=worker
  
 To get a list of all pods across all namespaces:
      
      kubectl get pods --all-namespaces
  
 To get list of pods in a given namespace:
      
      kubectl get pods -n <namespace>
  
 To get a Worker-wise list of all pods scheduled across the nodes:
  
      kubectl get pod -o=custom-columns=NODE:.spec.nodeName,NAME:.metadata.name -n <namespace>
  
  We can get pods on a particular node using :
  
      kubectl get pod -o=custom-columns=NODE:.spec.nodeName,NAME:.metadata.name -n <namespace> | grep <node-name>
  
  To get list of services with their cluster-IP/ nodeports:
  
      kubectl get svc -n <namespace>
  
  To avoid scheduling of pods on a particular node, add a taint using:
  
      kubectl taint node <node-name> key1=value1:NoSchedule
  
  To remove taint
  
      kubectl taint node <node-name> key1=value1:NoSchedule-

  
  By default, no pods are scheduled on master/ control-plane node. To avoid this, use above command to remove taint from control-plane node. (Not recommended)
