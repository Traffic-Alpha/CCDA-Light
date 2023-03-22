'''
@Author: WANG Maonan
@Date: 2022-08-16 20:09:24
@Description: 测试环境, 看一下相同动作的 reward
LastEditTime: 2022-08-16 23:34:04
'''
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
        [-10, 10, 5],
        [-10, 10, 5],
        [-10, 10, 5],
        [-10, 10, 5],
    ] # 每个 phase 变化范围

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
        # action = np.array([0,0,0,0]) # 减小相位时间
        action = np.array([2,2,2,2]) # 保持相位时间不变
        # action = np.array([4,4,4,4]) # 增大相位时间
        obs, reward, done, info = env1.step(action) # 随机选择一个动作, 从 phase 中选择一个
        print(obs.shape) # 检查一下 obs 返回的值是否正确
        total_reward += reward
    print(f'累计奖励, {total_reward}')
    # 随机动作, 累计奖励, -8442.75
    # 一直减小, 累计奖励, -6982.716666666
    # 一直增大 5, 累计奖励, -5373.70555555555
    # 一直增大 10, 累计奖励, -5642.9722222222235
    # 全部相位是 30s, 累计奖励, -3054.34166666666
    env1.close()