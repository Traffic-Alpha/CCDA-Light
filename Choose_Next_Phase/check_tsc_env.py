'''
@Author: WANG Maonan
@Date: 2023-09-08 15:57:34
@Description: 测试 TSC Env (Choose Next Phase) 环境
@LastEditTime: 2024-06-18 22:06:09
'''
import numpy as np
from loguru import logger
from tshub.utils.get_abs_path import get_abs_path
from tshub.utils.init_log import set_logger
from stable_baselines3.common.env_checker import check_env
from env_utils.make_tsc_env import make_env

path_convert = get_abs_path(__file__)
set_logger(path_convert('./'))

if __name__ == '__main__':
    sumo_cfg = path_convert("../sumo_envs/fourWay/env/single_junction.sumocfg")
    log_path = path_convert('./log/')
    tsc_env_generate = make_env(
        tls_id='htddj_gsndj',
        num_seconds=7200,
        sumo_cfg=sumo_cfg,
        delta_time=5, # 动作之间的间隔时间
        use_gui=False,
        log_file=log_path,
        env_index=0,
    )
    tsc_env = tsc_env_generate()

    # Check Env
    print(tsc_env.observation_space.sample())
    print(tsc_env.action_space.n)
    check_env(tsc_env)

    # Simulation with environment
    dones = False
    tsc_env.reset()
    while not dones:
        action = np.random.randint(4)
        states, rewards, truncated, dones, infos = tsc_env.step(action=action)
        logger.info(f"SIM: {infos['step_time']} \n+State:{states}; \n+Reward:{rewards}.")
    tsc_env.close()