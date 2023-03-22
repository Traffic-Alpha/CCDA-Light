'''
@Author: WANG Maonan
@Date: 2022-06-16 21:57:23
@Description: 测试环境, state, action 和 reward
@LastEditTime: 2022-08-19 20:32:02
'''
import os
from lib import makeENV
from aiolos.utils.get_abs_path import getAbsPath
from aiolos.trafficLog.initLog import init_logging
from stable_baselines3.common.env_checker import check_env
from prettyprinter import cpprint

if __name__ == '__main__':
    pathConvert = getAbsPath(__file__)
    init_logging(log_path=pathConvert('./'), log_level=0)
    
    ACTION_TYPE = 'discrete' # 'discrete', 'minorEdit', 'continue'

    tls_id = 'htddj_gsndj'
    sumo_cfg = pathConvert(f'../nets/env/single_junction.sumocfg')
    net_file = pathConvert(f'../nets/env/4phases.net.xml')
    route_list = [pathConvert(f'../nets/routes/{i}.rou.xml') for i in range(1)]
    log_path = pathConvert('./log/')

    if not os.path.exists(log_path):
        os.makedirs(log_path)

    # 初始化环境
    g_envs = makeENV.make_env(
        tls_id=tls_id,
        num_seconds=7000,
        sumo_cfg=sumo_cfg,
        net_file=net_file,
        route_files=route_list,
        use_gui=False,
        min_green=5, # 最小绿灯时间为 10s
        log_file=log_path, # 存储 log 文件的路径
        env_index='test_env',
        action_type=ACTION_TYPE,
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

    while not done:
        action = env1.action_space.sample()
        obs, reward, done, info = env1.step(action) # 随机选择一个动作, 从 phase 中选择一个
        print(obs.shape) # 检查一下 obs 返回的值是否正确

    env1.close()