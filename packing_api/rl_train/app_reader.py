# This file reads app csv file and creates machine objects
import pandas as pd
import numpy as np

def generate_app_list(file_name, length):
    df = pd.read_csv(file_name)


    disk_flag, net_flag = False, False 

    if 'disk' in df.columns:
        disk_flag = True

    if 'net' in df.columns:
        net_flag = True


    app_list = list()
    apps_dict = {}
    static_ct = 0

    for idx, (_, row) in enumerate(df.iterrows()):

        if idx == length:
            break

        disk , net = -1, -1
        if disk_flag:
            disk = row.disk 
        if net_flag:
            net = row.net

        apps_dict[idx] = row.cid

        app_list.append([idx, row.cpu, row.mem, disk, net])
    
    apps = np.array(app_list, dtype=int)

    return apps, apps_dict, static_ct
