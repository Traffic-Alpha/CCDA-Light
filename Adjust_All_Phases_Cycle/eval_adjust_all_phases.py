'''
@Author: WANG Maonan
@Date: 2024-05-01 19:26:54
@Description: 测试 Adjust All Phase 的模型, 得到信号灯策略曲线
@LastEditTime: 2024-06-28 00:32:12
'''
import os
import torch
import shutil
import argparse

from tshub.utils.init_log import set_logger
from tshub.utils.get_abs_path import get_abs_path

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import SubprocVecEnv

from env_utils.make_tsc_env import make_env 

path_convert = get_abs_path(__file__)
set_logger(path_convert('./'), file_log_level="INFO", terminal_log_level="WARNING")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process delta_time.')
    parser.add_argument('--delta_time', type=int, default=None, help='The delta time value')
    args = parser.parse_args() # Parse the arguments
    delta_time = args.delta_time # Use the delta_time argument

    # #########
    # Init Env
    # #########
    log_path = path_convert(f'./log/{delta_time}/eval')
    sumo_cfg = path_convert("../sumo_envs/fourWay/env/single_junction.sumocfg")
    input_folder = path_convert("../sumo_envs/fourWay/add")
    output_folder = path_convert(f"./exp_output/{delta_time}/")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    tls_add = [
        # 探测器
        path_convert(f'../sumo_envs/fourWay/detectors/e2.add.xml'),
        # 信号灯
        path_convert(f'../sumo_envs/fourWay/add/tls_programs.add.xml'),
        path_convert(f'../sumo_envs/fourWay/add/tls_state.add.xml'),
        path_convert(f'../sumo_envs/fourWay/add/tls_switch_states.add.xml'),
        path_convert(f'../sumo_envs/fourWay/add/tls_switches.add.xml')
    ]
    params = {
        'tls_id':'htddj_gsndj',
        'num_seconds': 7200,
        'sumo_cfg':sumo_cfg,
        'delta_time': delta_time,
        'use_gui':False,
        'log_file':log_path,
        'tls_state_add': tls_add,
        'trip_info': path_convert(f'./exp_output/{delta_time}/tripinfo.out.xml'),
        'summary': path_convert(f'./exp_output/{delta_time}/summary.out.xml'),
        'statistic_output': path_convert(f'./exp_output/{delta_time}/statistic.out.xml'),
    }
    env = SubprocVecEnv([make_env(env_index=f'{i}', **params) for i in range(1)])

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model_path = path_convert(f'./save_models/{delta_time}/rl_model_100000_steps.zip')
    model = PPO.load(model_path, env=env, device=device)

    # 使用模型进行测试
    obs = env.reset()
    dones = False # 默认是 False
    total_reward = 0

    while not dones:
        action, _state = model.predict(obs, deterministic=True)
        obs, rewards, dones, infos = env.step(action)
        total_reward += rewards
     
    env.close()
    print(f'累积奖励为, {total_reward}.')

    shutil.copytree(
        src=input_folder,
        dst=f"{output_folder}/add/",
        dirs_exist_ok=True
    )