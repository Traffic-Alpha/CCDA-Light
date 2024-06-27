'''
@Author: WANG Maonan
@Date: 2024-05-01 17:29:57
@Description: 处理环境的 state, action 和 reward
@LastEditTime: 2024-06-27 22:57:52
'''
import numpy as np
import gymnasium as gym
from gymnasium.core import Env
from typing import Any, SupportsFloat, Tuple, Dict, List

from env_utils.occupancy_list import OccupancyList

def generate_single_element_combinations(N, choices):
    all_combinations = [[0] * N]  # 首先添加全零列表

    for i in range(N):
        for value in choices:
            if value != 0:  # 只有非零值时才设置，避免重复生成全零列表
                combination = [0] * N
                combination[i] = value
                all_combinations.append(combination)

    return all_combinations


class TSCEnvWrapper(gym.Wrapper):
    """TSC Env Wrapper for single junction with tls_id
    """
    def __init__(self, env: Env, tls_id:str) -> None:
        super().__init__(env)
        self.tls_id = tls_id # 单路口的 id
        self.movement_ids = None
        self.phase2movements = None

        self.reset_num = 0

        self.modify_range = [-5, 0, 5] # 每次修改的范围可以从这三个数字里面选择
        self.all_actions = generate_single_element_combinations(N=4, choices=self.modify_range)
        self.keys_order = ['phase_duration', 'average', 'max', 'min', 'std_dev', 'median'] # 将这些信息拼接起来
        self.occupancy = OccupancyList() # 记录一段仿真内的 occ 结果
        self.rewards = [] # 记录每个时刻的奖励, 用于计算平均值
        
    @property
    def action_space(self):
        return gym.spaces.Discrete(len(self.all_actions))
    
    @property
    def observation_space(self):
        obs_space = gym.spaces.Box(
            low=np.zeros((64,)),
            high=np.ones((64,)),
            shape=(64,)
        ) # 5*12+4=64
        return obs_space
    
    def get_state(self):
        """获得 state, 主要进行以下操作:
        1. 获得统计值 (包含路口信息+相位信息)
        2. 拼接为 5*12 的向量
        3. 清空 occupancy_list
        """
        raw_state = self.occupancy.calculate_statistics() # 统计占有率的不同指标
        raw_state['phase_duration'] = self.env.tsc_env.scene_objects['tls'].traffic_lights[self.tls_id].tls_action.get_green_durations() # 在 raw_state 加入相位时长的信息
        raw_state['phase_duration'] = [i/60 for i in raw_state['phase_duration']] # 对 phase duration 进行归一化
        state = np.concatenate([np.array(raw_state[key], dtype=np.float32).flatten() for key in self.keys_order])
        self.occupancy.reset_occupancies()
        return state

    # Wrapper
    def state_wrapper(self, state):
        """返回当前每个 movement 的 occupancy
        """
        occupancy = state['tls'][self.tls_id]['last_step_occupancy']
        can_perform_action = state['tls'][self.tls_id]['can_perform_action']
        return occupancy, can_perform_action
    
    def reward_wrapper(self, states) -> float:
        """返回整个路口的排队长度的平均值
        """
        waiting_times = [veh['waiting_time'] for veh in states['vehicle'].values()] # 这里需要优化所有车的等待时间, 而不是停止车辆的等待时间
        
        return -np.mean(waiting_times) if waiting_times else 0


    def reset(self, seed=1) -> Tuple[Any, Dict[str, Any]]:
        """reset 时初始化 (1) 静态信息; (2) 动态信息
        """
        state =  self.env.reset()
        # 初始化路口静态信息
        self.movement_ids = state['tls'][self.tls_id]['movement_ids']
        self.phase2movements = state['tls'][self.tls_id]['phase2movements']
        # 处理路口动态信息
        occupancy, _ = self.state_wrapper(state=state)
        self.occupancy.add_occupancy(occupancy.copy()) # 添加占有率
        state = self.get_state() # 获得状态
        return state, {'step_time':0}
    

    def step(self, raw_action: int) -> Tuple[Any, SupportsFloat, bool, bool, Dict[str, Any]]:
        can_perform_action = False
        while not can_perform_action:
            action = {self.tls_id: self.all_actions[raw_action]} # 构建单路口 action 的动作
            states, rewards, truncated, dones, infos = super().step(action) # 与环境交互
            occupancy, can_perform_action = self.state_wrapper(state=states) # 处理每一帧的数据

            # 记录每一时刻的数据
            self.occupancy.add_occupancy(occupancy.copy())
            single_step_reward = self.reward_wrapper(states=states)
            self.rewards.append(single_step_reward)
            
        
        # 处理好的时序的 state
        state = self.get_state()
        rewards = np.mean(self.rewards)
        self.rewards = [] # 重新初始化 rewards

        return state, rewards, truncated, dones, infos
    
    def close(self) -> None:
        return super().close()