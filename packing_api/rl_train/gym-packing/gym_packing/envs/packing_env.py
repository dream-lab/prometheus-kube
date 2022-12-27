import numpy as np
import copy
import gym
from gym import spaces
from gym_packing.utils import *
from gym.utils import seeding

from gym_packing.utils import normalize_data

BIG_NEG_REWARD = -1000

class VMPackingEnv(gym.Env):
    '''
    Observation:
        Type: Tuple, Discrete
        [0][:, 0]: Binary indicator for open PM's
        [0][:, 1]: CPU load of PM's
        [0][:, 2]: Memory load of PM's
        [0][:, 3]: Disk load of PM's
        [0][:, 4]: Network load of PM's
        [1][0]: Dummy value to match dimension with PMs
        [1][1]: Current CPU demand
        [1][2]: Current memory demand
        [1][3]: Current disk demand
        [1][4]: Current network demand

    Actions:
        Type: Discrete
        Integer of PM number to send VM to that PM

    Reward:
        Negative of the waste, which is the difference between the current
        size and excess space on the PM.

    Starting State:
        No open PM's and first request
        
    Episode Termination:
        When invalid action is selected, attempt to overload VM, or step
        limit is reached.
    '''

    def __init__(self,  *args, **kwargs):
        # Fill with dummy values that can be overridden by env_config
        # self.seed = np.random.RandomState(0)
        self.eps = 1e-6
        self.step_limit = 75 # number of requests
        self.n_pms = 15 # number of machines

        self.machines = np.empty(shape=(self.n_pms,4)) # cpu, mem, disk, net # INT
        self.max_vals = np.empty(shape=(1,4)) # max values of cpu mem disk net
        self.shuffle_cnt = False
        self.containers = np.empty(shape=(self.step_limit, 4)) # cpu, mem, disk, net
        self.reward_type = 'space'
        assign_env_config(self, kwargs)

        self.machines_avail = None  # pm_on/off, cpu, mem, disk, net # (Norm)
        self.machines_cap_norm_sum = None # pm_on/off, cpu, mem, disk, net # (Norm)

        self.demand = None # dummy, cpu, mem, disk, net # (Norm)

        self.machines_avail_int = None # deepcopy of machines
        self.machines_used_int = None # empty machines usage gets added here
        self.machines_cap_int = None # deepcopy of machines
        self.containers_int = None # deep copy of containers

        self.active_machines = 0
        self.current_step = 0

        self.action_space = spaces.Discrete(self.n_pms) # Choose one of the machine
        self.observation_space = spaces.Box(low = 0, high = 1, shape=(self.n_pms+1, 5), dtype=np.float32)

        self.state = self.reset()


    def normalize_data(self, data):
        data = data / self.max_vals
        data = np.c_[np.zeros(np.size(data, 0)), data]
        return data


    def reset(self):
        self.current_step = 0 # signifies the current process
        self.assignment = {} # dict to map vm req number to pm number
        self.active_machines = 0

        if self.shuffle_cnt == True:
            np.random.shuffle(self.containers)

        self.machines_avail = self.normalize_data(self.machines)
        self.machines_cap_norm_sum = self.machines_avail[:, 1:].sum(axis = 1)

        # cpu, mem, disk, net
        self.machines_avail_int = copy.deepcopy(self.machines) 
        self.containers_int = copy.deepcopy(self.containers)
        self.demand = self.normalize_data(self.containers_int)
        request_norm = self.demand[self.current_step]
        
        self.state = np.vstack(
                [
                    self.machines_avail, # pm_on/off, cpu, mem, disk, net
                    request_norm.reshape(1,-1), # dummy, cpu, mem, disk, net
                ]
            ).astype(np.float32)

        # print(self.state.shape)
        return self.state

    def step(self, action):
        done = False
        step = self.current_step
        self.current_step += 1

        pm_state = self.state[:-1]
        demand = self.state[-1]

        reward = 0

        if action < 0 or action >= self.n_pms:
            raise ValueError("Invalid action: {}".format(action))

        # Demand doesn't fit into PM
        elif any(pm_state[action, 1:] - demand[1:] < 0 - self.eps):
            cost = 0.7*self.machines_avail_int[action,0] + 0.3*self.machines_avail_int[action,1]
            reward = BIG_NEG_REWARD - self.calculate_reward_on_space(pm_state, cost)
            done = True
        else:
            new_mc = False
            if pm_state[action, 0] == 0:
                # Open PM if closed
                pm_state[action, 0] = 1
                new_mc = True
                self.active_machines += 1

            cost = 0.7*self.machines_avail_int[action,0] + 0.3*self.machines_avail_int[action,1]
            pm_state[action, 1:] -= demand[1:]
            self.machines_avail_int[action] -= self.containers_int[step]
            self.assignment[step] = action 

            if self.reward_type == 'space':
                if new_mc:
                    reward = self.calculate_reward_on_space(pm_state, cost)
                    # print("RC=",reward)
                else:
                    reward = -pm_state[action, 1:].sum()
                    # print("R=",reward)
        
        if self.current_step >= self.step_limit:
            done = True
        self.update_state(pm_state)
 
        return self.state, reward, done, {'active_machines':self.active_machines, 'mid': action, 'cid':self.containers_int[step], 'reward':reward}



    def update_state(self, pm_state):

        # Make action selection impossible if the PM would exceed capacity
        step = self.current_step if self.current_step < self.step_limit else self.step_limit-1
        self.machines_avail = self.normalize_data(self.machines_avail_int)

        # print(self.machines_avail.shape, pm_state.shape)
        self.machines_avail[:,0] = pm_state[:,0]

        data_center = np.vstack([
            self.machines_avail, 
            self.demand[step].reshape(1,-1)]
        ).astype(np.float32)

        data_center = np.where(data_center>1,1, data_center) # Fix rounding errors
        self.state = data_center

    def calculate_reward_on_space(self, pm_state, cost):
        remain = pm_state[:, 0] * (pm_state[:,1:].sum(axis=1) - self.machines_cap_norm_sum)
        r1 = np.sum(remain)
        r2 = np.sum(pm_state[:, 0]) / len(self.machines)
        reward = 0.6 * r1 - r2 - 0.4 * cost
        return reward

    
    def sample_action(self):
        return self.action_space.sample()

    def valid_action_mask(self):
        
        pm_state = self.state[:-1]
        demand = self.state[-1]
        action_mask = (pm_state[:,1:] - demand[1:]) > 0 - self.eps
        return (action_mask.sum(axis=1)==4).astype(int)

    def action_masks(self):
        return self.valid_action_mask()

    def get_obs(self):
        return self.state 

    def set_obs(self, state, cidx):
        self.state = state
        self.current_step = cidx 


    


   