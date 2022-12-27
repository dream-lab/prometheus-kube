import sys 

# Imports
import os, argparse
from app_reader import generate_app_list
from vm_reader import generate_vm_list
import pickle

import gym
import gym_packing
import numpy as np

from stable_baselines3.common.monitor import Monitor
from sb3_contrib.common.maskable.policies import MaskableActorCriticPolicy
from sb3_contrib.common.wrappers import ActionMasker
from sb3_contrib.ppo_mask import MaskablePPO
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback, ProgressBarCallback, CallbackList
import torch as th

TRAIN_EPISODES = 5000

# CLI Arguments
parser = argparse.ArgumentParser(description='file')
parser.add_argument('--mf', help='machine file path')
parser.add_argument('--cf', help='container file path')
parser.add_argument('--l',  help='choose length', default=-1)
parser.add_argument('--check', help="Validate gym environment", default=0)
parser.add_argument('--train', help="Train gym environment", default=0)
args = parser.parse_args()

machine_path = args.mf
contianer_path = args.cf
check = int(args.check)
length = int(args.l)
train = int(args.train)

# Generating data
vms, vms_dict = generate_vm_list(os.path.abspath(machine_path))
apps, apps_dict, static_ct = generate_app_list(os.path.abspath(contianer_path), length)

# print(apps[0])
def mask_fn(env: gym.Env) -> np.ndarray:
    # Do whatever you'd like in this function to return the action mask
    # for the current env. In this example, we assume the env has a
    # helpful method we can rely on.
    return env.valid_action_mask()



model = None 
actions_dict = None
env_config = {
    'step_limit' : np.size(apps, 0),
    'n_pms' : np.size(vms, 0),
    'machines' : vms[:,1:],
    'max_vals' : vms[:,1:].max(axis = 0),
    'containers' : apps[:,1:],
    'shuffle_cnt' : True,
}

if check == 1:
    
    from stable_baselines3.common.env_checker import check_env
    env = gym.make('vm-packing-v0', env_config=env_config)
    check_env(env)


    
trainer = None

if train == 1:

    actions_dict = None
    transitions = None
    venv = None
    env = None

    eval_env = gym.make('vm-packing-v0', env_config=env_config)
    eval_env = ActionMasker(eval_env, mask_fn)
    eval_env = Monitor(eval_env)

    eval_callback = EvalCallback(
        eval_env, 
        best_model_save_path="./models/",
        log_path="./log/",
        eval_freq=env_config['step_limit']*3,
        deterministic=True, 
        render=False,
        verbose=0,
    )

    progress_bar = ProgressBarCallback()
    callbacks = CallbackList([eval_callback, progress_bar])

    # MaskablePPO behaves the same as SB3's PPO unless the env is wrapped
    # with ActionMasker. If the wrapper is detected, the masks are automatically
    # retrieved and used when learning. Note that MaskablePPO does not accept
    # a new action_mask_fn kwarg, as it did in an earlier draft.
    env = gym.make('vm-packing-v0', env_config=env_config)
    env = ActionMasker(env, mask_fn)  # Wrap to enable masking

    # Custom actor (pi) and value function (vf) networks
    # of two layers of size 32 each with Relu activation function
    policy_kwargs = dict(
        net_arch=[dict(vf=[64, 32], pi=[64, 32])],
        activation_fn=th.nn.LeakyReLU,
    )

    model = MaskablePPO(MaskableActorCriticPolicy, env, verbose=0, tensorboard_log="./log/", batch_size=32, policy_kwargs=policy_kwargs)
    model.learn(env_config['step_limit']*TRAIN_EPISODES, callback=callbacks)
    print("Training done!!")

