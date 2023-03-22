'''
@Author: WANG Maonan
@Date: 2022-10-17 15:49:53
@Description: 测试 Set Current Phase Duration (使用外挂的参数)
@LastEditTime: 2022-10-24 15:54:24
'''
import os
import shutil
import torch
import itertools
import argparse
import numpy as np
rmd = np.random.RandomState(1) # 固定随机数

from aiolos.utils.get_abs_path import getAbsPath
from aiolos.trafficLog.initLog import init_logging
from stable_baselines3 import A2C, PPO, DQN
from stable_baselines3.common.vec_env import VecNormalize, SubprocVecEnv

from lib import makeENV


if __name__ == '__main__':
    pathConvert = getAbsPath(__file__)
    init_logging(log_path=pathConvert('./'), log_level=0)

    # 路网参数
    parser = argparse.ArgumentParser("Run Set Current Phase Duration experiments.")
    parser.add_argument("--home_folder", type=str, required=True, help="所有内容存放在目录.")
    parser.add_argument("--net_folder", type=str, required=True, help="路网的文件夹.")
    parser.add_argument("--net_id", type=str, required=True, help="不同的信号灯组合.")
    parser.add_argument("--delta_times", required=True, help="做动作的间隔.")
    parser.add_argument("--model_type", required=True, help="模型选择, best or last.") # best or last
    parser.add_argument("--route_id", required=True, help="车流文件, stable or fluctuation.") # stable or fluctuation
    parser.add_argument("--random_mask_obs", required=True, help="是否随机遮住 obs, 用于查看模型的鲁棒性.") # True or False
    parser.add_argument("--model_name", default='PPO', help="模型的名称, 可以是 PPO, DQN.")

    args = parser.parse_args()
    HOME_FOLDER = args.home_folder # 所有文件的主目录
    MODEL_NAME = args.model_name # 模型的名称
    assert MODEL_NAME in ['PPO', 'DQN', 'A2C'], f'模型名称需要是 PPO, DQN, A2C, 现在是 {MODEL_NAME}'
    net_folder, net_id = args.net_folder, args.net_id
    MODEL_TYPE = args.model_type
    route_id = args.route_id
    random_mask_obs = bool(args.random_mask_obs) # 是否对 obs 进行 mask 处理, True or False
    if args.delta_times == 'None':
        delta_times = None # 在传入环境的时候, 如果是 None 那么就 5s 控制一次
    else:
        delta_times = int(args.delta_times) # 做动作的间隔


    print(f'===> 开始分析, {MODEL_TYPE}, {route_id}')
    # #######
    # 训练参数
    # #######  
    NUM_CPUS = 1
    MIN_GREEN = 5
    INIT_DURATION = 30 # 初始信号灯时间
    SHFFLE = False # 是否进行数据增强
    ACTION_TYPE = 'discrete' # 'discrete', 'minorEdit', 'continue'
    MODEL_FOLDER = pathConvert(f'./{HOME_FOLDER}/models/{delta_times}/{net_folder}/{net_id}/{route_id}/')
    MODEL_PATH = os.path.join(MODEL_FOLDER, f'{MODEL_TYPE}_model.zip')
    VEC_NORM = os.path.join(MODEL_FOLDER, f'{MODEL_TYPE}_vec_normalize.pkl')
    LOG_PATH = pathConvert(f'./log/{delta_times}/{net_folder}/{net_id}/{route_id}/') 
    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH)

    # 初始化环境
    tls_id = 'htddj_gsndj'
    sumo_cfg = pathConvert(f'../nets/{net_folder}/env/single_junction.sumocfg')
    net_file = pathConvert(f'../nets/{net_folder}/env/{net_id}.net.xml')
    route_list = [pathConvert(f'../nets/{net_folder}/routes/{route_id}.rou.xml')]
    # output 统计文件
    output_folder = pathConvert(f'./{HOME_FOLDER}/testResult_mask_obs/{delta_times}/{net_folder}/{net_id}/{route_id}/{MODEL_TYPE}')
    os.makedirs(output_folder, exist_ok=True) # 创建文件夹
    trip_info = os.path.join(output_folder, f'tripinfo.out.xml')
    statistic_output = os.path.join(output_folder, f'statistic.out.xml')
    summary = os.path.join(output_folder, f'summary.out.xml')
    queue_output = os.path.join(output_folder, f'queue.out.xml')
    tls_add = [
        # 探测器
        pathConvert(f'../nets/{net_folder}/detectors/e1_internal.add.xml'),
        pathConvert(f'../nets/{net_folder}/detectors/e2.add.xml'),
        # 信号灯
        pathConvert(f'../nets/{net_folder}/add/tls_programs.add.xml'),
        pathConvert(f'../nets/{net_folder}/add/tls_state.add.xml'),
        pathConvert(f'../nets/{net_folder}/add/tls_switch_states.add.xml'),
        pathConvert(f'../nets/{net_folder}/add/tls_switches.add.xml')
    ]
    params = {
        'tls_id':tls_id,
        'num_seconds':7000,
        'sumo_cfg':sumo_cfg,
        'net_file':net_file,
        'route_files':route_list,
        'is_shuffle':SHFFLE, # 不进行数据增强
        'action_type':ACTION_TYPE,
        'is_libsumo':False,
        'use_gui':False,
        'min_green':MIN_GREEN,
        'delta_times':delta_times,
        'init_green_duration':INIT_DURATION,
        'log_file':LOG_PATH,
        'trip_info':trip_info,
        'statistic_output':statistic_output,
        'summary':summary,
        'queue_output':queue_output,
        'tls_state_add': tls_add,
        'mode':'eval' # 不要对环境进行 reset
    }
    env = SubprocVecEnv([makeENV.make_env(env_index=f'evaluate_{i}', **params) for i in range(NUM_CPUS)])
    env = VecNormalize.load(load_path=VEC_NORM, venv=env) # 加载环境 Norm 参数
    env.training = False # 测试的时候不要更新
    env.norm_reward = False
    # 加载模型
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    if MODEL_NAME == 'A2C':
        model = A2C.load(MODEL_PATH, env=env, device=device)
    elif MODEL_NAME == 'PPO':
        model = PPO.load(MODEL_PATH, env=env, device=device)
    elif MODEL_NAME == 'DQN':
        model = DQN.load(MODEL_PATH, env=env, device=device)
    # 使用模型进行测试
    obs = env.reset()
    done = False # 默认是 False

    total_reward = 0
    while not done:
        if random_mask_obs: # 是否对 obs 进行随机
            mask = (rmd.rand(*obs.shape)) > 0.8 # 有 20% 的概率, 将 True 修改为随机数
            obs = obs*(1-mask) + rmd.rand(*obs.shape)*mask # 生成新的 obs

        action, _state = model.predict(obs, deterministic=True)
        obs, reward, done, info = env.step(action) # 随机选择一个动作, 从 phase 中选择一个
        total_reward += reward
    print(f'累计奖励, {total_reward}')
    env.close()

    # 把 add 文件复制到 testResult 文件夹下
    shutil.copytree(
        src=pathConvert(f'../nets/{net_folder}/add/'),
        dst=f'{output_folder}/add/',
        dirs_exist_ok=True,
    )