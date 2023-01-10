from pyvpsolver.solvers import mvpsolver
from collections import deque, defaultdict 

import numpy as np

class prettyDict(defaultdict):
    def __init__(self, *args, **kwargs):
        defaultdict.__init__(self,*args,**kwargs)

    def __repr__(self):
        return str(dict(self))


def generate_data(machines, mid_list, containers, cid_list):
    total_ct_grp = np.size(containers, 0)

    bin_to_machine_maps = prettyDict(deque)
    data = {}

    # Bins
    bin_capacities, num_bins = np.unique(machines, return_counts=True, axis = 0)

    bin_capacities = bin_capacities.astype(int)

    for mid, machine in zip(mid_list, machines):
        x = machine.astype(int)
        bin_to_machine_maps[tuple(x)].append(mid)

    # cost = bin_capacities[:,0]*70 + bin_capacities[:,1]*20 + bin_capacities[:,2]*5 + bin_capacities[:,3]*5

    cost = [1 for _ in range(np.size(bin_capacities, 0))]
    # cost = bin_capacities[:,0]*7 + bin_capacities[:,1]*3

    demand = [1 for _ in range(total_ct_grp)]
    cids = cid_list
    item_capacities = [[x] for x in containers]

    data['mids'] = bin_to_machine_maps
    data['bin_capacities'] = bin_capacities
    data['cost'] = cost
    data['num_bins'] = num_bins

    data['cids'] = cids 
    data['item_capacities'] = item_capacities
    data['demand'] = demand
    return data

def group_containers(a):
    x = np.split(a, np.unique(a[:, 1], return_index=True)[1])[::-1][0]
    x = x.astype(int)
    return x



def VpSolver(machines, mid_list, containers, cid_list):

    optimizer = 'vpsolver_glpk.sh' 

    action_dict = {}

    data = generate_data(machines, mid_list, containers, cid_list)
    # print(data)
    solution = None

    try:
        solution = mvpsolver.solve(
            data['bin_capacities'], data['cost'], data['num_bins'],
            data['item_capacities'], data['demand'],
            script=optimizer,
            verbose=False,
            script_options="Threads=8",    
            )
            
        # mvpsolver.print_solution(solution)

    except Exception as e:
        # print(e)
        return {'ERROR' : 'VPSolv cannot fit for given placement'}



    objective, lst_sol = solution
    container_set = set()
    for idx, sol in enumerate(lst_sol):
        x = tuple(data['bin_capacities'][idx])
        
        mc_idx = 0

        for multiplier, pattern in sol:

            for i in range(multiplier):

                schedule_mc_name = data['mids'][x][0]

                
                for it, opt in pattern:
                    action_dict[cid_list[it]] = schedule_mc_name
                mc_idx += 1

    return action_dict


    
