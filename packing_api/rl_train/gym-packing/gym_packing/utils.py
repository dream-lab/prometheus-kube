import numpy as np
import pandas as pd

def normalize_data(data, max_vals, type):
    # print(max_vals, data.shape)
    if type == 'machine':
        data = data / max_vals
        data = np.c_[np.zeros(np.size(data, 0)), data]
        return data 
    
    elif type == 'container':
        data[:,1:] = data[:, 1:] / max_vals
        data[:, 0] = data[:, 0] / max(data[:, 0])
        return data 

def assign_env_config(self, kwargs):
    for key, value in kwargs.items():
        setattr(self, key, value)
    if hasattr(self, 'env_config'):
        for key, value in self.env_config.items():
            # Check types based on default settings
            if hasattr(self, key):
                if type(getattr(self,key)) == np.ndarray:
                    setattr(self, key, value)
                else:
                    setattr(self, key,
                        type(getattr(self, key))(value))
            else:
                raise AttributeError(f"{self} has no attribute, {key}")

def generate_durations(demand):
    # duration_params = np.array([ 6.53563303e-02,  5.16222242e+01,  4.05028032e+06, -4.04960880e+06])
    return {i: np.random.randint(low=i+1, high=len(demand)+1)
        for i, j in enumerate(demand)}

def generate_demand(n):
    # From Azure data
    mem_probs = np.array([0.12 , 0.165, 0.328, 0.287, 0.064, 0.036])
    mem_bins = np.array([0.02857143, 0.05714286, 0.11428571, 0.45714286, 0.91428571, 1.]) # Normalized bin sizes

    mu_cpu = 16.08
    sigma_cpu = 1.26
    cpu_demand = np.random.normal(loc=mu_cpu, scale=sigma_cpu, size=n)
    cpu_demand = np.where(cpu_demand<=0, mu_cpu, cpu_demand) # Ensure demand isn't negative

    mem_demand = np.random.choice(mem_bins, p=mem_probs, size=n)

    mu_disk = 25.08
    sigma_disk = 3.26
    disk_demand = np.random.normal(loc=mu_disk, scale=sigma_disk, size=n)
    disk_demand = np.where(disk_demand<=0, mu_disk, disk_demand) # Ensure demand isn't negative

    mu_net = 8.06
    sigma_net = 2.35
    net_demand = np.random.normal(loc=mu_net, scale=sigma_net, size=n)
    net_demand = np.where(net_demand<=0, mu_net, net_demand) # Ensure demand isn't negative

    return np.vstack([np.arange(n)/n, cpu_demand/100, mem_demand, disk_demand/100, net_demand/100]).T


