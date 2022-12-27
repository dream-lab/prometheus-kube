from fastapi import FastAPI, HTTPException, Query
import numpy as np
from typing import List
from vpsolv import VpSolver
from rl import rl_pack

import yaml
import promlib
from collections import defaultdict

with open("hosts.yaml", 'r') as stream:
    host_list = yaml.safe_load(stream)

with open("config.yaml", 'r') as stream:
    config = yaml.safe_load(stream)

# app_list = ["cadvisor-n9w5s","etcd-minikube","kube-state-metrics-6654dd6bb-sbw8k"] #pod id


description = """
<img id="image" src="https://iisc.ac.in/wp-content/uploads/2020/08/IISc_Master_Seal_Black.jpg" height="100" width="100" >


This API helps you get intelligent placement decisions using various placement algorithms. 🚀
Currently Supported Algorithms:
* VpSolver
"""

tags_metadata = [
    {
        "name": "hello",
        "description": "Testing the server.",
    },
    {
        "name": "get_placement_vp",
        "description": "API to get placement mappings using _VPSolver_ algorithm."

    },
    {
        "name": "get_placement_ml",
        "description": "API to get placement mappings using _ML_."

    },
]


app = FastAPI(
    title="Intelligent Scheduler",
    description=description,
    version="1.0.0",
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    openapi_tags=tags_metadata,
    docs_url="/"
)


@app.get('/hello', tags=["hello"])
def hello():
    return {"Hello": "World"}



@app.get('/get_placement_vp', tags=["get_placement_vp"])
def get_placement_vp(app_list: list = Query(default=[])):

    '''
        This API gives placement using **VPSolver** algorithm.

        - **Input:** List of app ids
        - **Output:** Generated mappings between apps and hosts 
        
        ### BOILER PLATE CODE TO USE THE API ###

        ```
            # Assumed application ids to be placed
            apps_list = ['app1', 'app2', 'app3'] 

            query_apps = []
            for app in apps_list:
                query_apps.append('app_list='+app)

            query = "&".join([qapp for qapp in query_apps])

            url = 'http://x.x.x.x:port/get_placement_vp?'+query
            response = requests.get(url).json()

            print(response)

        ```
    '''

    if len(app_list) == 0:
        raise HTTPException(status_code=404, detail="App List Cannot be empty")

    hosts = host_list['host_list']

    if len(hosts) == 0:
        raise HTTPException(status_code=404, detail="No hosts present")
    # machines, containers = None, None
    # try:
    machine_capacity = np.array(promlib.machine_total(hosts))
    machine_usage = np.array(promlib.machine_total(hosts)) - np.array(promlib.machine_average(hosts))
    machine_avail = np.floor((machine_capacity - machine_usage) * float(config['MAX_AVAIL'])).astype(int)
    # machine_avail = np.floor(np.array(promlib.machine_average(hosts)))

    containers = np.ceil(promlib.application_quantile(app_list)).astype(int)
    print(machine_avail, containers)
        # print(machine_avail, containers)

        # containers = [[1,1,1,1]]
    # # print(machine_avail, hosts, containers, app_list)
        
    # except Exception as e:
    #     # print(e)
    #     raise HTTPException(status_code=500, detail="Internal Server Error!")

    # machine_avail = np.array([[10,20,30,40], [50,100,200,300], [25,35,40,50]])
    # hosts = ['m1', 'm2', 'm3']
    # containers = np.array([[5,5,10,10], [30,50,20,20], [5,10,15,20], [15,25,20,30]])
    # app_list = ['c1', 'c2', 'c3', 'c4']
    # app_list = ['catalogue-db', 'carts-db', 'front-end', 'istio-gateway']
    
    # Mapping is a dictionary
    mappings = VpSolver(machine_avail, hosts, containers, app_list)

    reverse_mappings = defaultdict(list)
    for k, v in mappings.items():
        reverse_mappings[v.split(':')[0]].append(k.split(':')[1])

    print("MAPP=",reverse_mappings)
    if 'ERROR' in mappings:
        raise HTTPException(status_code=404, detail=mappings['ERROR'])

    logs = []
    for k, v in reverse_mappings.items():
        logs.append(promlib.deploy(k, v, 'deathstar-deploy'))
    
    return {'mappings' : reverse_mappings, 'command': '\n'.join(logs)}


@app.get('/get_placement_rl', tags=["get_placement_ml"])
def get_placement_vp(app_list: list = Query(default=[])):

    '''
        This API gives placement using **RL** algorithm.

        - **Input:** List of app ids
        - **Output:** Generated mappings between apps and hosts 
        
        ### BOILER PLATE CODE TO USE THE API ###

        ```
            # Assumed application ids to be placed
            apps_list = ['app1', 'app2', 'app3'] 

            query_apps = []
            for app in apps_list:
                query_apps.append('app_list='+app)

            query = "&".join([qapp for qapp in query_apps])

            url = 'http://x.x.x.x:port/get_placement_vp?'+query
            response = requests.get(url).json()

            print(response)

        ```
    '''

    if len(app_list) == 0:
        raise HTTPException(status_code=404, detail="App List Cannot be empty")

    hosts = host_list['host_list']

    if len(hosts) == 0:
        raise HTTPException(status_code=404, detail="No hosts present")
    machines, containers = None, None
    try:
        machine_capacity = np.array(promlib.machine_total(hosts))
        machine_usage = np.array(promlib.machine_total(hosts)) - np.array(promlib.machine_average(hosts))
        machine_avail = np.floor((machine_capacity - machine_usage) * float(config['MAX_AVAIL'])).astype(int)
        # machine_avail = np.floor(np.array(promlib.machine_average(hosts)))

        containers = np.ceil(promlib.application_quantile(app_list)).astype(int)
        print(machine_avail, containers)
        print(machine_avail, containers)

        # containers = [[1,1,1,1]]
        # print(machine_avail, hosts, containers, app_list)
        
    except Exception as e:
        # print(e)
        raise HTTPException(status_code=500, detail="Internal Server Error!")

    # hosts = ['m1', 'm2', 'm3']
    # containers = np.array([[1,2,10,10], [2,1,2,2], [5,10,15,20], [4,8,20,30]])
    # app_list = ['c1', 'c2', 'c3', 'c4']
    # app_list = ['catalogue-db', 'carts-db', 'front-end', 'istio-gateway']
    
    # Mapping is a dictionary
    mappings = rl_pack(machine_avail, hosts, containers, app_list)


    reverse_mappings = defaultdict(list)
    for k, v in mappings.items():
        reverse_mappings[v.split(':')[0]].append(k.split(':')[1])

    print("MAPP=",reverse_mappings)
    if 'ERROR' in mappings:
        raise HTTPException(status_code=404, detail=mappings['ERROR'])

    logs = []
    for k, v in reverse_mappings.items():
        logs.append(promlib.deploy(k, v, 'deathstar-deploy'))
    
    return {'mappings' : reverse_mappings, 'command': '\n'.join(logs)}

