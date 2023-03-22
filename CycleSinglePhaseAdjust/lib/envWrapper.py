'''
@Author: WANG Maonan
@Date: 2022-08-10 21:53:52
@Description: 每个周期只可以调整一个相位的时长
LastEditTime: 2022-08-19 13:09:19
'''
import itertools
import logging
import gym
import numpy as np
from typing import List, Dict
from gym import spaces

class env_wrapper(gym.Wrapper):
    def __init__(
            self, 
            env, # 传入环境
            tls_id, 
            mode='train', # mode 是 train 会自动进行 reset
            duration_range=[[-5,5],[-5,5],[-5,5],[-5,5]], # 自定义每一个 phase 的变化范围, 这里只有两个
            net_files:List[str]=None, 
            route_files:List[str]=None,
            env_dict:Dict[str,str]=None,
            is_movement:bool=False,
            is_shuffle:bool=False,
            vectorized:bool=False,
        ) -> None:
        super(env_wrapper, self).__init__(env)
        self.logger = logging.getLogger(__name__)
        self.env = env
        self.duration_range = duration_range
        self.tls_id = tls_id # 信号灯 id (原本是一个 multi-agent 的环境)
        self.net_files = net_files # 用于 reset net 文件
        self.route_files = route_files # 用于 reset 的 routes 文件
        self.sumo_cfg = None # 默认不修改 sumo config 文件
        self.env_dict = env_dict # {'1': {'net':[...], 'route':[...]}, }
        self.is_movement = is_movement # 特征按照 movement 还是 lane
        self.is_shuffle = is_shuffle # 是否对 obs 进行 shuffle, 进行数据增强
        self.vectorized = vectorized # 自动 reset
        # 训练或是测试模式, reset 有所区别
        self.mode = mode # train 模式正常
        self.reset_num = 0 # 第一次 reset 正常

        # 重写 observation space 和 action space
        self.observation_space = spaces.Box(
            low=-np.inf, 
            high=np.inf,
            shape=(8,7)
        ) # obs 空间
        net_phase2movements = self.env.traffic_signals[self.tls_id].phase2movements
        self.phase_num = len(net_phase2movements) # 路网相位数量

        _actions = [(0,)*len(duration_range)] # 存储所有的动作组合, 首先是不变得动作
        for phase_index, phase_range in enumerate(duration_range): 
            t = [[0] for i in range(len(duration_range))] # 生成 [[0], [0], [0], [0]] 的列表
            t[phase_index] = phase_range # 修改为 [[0], [-5,5], [0], [0]] 的列表
            _actions += sorted(list(itertools.product(*t))) # 组合得到 [[0,-5,0,0], [0,5,0,0]] 并添加到 _actions
        self.actions = _actions.copy()
        self.logger.debug(f'动作为 {self.actions}.')
        self.action_space = spaces.Discrete(len(self.actions))

        if self.is_movement:
            self.net_movements = dict() # 记录每个 net 的 movement 顺序, {'net1': [m1, m2, ...], '2': [m1, m2, ..]}
            self.net_masks = dict() # 记录每个 net 的相位结构 {'net1': [[1,0,0,1],[0,1,1,0]], 'net2': [[],[]]}
            self.movement_info = dict() # 记录 movement 的信息, {'net1': {'m1':[方向, 车道数], }, 'net2': [[],[]]}
            
        

    def reset(self, ):
        """将 reset 返回的 obs 从 dict->list
        - 支持 reset 时候随机选择 route 文件和 net 文件
        - 提取一些 movement 的信息
        """
        if (self.mode == 'train') or (self.reset_num == 0):
            self.sim_steps = 0 # 仿真进行了多少步

            if self.env_dict is not None:
                _env_id = np.random.choice(list(self.env_dict.keys()))
                self.sumo_cfg = self.env_dict[_env_id]['cfg']
                self.net_files = self.env_dict[_env_id]['net']
                self.route_files = self.env_dict[_env_id]['route']

            # 随机选择 route 和 net
            if (self.route_files is not None) and (self.net_files is not None): # net 和 route 都不是 None
                # 随机一个 net 和 route 文件
                net_file = np.random.choice(self.net_files, 1)[0]
                route_file = np.random.choice(self.route_files, 1)[0]
                observations = self.env.reset(sumo_cfg=self.sumo_cfg, net_file=net_file, route_file=route_file)
            elif (self.route_files is not None) and (self.net_files is None): # route!=None, net=None
                route_file = np.random.choice(self.route_files, 1)[0]
                observations = self.env.reset(sumo_cfg=self.sumo_cfg, route_file=route_file)    
            elif (self.route_files is None) and (self.net_files is not None): # route=None, net!=None
                net_file = np.random.choice(self.net_files, 1)[0]
                observations = self.env.reset(sumo_cfg=self.sumo_cfg, net_file=net_file)                   
            else: # 不随机 route 文件
                observations = self.env.reset()

            _observations = observations[self.tls_id]

            # 初始化时, 初始化 net 的 movement 组合和 traffic light structure (只需要第一次 reset 的时候更新即可)
            if (self.is_movement) and (self.env._net not in self.net_movements): # 初始化时提取每个 net 的 movement
                net_phase2movements = self.env.traffic_signals[self.tls_id].phase2movements

                # 初始化 net_movements
                _net_movement = list() # 存储每个 net 中 movement 的顺序
                for _, phase_movement_list in net_phase2movements.items():
                    for phase_movement in phase_movement_list: # 0: ['gsndj_s4--s', 'gsndj_n7--s', 'None--None', 'gsndj_s4--r', 'gsndj_n7--r']
                        direction = phase_movement.split('--')[1] # 获得方向
                        if direction not in ['None', 'r']: # 去除 右转 和 None
                            _net_movement.append(phase_movement)
                self.net_movements[self.env._net] = sorted(list(set(_net_movement)))

                # 初始化 net_masks
                _net_mask = list() # 存储 net mask
                for phase_index, phase_movement_list in net_phase2movements.items(): # {0: ['gsndj_s4--s', 'gsndj_n7--s', 'None--None', 'gsndj_s4--r', 'gsndj_n7--r']， 1: []}
                    _phase_mask = [0]*len(self.net_movements[self.env._net]) # 每个 phase 由哪些 movement 组成
                    for phase_movement in phase_movement_list: # ['gsndj_s4--s', 'gsndj_n7--s', 'None--None', 'gsndj_s4--r', 'gsndj_n7--r']
                        if phase_movement in self.net_movements[self.env._net]: # self.net_movements 是没有 右转 和 None
                            _phase_mask[self.net_movements[self.env._net].index(phase_movement)] = 1 # 对应位置转换为 1
                    _net_mask.append(_phase_mask.copy())
                self.net_masks[self.env._net] = np.array(_net_mask.copy(), dtype=np.int8)

                # 初始化 movement_info, 统计每个 movement 的「方向」和「车道数」
                _movement_info = dict()
                for movement_id, movement_flow in _observations['flow'].items():
                    _direction = movement_id.split('--')[1] # 获得方向
                    if _direction not in ['None', 'r']: # 去除 右转 和 None
                        _is_s = 1 if _direction=='s' else 0 # 是否是直行, 1=s, 0=l
                        _lane_num = len(movement_flow) # 车道数
                        _movement_info[movement_id] = (_is_s, _lane_num) # 统计每个 movement 的「方向」和「车道数」
                self.movement_info[self.env._net] = _movement_info

                # 初始化 phase 数量
                assert self.phase_num == self.net_masks[self.env._net].shape[0], f'Phase 数量没有对齐.' # net phase 数量

            # 利用上面的信息处理 obs
            obs = self._process_obs(_observations)
        else:
            obs = 0
        
        self.reset_num += 1 # 重置次数
        return obs


    def step(self, action):
        """这里 action 为索引, 是一维的, 将多维离散的动作转换为了完全离散的. 
        例如是二相位, 每个相位可以调节的时间为 [[-5, 5], [-5, 5]], 
        于是一共有 5 种不同的可能性, 所以动作空间是 5. 下面是 5 种可能（这里每次只有一个相位可以发生改变）:
        [ 
            (-5, 0), 
            (0, -5), 
            (0, 0), 
            (0, 5), 
            (5, 0), 
        ]
        Args:
            action (int): 为 action 的索引
        """
        _action = list(self.actions[action]) # 得到每一个相位要修改的时间
        action = {self.tls_id: _action} # 因为只有一个路口, 构建一个字典
        observations, rewards, dones, info = self.env.step(action)
        # 是否将动作输出到控制台上
        # self.logger.info(f'Action, {action}; Green Duration, {self.env.traffic_signals[self.tls_id].get_green_durations()}.') # 输出详细的动作

        # 处理 obs
        _observations = observations[self.tls_id]
        self.delta_time = _observations['delta_time'] # 上一阶段信号灯周期
        observation = self._process_obs(_observations)

        # 处理 reward, 提取每个 phase 的 reward
        single_agent_reward = rewards[self.tls_id] # 单个 agent 的 reward, 这里是 jam list
        process_reward = self._process_reward(single_agent_reward)

        if (self.vectorized) and (dones['__all__']): # 结束, 自动 reset
            _ = self.reset() # 重置
            return observation, process_reward, dones['__all__'], info[self.tls_id]
        
        return observation, process_reward, dones['__all__'], info


    def _process_reward(self, raw_reward):
        """整个路口的排队, 希望整个路口的排队最短
        """
        # 所有车道的排队全部用到
        tls_reward = list()
        for _, jam in raw_reward.items():
            tls_reward.extend(jam)
        
        return -np.mean(tls_reward)/100

        # 下面是只使用最大相位的排队
        """
        phase_reward = list() # 计算出每个 phase 对应的平均排队
        for _phase_mask in self.net_masks[self.env._net]: # _phase_mask 为 [[0, 0, 0, 1, 1, 0, 0, 0], [1, 0, 1, 0, 0, 0, 0, 0], ..., ]
            _phase_reward = list()
            for _movement_index in np.where(_phase_mask==1)[0]: # 找出 1 对应的 movement
                _movement_name = self.net_movements[self.env._net][_movement_index]
                _phase_reward.append(np.mean(raw_reward[_movement_name])/60) # 一个 movement 可能由多个车道组成, 除 60 转换为每秒的车
            phase_reward.append(np.sum(_phase_reward)) # 求出 phase 中所有 movement 排队的最大值（有排队就应该加大时间）
        
        tls_jam = np.sum(phase_reward) # 使用相位中排队最长的
        
        return -tls_jam # 注意这里 reward 的计算,
        """
    
    
    def _process_obs(self, raw_observation):
        """处理 observation, 将 dict 转换为 array
        - 如果 movement 小于 8, 则进行填充
        - 对 state 进行 shuffle
        - state 包含以下几个部分, [flow, mean_occupancy, max_occupancy, duration, is_s, num_lane, mingreen, is_now_phase]
        """
        if self.is_movement: # 按照 movment 提取信息
            observation = list()
            delta_time = raw_observation['delta_time']
            for _movement_id, _movement in enumerate(self.net_movements[self.env._net]): # 按照 movment_id 提取
                flow = np.mean(raw_observation['flow'][_movement])/delta_time # 假设每秒通过一辆车
                mean_occupancy = np.mean(raw_observation['mean_occupancy'][_movement])/100
                max_occupancy = np.mean(raw_observation['max_occupancy'][_movement])/100
                movement_duration = raw_observation['duration'][_movement]/100 # 绿灯时长/100
                is_s = self.movement_info[self.env._net][_movement][0] # 是否是直行
                num_lane = self.movement_info[self.env._net][_movement][1]/5 # 车道数(默认不会超过 5 个车道)
                min_green = raw_observation['min_green'][0]# min green
                observation.append([flow, mean_occupancy, max_occupancy, movement_duration, is_s, num_lane, min_green])
            
            # 不是四岔路, 进行不全
            for _ in range(8 - len(observation)):
                self.logger.debug(f'{self.env._net} 进行 obs 补全到 8 个 movement.')
                observation.append([0]*7)
            
            # 对 obs 进行 shuffle
            if self.is_shuffle:
                np.random.shuffle(observation) # 直接对原始 array 进行修改
            
            observation = np.array(observation, dtype=np.float32)

        return observation


    def _shuffle(self):
        pass