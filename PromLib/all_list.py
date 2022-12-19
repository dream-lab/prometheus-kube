import yaml
import requests

with open("config.yaml", 'r') as stream:
    config = yaml.safe_load(stream)

prometheus = "http://" + config['prometheus_source'] + "/"

def get_all_machine_id():
    query = 'group by (instance,job) (node_load5!=0)'
    # print(query)
    response = requests.get(prometheus + '/api/v1/query', params={
        'query': query})
    results = response.json()['data']['result']
    #print(results)
    machine_list=[]
    for i in results:
        if i['metric']['job']== 'Kubernetes VMs GPU nodes':
            machine_list.append(i['metric']['instance'])
    #print(machine_list)
    return machine_list

def get_all_app_list():
    query ='group by (container_label_io_kompose_service)( container_tasks_state{container_label_io_kompose_service!~""})'
    #print(query_temp)
    response = requests.get(prometheus + '/api/v1/query', params={
            'query': query})
    #print(response.json())
    results = response.json()['data']['result']
    # print(results)
    app_list=[]
    for idx in results:
            pod=idx['metric']['container_label_io_kompose_service']
            app_list.append(pod)
    return app_list
