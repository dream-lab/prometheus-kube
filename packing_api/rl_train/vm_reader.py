# This file reads vms csv file and creates vm objects
import pandas as pd
import numpy as np

def generate_vm_list(file_name):
    df = pd.read_csv(file_name)

    vms_list = list()
    vms_dict = {}
    
    disk_flag, net_flag = False, False 


    if 'disk' in df.columns:
        disk_flag = True

    if 'net' in df.columns:
        net_flag = True

    for idx, row in df.iterrows():

        disk , net = -1, -1
        if disk_flag:
            disk = row.disk 
        if net_flag:
            net = row.net

        vms_dict[idx] = row.mid 
        vm = np.array([idx, row.cpu, row.mem, disk, net])
        vms_list.append(vm)

    vms = np.array(vms_list, dtype=int)

    return vms, vms_dict