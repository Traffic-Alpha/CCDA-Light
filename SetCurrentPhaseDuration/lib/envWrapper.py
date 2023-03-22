'''
@Author: WANG Maonan
@Date: 2022-06-16 21:51:03
@Description: 生成对应的 state, action, reward. 同时对 state 进行数据增强
- 这里支持三种动作设计
- 1. discrete: 从 5-60 中选择一个作为绿灯时间, 每次间隔 5s, 共 12 个数字
- 2. minorEdit: 对现有的绿灯时间进行微调, [+k, 0, -k]
- 3. continue: 将 -1-1 的数字映射到 6-80
@LastEditTime: 2022-08-19 20:31:50
'''
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
            action_type:str='discrete',
            mode='train',
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
        self.tls_id = tls_id # 信号灯 id (原本是一个 multi-agent 的环境)
        self.net_files = net_files # 用于 reset net 文件
        self.route_files = route_files # 用于 reset 的 routes 文件
        self.sumo_cfg = None # 默认不修改 sumo config 文件
        self.env_dict = env_dict # {'1': {'net':[...], 'route':[...]}, }
        self.is_movement = is_movement # 特征按照 movement 还是 lane
        self.is_shuffle = is_shuffle # 是否对 obs 进行 shuffle, 进行数据增强
        self.vectorized = vectorized # 自动 reset
        self.action_type = action_type # 动作类型
        # 训练或是测试模式, reset 有所区别
        self.mode = mode # train 模式正常
        self.reset_num = 0 # 第一次 reset 正常

        self.observation_space = spaces.Box(
            low=0, 
            high=5,
            shape=(8,8)
        ) # obs 空间

        assert self.action_type in ['discrete', 'minorEdit', 'continue'], f'{self.action_type} 需要是 discrete, minorEdit, continue'
        if self.action_type == 'discrete':
            self.logger.debug(f'从 5-60 中选择数字')
            self._actions = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60] # 所有可以选择的绿灯时间
            self.action_space = spaces.Discrete(12) # 动作空间
        elif self.action_type == 'minorEdit':
            self.logger.debug(f'微调绿灯时间')
            self.action_space = spaces.Discrete(3) # 动作空间
        else:
            self.logger.debug(f'连续控制')
            self.action_space = spaces.Box(low=-1, high=1, shape=(1,), dtype=np.float32)

        if self.is_movement:
            self.net_movements = dict() # 记录每个 net 的 movement 顺序, {'net1': [m1, m2, ...], '2': [m1, m2, ..]}
            self.net_masks = dict() # 记录每个 net 的相位结构 {'net1': [[1,0,0,1],[0,1,1,0]], 'net2': [[],[]]}
            self.movement_info = dict() # 记录 movement 的信息, {'net1': {'m1':[方向, 车道数], }, 'net2': [[],[]]}
            self.phase_num = 0 # 路网相位数量
        

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

            # 初始化时, 初始化 net 的 movement 组合和 traffic light structure
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
                self.phase_num = self.net_masks[self.env._net].shape[0] # net phase 数量

            # 利用上面的信息处理 obs
            obs = self._process_obs(_observations)
        else:
            obs = 0
        
        self.reset_num += 1 # 重置次数
        return obs


    def step(self, action, K:int=5):
        """将 step 的结果提取, 从 dict 提取为 list

        Args:
            action (_type_): 有三种类型的动作设计
            K (int, optional): 每个相位微调的时间. Defaults to 5.
        """
        phase_index = self.env.traffic_signals[self.tls_id].phase_index
        phase_durations = self.env.traffic_signals[self.tls_id].phase_durations # 当前的相位时间
        if self.action_type == 'discrete':
            action =  {self.tls_id: self._actions[action]}
        elif self.action_type == 'minorEdit':
            assert K < self.env.min_greens[self.tls_id], f'微调时间 {K} 需要小于最小绿灯时间 {self.env.min_greens[self.tls_id]}'
            action = {self.tls_id: phase_durations[phase_index] + K*(action - 1)} # 微调 K 秒
        else:
            action = {self.tls_id: int(37*action+43)}

        observations, rewards, dones, info = self.env.step(action)

        # 处理 obs
        _observations = observations[self.tls_id]
        self.delta_time = _observations['delta_time'] # 上一阶段信号灯周期
        self.phase_id = _observations['phase_id'].index(1) # phase ID, [1, 0, 0, 0], -> 0
        self.last_phase_id = (self.phase_id - 1)%self.phase_num # last phase ID
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
            phase_reward.append(np.max(_phase_reward)) # 求出 phase 中所有 movement 排队的最大值（有排队就应该加大时间）
        
        tls_jam = np.max(phase_reward) # 使用相位中排队最长的
        
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
            phase_index = raw_observation['phase_id'].index(1) # 相位所在 index
            phase_movements = self.net_masks[self.env._net][phase_index] # 得到一个 phase 有哪些 movement 组成的
            for _movement_id, _movement in enumerate(self.net_movements[self.env._net]): # 按照 movment_id 提取
                flow = np.mean(raw_observation['flow'][_movement])/delta_time # 假设每秒通过一辆车
                mean_occupancy = np.mean(raw_observation['mean_occupancy'][_movement])/100
                max_occupancy = np.mean(raw_observation['max_occupancy'][_movement])/100
                movement_duration = raw_observation['duration'][_movement]/100 # 绿灯时长/100
                is_s = self.movement_info[self.env._net][_movement][0] # 是否是直行
                num_lane = self.movement_info[self.env._net][_movement][1]/5 # 车道数(默认不会超过 5 个车道)
                is_now_phase = phase_movements[_movement_id] # now phase id
                min_green = raw_observation['min_green'][0] if is_now_phase else 0 # min green
                observation.append([flow, mean_occupancy, max_occupancy, movement_duration, is_s, num_lane, min_green, is_now_phase]) # 八个特征
            
            # 不是四岔路, 进行不全
            for _ in range(8 - len(observation)):
                self.logger.debug(f'{self.env._net} 进行 obs 补全到 8.')
                observation.append([0]*8)
            
            # 对 obs 进行 shuffle
            if self.is_shuffle:
                np.random.shuffle(observation) # 直接对原始 array 进行修改
            
            observation = np.array(observation, dtype=np.float32)

        return observation


    def _shuffle(self):
        pass