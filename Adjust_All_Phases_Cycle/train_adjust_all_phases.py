'''
@Author: WANG Maonan
@Date: 2024-05-01 19:10:59
@Description: 训练同时修改所有相位
-> python train_adjustAllPhases.py --delta_time 120
@LastEditTime: 2024-06-28 15:47:14
'''
import os
import torch
import argparse

from loguru import logger
from tshub.utils.get_abs_path import get_abs_path

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import SubprocVecEnv, VecNormalize
from stable_baselines3.common.callbacks import CallbackList, CheckpointCallback

from env_utils.make_tsc_env import make_env
from train_utils.sb3_utils import linear_schedule
from train_utils.custom_models import CustomModel

logger.remove()
path_convert = get_abs_path(__file__)

def create_env(params, CPU_NUMS=12):
    env = SubprocVecEnv([make_env(env_index=f'{i}', **params) for i in range(CPU_NUMS)])
    env = VecNormalize(env, norm_obs=False, norm_reward=True)
    return env

def train_model(env, delta_time, tensorboard_path, callback_list):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    policy_kwargs = dict(
        features_extractor_class=CustomModel,
        features_extractor_kwargs=dict(features_dim=32),
    )
    model = PPO(
        "MlpPolicy", 
        env, 
        batch_size=128, 
        n_steps=7200//delta_time, # 每次更新的样本数量为 n_steps*NUM_CPUS, n_steps 太小可能会收敛到局部最优
        n_epochs=10, # 每次更新时，用同一批数据进行优化的次数。
        learning_rate=linear_schedule(1e-3),
        verbose=True,
        policy_kwargs=policy_kwargs, 
        tensorboard_log=tensorboard_path, 
        device=device
    )
    model.learn(total_timesteps=1e5, tb_log_name=f'CycleAdjustPhases_{delta_time}', callback=callback_list)
    return model

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process delta_time.')
    parser.add_argument('--delta_time', type=int, default=None, help='The delta time value')
    parser.add_argument('--num_envs', type=int, default=10, help='The number of envs')
    args = parser.parse_args() # Parse the arguments
    delta_time = args.delta_time # Use the delta_time argument
    num_envs = args.num_envs # 同时开启的环境数量

    log_path = path_convert(f'./log/{delta_time}/')
    model_path = path_convert(f'./save_models/{delta_time}/')
    tensorboard_path = path_convert('./tensorboard/')
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    if not os.path.exists(model_path):
        os.makedirs(model_path)
    if not os.path.exists(tensorboard_path):
        os.makedirs(tensorboard_path)
    
    # Define the parameters for the environment creation
    sumo_cfg = path_convert("../sumo_envs/fourWay/env/single_junction.sumocfg")
    params = {
        'tls_id': 'htddj_gsndj',
        'num_seconds': 7200,
        'sumo_cfg': sumo_cfg,
        'delta_time': delta_time,
        'use_gui': False,
        'log_file': log_path,
    }
    env = create_env(params, CPU_NUMS=num_envs)

    # Callbacks
    checkpoint_callback = CheckpointCallback(
        save_freq=1000, 
        save_path=model_path,
        save_vecnormalize=True
    )
    callback_list = CallbackList([checkpoint_callback])

    model = train_model(env, delta_time, tensorboard_path, callback_list)

    # Save model and environment
    model.save(os.path.join(model_path, 'last_rl_model.zip'))
    logger.info('Training complete, reached maximum steps.')

    env.close()