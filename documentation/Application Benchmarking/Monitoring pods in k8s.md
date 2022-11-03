# Monitoring Kubernetes pods

The two important modules to get pod level metrics exported into prometheus database from Kubernetes pods are:
1) Kubestate metrics
2) Cadvisor

We need to setup each of these services on the worker nodes to get info of all the pods running on them.

## Kube-state-metrics setup (optional)

Run the below steps on the control plane to deploy kube-state-metrics as NodePort service (to make service discoverable outside the cluster):
  
    git clone https://github.com/ArjunKini2011/kube-state-metrics.git
    kubectl apply -f kube-state-metrics/examples/standard/.
    
To check if its up and running, check status from:
    
    kubectl get pods -n kube-system 
   

## cAdvisor

Make sure GO lang is installed else follow steps at:

> https://www.digitalocean.com/community/tutorials/how-to-install-go-on-ubuntu-20-04

Next install kustomize using GO source.


    GOBIN=$(pwd)/ GO111MODULE=on go get sigs.k8s.io/kustomize/kustomize/v4
    unset GOPATH
    unset GO111MODULES

    git clone git@github.com:kubernetes-sigs/kustomize.git
    cd kustomize


    git checkout kustomize/v4.5.2


    (cd kustomize; go install .)

    ~/go/bin/kustomize version

Alternatively use:

    curl -s "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh"  | bash


Now clone cadvisor repo and enter kubernetes directory:

    git clone https://github.com/google/cadvisor.git
    cd cadvisor

Now to make cadvisor service discoverable outside the k8s cluster follow these commands:
    
    cd deploy/kubernetes/overlays/examples_perf
    sudo vi  cadvisor-perf.yaml
    
Inside spec add a host network true command as follows:
    
    spec:
      template:
         spec:
            hostNetwork: true

   
Now apply following commands to setup cadvisor on all worker nodes:
    
    VERSION=v0.42.0
    cd deploy/kubernetes/base && kustomize edit set image gcr.io/cadvisor/cadvisor:${VERSION} && cd ../../..
    kubectl kustomize deploy/kubernetes/overlays/examples_perf
    kubectl kustomize deploy/kubernetes/overlays/examples_perf | kubectl apply -f -

Check status of pods using:

    kubectl get pods -n cadvisor


Once all pods are running open the the prometheus.yaml config file and add job config as follows:

  ````yaml
  - job_name: 'cadvisor'
    honor_timestamps: true
    scrape_interval: 5s
    scrape_timeout: 5s
    static_configs:
      - targets: ['192.168.0.47:8080','192.168.0.48:8080','192.168.0.49:8080','192.168.0.50:8080','192.168.0.51:8080','192.168.0.52:8080','192.168.0.53:8080','192.168.0.54:8080']
        labels:
           alias: 'cadvisor'
   ````
Lastly inside grafana add a newdashboard by going into 'Import' followed by new dashboard then upload the json file or copy the contents from the json file in the binaries repo.
