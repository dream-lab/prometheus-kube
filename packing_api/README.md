
Python >= 3.7 (We use 3.8.13)

## INSTALLATION:

```
pip install fastapi
pip install "uvicorn[standard]"
pip install pyvpsolver
sudo apt-get install glpk-utils
pip install stable-baselines3[extra]
pip install sb3-contrib
pip install tqdm
pip install tensorboard
```

## INSTALLING GYM ENV:
```
cd rl_train/gym-packing
pip install -e .
```

## RL TRAINING:
``` 
cd rl_train
```

- Create csv files similar to **test_applications.csv** and **test_vms.csv** these shall be your training data
- Test if gym env is valid
```
python train.py --mf data/test_vms.csv --cf data/test_applications.csv --check 1
``` 
This should return just a user warning regarding the shape of observation space 

- Train the RL agent
```
python train.py --mf data/test_vms.csv --cf data/test_applications.csv --train 1
```
Best model will be saved under ```models/``` dir, tensorboard logs are stored under ```logs/``` dir


## INTEGRATING WITH AN API
- Need to write custom code for ```get_capacity_and_max``` in ```rl.py``` that shall return the initial capacities of all machines and max across each dimension (cpu, mem, disk, net) depending upon usecase.

- If using FastAPI as server, use the following command to start the server
```
uvicorn packing:app --host x.x.x.x
```
x.x.x.x is either localhost or an ip


