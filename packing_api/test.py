import yaml
import promlib
import numpy as np

with open("hosts.yaml", 'r') as stream:
    host_list = yaml.safe_load(stream)

with open("config.yaml", 'r') as stream:
    config = yaml.safe_load(stream)

hosts = host_list['host_list']
print(hosts)

# app_list = ["cadvisor-n9w5s","etcd-minikube","kube-state-metrics-6654dd6bb-sbw8k"] #pod id
app_list = ["calico-node-54m5q:kube-system"]

# print(promlib.machine_total(hosts))
# print(promlib.machine_current(hosts))
# print(promlib.machine_average(hosts))

# print(promlib.application_average(app_list))

# machine_capacity = np.array(promlib.machine_total(hosts))
# machine_usage = np.array(promlib.machine_total(hosts)) - np.array(promlib.machine_average(hosts))
# machine_avail = np.floor((machine_capacity - machine_usage) * float(config['MAX_AVAIL'])).astype(int)

# machine_avail_avg = np.floor(np.array(promlib.machine_average(hosts)) * float(config['MAX_AVAIL'])).astype(int)
# container_req_avg = np.ceil(promlib.application_average(app_list)).astype(int)
# print(machine_avail)

import requests
query_apps = []
for app in app_list:
    query_apps.append('app_list='+app)

query = "&".join([qapp for qapp in query_apps])

url = 'http://10.16.70.242:8000/get_placement_vp?'+query
response = requests.get(url)
# print(response.text)

for key, value in response.items():
    print(key, value)
