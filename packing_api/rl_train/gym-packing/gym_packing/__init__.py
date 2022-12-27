from gym.envs.registration import register

register(
    id='vm-packing-v0',
    entry_point='gym_packing.envs:VMPackingEnv',
)

register(
    id='vm-packing-std-v0',
    entry_point='gym_packing.envs:VMPackingEnv2',
)