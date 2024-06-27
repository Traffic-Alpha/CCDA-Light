'''
@Author: WANG Maonan
@Date: 2024-05-01 17:23:25
@Description: 信号灯控制基础环境
@LastEditTime: 2024-05-05 16:12:36
'''
import gymnasium as gym

from typing import List, Dict
from tshub.tshub_env.tshub_env import TshubEnvironment

class TSCEnvironment(gym.Env):
    def __init__(self, sumo_cfg:str, num_seconds:int, tls_ids:List[str], delta_time:int=None, use_gui:bool=False, tls_state_add:List[str]=None) -> None:
        super().__init__()

        self.tsc_env = TshubEnvironment(
            sumo_cfg=sumo_cfg,
            is_aircraft_builder_initialized=False, 
            is_vehicle_builder_initialized=True, # 用于获得 vehicle 的 waiting time 来计算 reward
            is_traffic_light_builder_initialized=True,
            tls_ids=tls_ids, 
            delta_time=delta_time, # 动作间隔的时间
            num_seconds=num_seconds,
            tls_state_add=tls_state_add,
            tls_action_type='adjust_cycle_duration',
            use_gui=use_gui,
            is_libsumo=(not use_gui), # 如果不开界面, 就是用 libsumo
        )

    def reset(self):
        state_infos = self.tsc_env.reset()
        return state_infos
        
    def step(self, action:Dict[str, Dict[str, List[int]]]):
        action = {'tls': action} # 这里只控制 tls 即可
        states, rewards, infos, dones = self.tsc_env.step(action)
        truncated = dones

        return states, rewards, truncated, dones, infos
    
    def close(self) -> None:
        self.tsc_env._close_simulation()