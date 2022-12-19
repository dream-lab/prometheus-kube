import yaml
import requests
import paramiko as pk
import subprocess as sp
import os
import re




with open("config.yaml", 'r') as stream:
    config = yaml.safe_load(stream)

prometheus = "http://" + config['prometheus_source'] + "/"
machine_window = config['machine_window']
app_scrape_interval=config['app_scrape_interval']
rate_interval=str(4*int(app_scrape_interval[:len(app_scrape_interval)-1])) + 's'
application_window =config['application_window']
app_metric_percentile=config['app_metric_percentile']

def machine_total(hosts):

    def cpu(host):
        host_node = '"' + host + '"'
        query = 'count(count(node_cpu_seconds_total{{ instance={} }}) by (cpu))'.format(host_node)
        # print(query)
        response = requests.get(prometheus + '/api/v1/query', params={
            'query': query})
        #print(response.json())
        results = response.json()['data']['result']
        cores = float(results[0]['value'][1])
        return cores

    def memory(host):
        host_node = '"' + host + '"'
        query = ' node_memory_MemTotal_bytes{{ instance={}  }} / (1024^3)'.format(host_node)
        # print(query)
        response = requests.get(prometheus + '/api/v1/query', params={
            'query': query})
        # print(response.json())
        results = response.json()['data']['result']
        mem = float(results[0]['value'][1])
        return mem

    def disk(host):
        host_node = '"' + host + '"'
        query = 'sum(node_filesystem_size_bytes{{ instance={},device!~"rootfs" }}) / (1024^3)'.format(
            host_node)
        # print(query)
        response = requests.get(prometheus + '/api/v1/query', params={
            'query': query})
        # print(response.json())
        results = response.json()['data']['result']
        space = float(results[0]['value'][1])
        return space

    def network(host):
        host_node = '"' + host + '"'
        query = 'node_network_speed_bytes{{ instance={} }} * 8/(10^9)'.format(host_node)
        # print(query)
        response = requests.get(prometheus + '/api/v1/query', params={
            'query': query})
        # print(response.json())
        results = response.json()['data']['result']
        speed = []
        for result in results:
            speed.append(float(result['value'][1]))
        return float(max(speed))

    result=[]
    for host in hosts:
        result.append((cpu(host), memory(host), disk(host), network(host)))

    return result


def machine_current(hosts):

    def cpu(host):
        host_node = '"' + host + '"'
        query = '100 - 100 * avg by (instance) (irate(node_cpu_seconds_total{{ mode="idle",instance={} }} [1m]))'.format(
            host_node)
        # print(query)
        response = requests.get(prometheus + '/api/v1/query', params={
            'query': query})
        # print(response.json())
        results = response.json()['data']['result']
        # print(float(results[0]['value'][1]))
        total_cpu=machine_total([host])[0][0]
        cpu_use = total_cpu - ((float(results[0]['value'][1]) * total_cpu) / 100)
        return cpu_use

    def memory(host):
        host_node = '"' + host + '"'
        query = ' node_memory_MemAvailable_bytes{{ instance={}  }} / (1024^3)'.format(host_node)
        # print(query)
        response = requests.get(prometheus + '/api/v1/query', params={
            'query': query})
        # print(response.json())
        results = response.json()['data']['result']
        mem = float(results[0]['value'][1])
        return mem

    def disk(host):
        host_node = '"' + host + '"'
        query = 'sum(node_filesystem_avail_bytes{{ instance={},device!~"rootfs" }})/ (1024^3)'.format(
            host_node)
        # print(query)
        response = requests.get(prometheus + '/api/v1/query', params={
            'query': query})
        # print(response.json())
        results = response.json()['data']['result']
        space = float(results[0]['value'][1])
        return space

    def network(host):
        host_node = '"' + host + '"'
        query = '(irate(node_network_receive_bytes_total{{ instance={},device!="lo" }}[1m])' \
                '+ irate(node_network_transmit_bytes_total{{ instance={},device!="lo" }}[1m])) *8/ (10^9)'.format(
            host_node, host_node)
        # print(query)
        response = requests.get(prometheus + '/api/v1/query', params={
            'query': query})
        # print(response.json())
        results = response.json()['data']['result']
        speed = []
        for result in results:
            speed.append(float(result['value'][1]))
        total_net=float(machine_total([host])[0][3])
        return  total_net - float(max(speed))

    result=[]
    for host in hosts:
        result.append((cpu(host), memory(host), disk(host), network(host)))

    return result



def machine_average(hosts):

    def cpu(host):
        host_node = '"' + host + '"'
        query = '(1 - avg(rate(node_cpu_seconds_total{{ mode="idle",instance={} }} [{}])) by ( instance )) *100'.format(
            host_node, machine_window)
        # print(query)
        response = requests.get(prometheus + '/api/v1/query', params={
            'query': query})
        # print(response.json())
        results = response.json()['data']['result']
        # print(float(results[0]['value'][1]))
        total_cpu=machine_total([host])[0][0]
        cpu_use = total_cpu - ((float(results[0]['value'][1]) * total_cpu) / 100)
        return cpu_use

    def memory(host):
        host_node = '"' + host + '"'
        query = ' sum(avg_over_time(node_memory_MemAvailable_bytes{{ instance={}  }}[{}]) /(1024^3))'.format(
            host_node, machine_window)
        # print(query)
        response = requests.get(prometheus + '/api/v1/query', params={
            'query': query})
        # print(response.json())
        results = response.json()['data']['result']
        mem = float(results[0]['value'][1])
        return mem

    def disk(host):
        host_node = '"' + host + '"'
        query = 'sum(avg_over_time(node_filesystem_avail_bytes{{ instance={},device!~"rootfs" }}[{}])) /(1024^3)'.format(
            host_node, machine_window)
        # print(query)
        response = requests.get(prometheus + '/api/v1/query', params={
            'query': query})
        # print(response.json())
        results = response.json()['data']['result']
        space = float(results[0]['value'][1])
        return space

    def network(host):
        host_node = '"' + host + '"'
        query = '(avg by (device) (rate(node_network_receive_bytes_total{{ instance={},device!="lo" }} [{}]))' \
                '+ avg by (device) (rate(node_network_transmit_bytes_total{{ instance={},device!="lo" }} [{}])))* 8 /(10^9)'.format(
            host_node,machine_window, host_node,machine_window)
        #print(query)
        response = requests.get(prometheus + '/api/v1/query', params={
            'query': query})
        #print(response.json())
        results = response.json()['data']['result']
        speed = []
        for result in results:
            speed.append(float(result['value'][1]))
        total_net=float(machine_total([host])[0][3])
        return  total_net - float(max(speed))

    result=[]
    for host in hosts:
        result.append((cpu(host), memory(host), disk(host), network(host)))

    return result

def application_average(app_list):

    def cpu(pod):
        query='quantile_over_time( {}, sum by (container_label_io_kubernetes_pod_name)' \
              ' (rate(container_cpu_usage_seconds_total{{ container_label_io_kubernetes_pod_name={} }}[{}]))[{}:])'\
            .format(app_metric_percentile,pod,rate_interval,application_window)
        #print(query)
        response = requests.get(prometheus + '/api/v1/query', params={
            'query': query})
        #print(response.json())
        results = response.json()['data']['result']
        cpu_use=float(results[0]['value'][1])
        return cpu_use

    def memory(pod):
        query='quantile_over_time( {} , sum by (container_label_io_kubernetes_pod_name) ' \
              '(avg_over_time(container_memory_working_set_bytes{{ container_label_io_kubernetes_pod_name={} }}[{}]))[{}:]) /(1024^3)'.\
            format(app_metric_percentile,pod,rate_interval,application_window)
        #print(query)
        response = requests.get(prometheus + '/api/v1/query', params={
            'query': query})
        #print(response.json())
        results = response.json()['data']['result']
        memory_use=float(results[0]['value'][1])
        return memory_use

    def disk(pod):
        query='quantile_over_time( {} , sum by (container_label_io_kubernetes_pod_name) ' \
              '(avg_over_time(container_fs_usage_bytes{{ container_label_io_kubernetes_pod_name={} }}[{}]))[{}:]) /(1024^3)'.\
            format(app_metric_percentile,pod,rate_interval,application_window)
        response = requests.get(prometheus + '/api/v1/query', params={
            'query': query})
        # print(response.json())
        results = response.json()['data']['result']
        disk_use = float(results[0]['value'][1])
        return disk_use
    def network(pod):
        query='((quantile_over_time( {}, sum by (container_label_io_kubernetes_pod_name)' \
              ' (rate(container_network_receive_bytes_total{{ container_label_io_kubernetes_pod_name={},interface=~"eth0|ens.*" }}[{}]))[{}:]))' \
              '+ (quantile_over_time( {}, sum by (container_label_io_kubernetes_pod_name)' \
              '(rate(container_network_transmit_bytes_total{{ container_label_io_kubernetes_pod_name={},interface=~"eth0|ens.*" }}[{}]))[{}:]))) *8/(10^9)'\
            .format(app_metric_percentile,pod,rate_interval,application_window,app_metric_percentile,pod,rate_interval,application_window)
        #print(query)
        response = requests.get(prometheus + '/api/v1/query', params={
            'query': query})
        #print(response.json())
        results = response.json()['data']['result']
        network_use=float(results[0]['value'][1])
        return network_use

    result=[]
    for id in app_list:

        cpu_use = 0
        memory_use = 0
        disk_use = 0
        network_use = 0

        namespace,app=id.split(":")
        namespace="'" + namespace + "'"
        app="'" + app + "'"
        query_temp='group by (container_label_io_kubernetes_pod_name) (container_tasks_state{{ container_label_io_kubernetes_pod_namespace={},' \
                   'container_label_io_kompose_service={} }})'.format(namespace,app)
        #print(query_temp)
        response = requests.get(prometheus + '/api/v1/query', params={
            'query': query_temp})
        #print(response.json())
        results = response.json()['data']['result']
        #print(results)
        for idx in results:
            pod=idx['metric']['container_label_io_kubernetes_pod_name']
            #print(pod)
            pod="'" + pod + "'"
            cpu_use+=cpu(pod)
            memory_use+=memory(pod)
            disk_use+=disk(pod)
            network_use+=network(pod)
        result.append((cpu_use,memory_use,disk_use,network_use))
    return result

def application_average(app_list):
    def cpu(pod):
        query = 'sum(avg by(cpu)  (rate(container_cpu_usage_seconds_total{{ container_label_io_kubernetes_pod_name={} }}[{}])))'.format(
            pod, application_window)
        # print(query)
        response = requests.get(prometheus + '/api/v1/query', params={
            'query': query})
        # print(response.json())
        results = response.json()['data']['result']
        cpu_use = float(results[0]['value'][1])
        return cpu_use

    def memory(pod):
        query = 'sum(avg_over_time(container_memory_working_set_bytes{{ container_label_io_kubernetes_pod_name={} }}[{}]))/(1024^3)'.format(
            pod, application_window)
        # print(query)
        response = requests.get(prometheus + '/api/v1/query', params={
            'query': query})
        # print(response.json())
        results = response.json()['data']['result']
        memory_use = float(results[0]['value'][1])
        return memory_use

    def disk(pod):
        query = 'sum(avg_over_time(container_fs_usage_bytes{{ container_label_io_kubernetes_pod_name = {} }}[{}])) / (1024^3)'.format(
            pod, application_window)
        response = requests.get(prometheus + '/api/v1/query', params={
            'query': query})
        # print(response.json())
        results = response.json()['data']['result']
        disk_use = float(results[0]['value'][1])
        return disk_use

    def network(pod):
        query = '(sum(avg(rate(container_network_transmit_bytes_total{{ container_label_io_kubernetes_pod_name={},interface=~"eth0|ens.*" }}[{}])))' \
                '+ sum(avg(rate(container_network_receive_bytes_total{{ container_label_io_kubernetes_pod_name={},interface=~"eth0|ens.*" }}[{}])))) * 8 / (10^9)' \
            .format(pod, application_window, pod, application_window)
        # print(query)
        response = requests.get(prometheus + '/api/v1/query', params={
            'query': query})
        # print(response.json())
        results = response.json()['data']['result']
        network_use = float(results[0]['value'][1])
        return network_use

    result=[]
    for id in app_list:

        cpu_use = 0
        memory_use = 0
        disk_use = 0
        network_use = 0

        namespace,app=id.split(":")
        namespace="'" + namespace + "'"
        app="'" + app + "'"
        query_temp='group by (container_label_io_kubernetes_pod_name) (container_tasks_state{{ container_label_io_kubernetes_pod_namespace={},' \
                   'container_label_io_kompose_service={} }})'.format(namespace,app)
        #print(query_temp)
        response = requests.get(prometheus + '/api/v1/query', params={
            'query': query_temp})
        #print(response.json())
        results = response.json()['data']['result']
        #print(results)
        for idx in results:
            pod=idx['metric']['container_label_io_kubernetes_pod_name']
            #print(pod)
            pod="'" + pod + "'"
            cpu_use+=cpu(pod)
            memory_use+=memory(pod)
            disk_use+=disk(pod)
            network_use+=network(pod)
        result.append((cpu_use,memory_use,disk_use,network_use))
    return result


def application_quantile(app_list):

    def cpu(pod):
        query='quantile_over_time( {}, sum by (container_label_io_kubernetes_pod_name)' \
              ' (rate(container_cpu_usage_seconds_total{{ container_label_io_kubernetes_pod_name={} }}[{}]))[{}:])'\
            .format(app_metric_percentile,pod,rate_interval,application_window)
        #print(query)
        response = requests.get(prometheus + '/api/v1/query', params={
            'query': query})
        #print(response.json())
        results = response.json()['data']['result']
        cpu_use=float(results[0]['value'][1])
        return cpu_use

    def memory(pod):
        query='quantile_over_time( {} , sum by (container_label_io_kubernetes_pod_name) ' \
              '(avg_over_time(container_memory_working_set_bytes{{ container_label_io_kubernetes_pod_name={} }}[{}]))[{}:]) /(1024^3)'.\
            format(app_metric_percentile,pod,rate_interval,application_window)
        #print(query)
        response = requests.get(prometheus + '/api/v1/query', params={
            'query': query})
        #print(response.json())
        results = response.json()['data']['result']
        memory_use=float(results[0]['value'][1])
        return memory_use

    def disk(pod):
        query='quantile_over_time( {} , sum by (container_label_io_kubernetes_pod_name) ' \
              '(avg_over_time(container_fs_usage_bytes{{ container_label_io_kubernetes_pod_name={} }}[{}]))[{}:]) /(1024^3)'.\
            format(app_metric_percentile,pod,rate_interval,application_window)
        response = requests.get(prometheus + '/api/v1/query', params={
            'query': query})
        # print(response.json())
        results = response.json()['data']['result']
        disk_use = float(results[0]['value'][1])
        return disk_use
    def network(pod):
        query='((quantile_over_time( {}, sum by (container_label_io_kubernetes_pod_name)' \
              ' (rate(container_network_receive_bytes_total{{ container_label_io_kubernetes_pod_name={},interface=~"eth0|ens.*" }}[{}]))[{}:]))' \
              '+ (quantile_over_time( {}, sum by (container_label_io_kubernetes_pod_name)' \
              '(rate(container_network_transmit_bytes_total{{ container_label_io_kubernetes_pod_name={},interface=~"eth0|ens.*" }}[{}]))[{}:]))) *8/(10^9)'\
            .format(app_metric_percentile,pod,rate_interval,application_window,app_metric_percentile,pod,rate_interval,application_window)
        #print(query)
        response = requests.get(prometheus + '/api/v1/query', params={
            'query': query})
        #print(response.json())
        results = response.json()['data']['result']
        network_use=float(results[0]['value'][1])
        return network_use

    result=[]
    for id in app_list:

        cpu_use = 0
        memory_use = 0
        disk_use = 0
        network_use = 0

        namespace,app=id.split(":")
        namespace="'" + namespace + "'"
        app="'" + app + "'"
        query_temp='group by (container_label_io_kubernetes_pod_name) (container_tasks_state{{ container_label_io_kubernetes_pod_namespace={},' \
                   'container_label_io_kompose_service={} }})'.format(namespace,app)
        #print(query_temp)
        response = requests.get(prometheus + '/api/v1/query', params={
            'query': query_temp})
        #print(response.json())
        results = response.json()['data']['result']
        #print(results)
        for idx in results:
            pod=idx['metric']['container_label_io_kubernetes_pod_name']
            #print(pod)
            pod="'" + pod + "'"
            cpu_use+=cpu(pod)
            memory_use+=memory(pod)
            disk_use+=disk(pod)
            network_use+=network(pod)
        result.append((cpu_use,memory_use,disk_use,network_use))
    return result

def deploy(vm_select,app_list,namespace):
    print('Deployment started... \n ')
    rootdir = "./deathstar"
    regex_str=''
    for i in app_list:
        regex_str+='('+i+')|'
    regex_str=regex_str[:len(regex_str)-1]

    #print(regex_str)
    regex = re.compile(regex_str)

    vm_dict={'10.24.24.131':'vm-1','10.24.24.132':'vm-2','10.24.24.133':'vm-3','10.24.24.134':'vm-4','10.24.24.135':'vm-5','10.24.24.136':'vm-6'}
    vm_list = ['vm-1', 'vm-2', 'vm-3', 'vm-4','vm-5','vm-6']
    file_list = []

    for root, dirs, files in os.walk(rootdir):
        for file in files:
            if regex.match(file):
                file_list.append(file)
    print('Files related to these deployments:\n',file_list,'\n')

    str='cd ~/hotelReservation-deployment/kubernetes/\n'
    vm_selected=vm_dict[vm_select]

    for i in vm_list:
        if vm_selected!=i:
            str+=('kubectl taint nodes {} key1=value1:NoSchedule\n'.format(i))

    for i in file_list:
        str+=('kubectl apply -f {} -n {}\n'.format(i,namespace))

    for i in vm_list:
        if vm_selected!=i:
            str+=('kubectl taint nodes {} key1=value1:NoSchedule-\n'.format(i))

    str += 'kubectl get pods --all-namespaces -o wide --field-selector spec.nodeName={} | head -n 1\n'.format(vm_selected,namespace)
    str+='kubectl get pods --all-namespaces -o wide --field-selector spec.nodeName={} | grep {}'.format(vm_selected,namespace)

    #print(str)

    ssh = pk.SSHClient()
    ssh.set_missing_host_key_policy(pk.AutoAddPolicy())

    ssh.connect(hostname=config['k8s_control_plane'], username='akshat', password='2716')
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(str)

    print('Error:')
    for line in iter(ssh_stderr.readline, ""):
        print(line, end="")
    print('finished. \n ')

    print('Output:')
    for line in iter(ssh_stdout.readline, ""):
        print(line, end="")
    print('finished.\n \nDeployment complete \n ')

def clear_namespace(namespace):
    print('Clearing namespace {}...\n'.format(namespace))
    str=''
    str+='kubectl delete daemonsets,replicasets,services,deployments,pods,rc,ingress,pvc,pv --all -n {}'.format(namespace)
    ssh = pk.SSHClient()
    ssh.set_missing_host_key_policy(pk.AutoAddPolicy())

    ssh.connect(hostname=config['k8s_control_plane'], username='akshat', password='2716')
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(str)

    print('Error:')
    for line in iter(ssh_stderr.readline, ""):
        print(line, end="")
    print('finished. \n')

    print('Output:')
    for line in iter(ssh_stdout.readline, ""):
        print(line, end="")
    print('finished. \n \nNamespace "{}" cleared'.format(namespace))


