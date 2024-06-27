'''
@Author: WANG Maonan
@Date: 2024-05-01 17:30:53
@Description: 创建 TSC Env (结合 SB3 使用)
@LastEditTime: 2024-05-05 16:45:08
'''
import gymnasium as gym
from typing import List
from env_utils.tsc_env import TSCEnvironment
from env_utils.tsc_wrapper import TSCEnvWrapper
from stable_baselines3.common.monitor import Monitor

def make_env(
        tls_id:str,num_seconds:int,sumo_cfg:str,use_gui:bool,
        delta_time:int, log_file:str, env_index:int,
        tls_state_add:List[str]=None,
        is_eval:bool=False
    ):
    def _init() -> gym.Env: 
        tsc_scenario = TSCEnvironment(
            sumo_cfg=sumo_cfg, 
            num_seconds=num_seconds,
            tls_ids=[tls_id], 
            delta_time=delta_time,
            use_gui=use_gui,
            tls_state_add=tls_state_add,
        )
        tsc_wrapper = TSCEnvWrapper(tsc_scenario, tls_id=tls_id, is_eval=is_eval)
        return Monitor(tsc_wrapper, filename=f'{log_file}/{env_index}')
    
    return _init