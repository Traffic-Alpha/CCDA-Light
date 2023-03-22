'''
@Author: WANG Maonan
@Date: 2022-08-16 20:09:24
@Description: 一个周期对相位进行调整, 且一个周期只调整一个相位的时间
LastEditTime: 2022-08-19 13:08:01
'''
import os
import numpy as np
from lib import makeENV
from aiolos.utils.get_abs_path import getAbsPath
from aiolos.trafficLog.initLog import init_logging
from stable_baselines3.common.env_checker import check_env

if __name__ == '__main__':
    pathConvert = getAbsPath(__file__)
    init_logging(log_path=pathConvert('./'), log_level=0)

    tls_id = 'htddj_gsndj'
    sumo_cfg = pathConvert(f'../nets/env/single_junction.sumocfg')
    net_file = pathConvert(f'../nets/env/4phases.net.xml')
    route_list = [pathConvert(f'../nets/routes/{i}.rou.xml') for i in range(1)]
    log_path = pathConvert('./log/')
    DURATION_RANGE = [
        [-10, 10],
        [-10, 10],
        [-10, 10],
        [-10, 10],
    ] # 每个 phase 变化范围

    if not os.path.exists(log_path):
        os.makedirs(log_path)

    # 初始化环境
    g_envs = makeENV.make_env(
        tls_id=tls_id,
        num_seconds=7000,
        sumo_cfg=sumo_cfg,
        net_file=net_file,
        route_files=route_list,
        duration_range=DURATION_RANGE,
        use_gui=False,
        min_green=5, # 最小绿灯时间为 10s
        log_file=log_path, # 存储 log 文件的路径
        env_index='test_env',
        is_shuffle=False
    )
    env1 = g_envs() # 生成新的环境
    check_env(env1, warn=True) # 测试环境

    # 随机执行动作, 查看 state, action, reward
    obs = env1.reset()
    done = False # 默认是 False
    
    # 打印相位结构
    print(env1.net_movements) # movement_id -> 转向
    print(env1.net_masks) # phase 包含哪些 movement
    print(env1.movement_info) # movement 包含的信息

    # 打印「obs space」和「action space」
    print(env1.observation_space)
    print(env1.action_space)

    total_reward = 0 # 统计一下累计奖励
    while not done:
        action = env1.action_space.sample()
        obs, reward, done, info = env1.step(action) # 随机选择一个动作, 从 phase 中选择一个
        print(obs.shape) # 检查一下 obs 返回的值是否正确
    env1.close()