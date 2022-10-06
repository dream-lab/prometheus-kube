# Deathstar Benchmark tutorial

First install luarocks and luasockets:
    
    apt-get install luarocks
    luarocks install luasocket
    
Now clone the Deathstar benchmark github repo

    git clone https://github.com/delimitrou/DeathStarBench.git
    
Create the local images using:

    sudo bash <path-of-DeathStarBench>/hotelReservation/kubernetes/scripts/build-docker-images.sh

If you run into some docker issues, replace the contents of the build-docker-images.sh file with this:

    #!/bin/bash
  
    cd $(dirname $0)/..


    EXEC=docker

    USER="salehsedghpour"

    TAG="latest"

    # ENTER THE ROOT FOLDER
    cd ../
    ROOT_FOLDER=$(pwd)

    for i in frontend geo profile rate recommendation reserve search user
    do
      IMAGE=hotel_reserv_${i}_single_node
      echo Processing image ${IMAGE}
      cd $ROOT_FOLDER
      $EXEC build -t "$USER"/"$IMAGE":"$TAG" -f Dockerfile .
      $EXEC push "$USER"/"$IMAGE":"$TAG"
      cd $ROOT_FOLDER

      echo
    done


    cd - >/dev/null
    
Now deploy services using
    
    kubectl apply -Rf <path-of-DeathStarBench>/hotelReservation/kubernetes/
    
  ***Note that this creates pods in default namespace***
  
Wait until all services are running which can be checked using:

    kubectl get pods
    
Once all pods are running, check for the port on which the frontend service is running using:

    kubectl get svc
 
By default the service runs on port 5000. Now port-forward the service to be accesible via http using:
    
    kubectl port-forward svc/frontend 5000
 
 It should show:
 
     Forwarding from 127.0.0.1:5000 -> 5000
     Forwarding from [::1]:5000 -> 5000
     
 Next open another terminal in the system.
 We need to make a small change int he mixec workload script for wrk2 as the code in repo by default gives some error.
 
     cd <path-of-DeathStarBench>/hotelReservation/wrk2/scripts/hotel-reservation/
     sudo vi mixed-workload_type_1.lua 

Change the line
``` python 
local socket = require("socket")
```
to
```python
socket = require("socket") 
```

Modify mixed-workload script as per need.

Save the changes. Now we can run the benchmark using:

    cd <path-of-repo>/hotelReservation
    ./wrk2/wrk -D exp -t <num-threads> -c <num-conns> -d <duration> -L -s ./wrk2/scripts/hotel-reservation/mixed-workload_type_1.lua http://localhost:5000 -R <reqs-per-sec>

Example:
      
     ./wrk2/wrk -D exp -t 2 -c 10 -d <duration> -L -s ./wrk2/scripts/hotel-reservation/mixed-workload_type_1.lua http://localhost:5000 -R 2000

This runs benchmark with 2 threads keeping 10 connections open generating a cumulative 2000 requests/sec.

 
    
