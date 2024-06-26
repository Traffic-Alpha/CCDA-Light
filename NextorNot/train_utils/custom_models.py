'''
@Author: WANG Maonan
@Date: 2024-05-01 19:17:16
@Description: Custom Model
LastEditTime: 2024-06-26 23:38:29
'''
import torch
import torch.nn as nn
import gymnasium as gym
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor

class CustomModel(BaseFeaturesExtractor):
    def __init__(self, observation_space: gym.Space, features_dim: int = 16):
        """特征提取网络, 这里包含两个部分:
        - 路口的动态特征
        - 当前信号灯的特征
        """
        super().__init__(observation_space, features_dim)
        net_shape = observation_space["occ"].shape[-1] # 12
        # 用于处理 traffic phase info 的网络
        self.phase_embedding = nn.Sequential(
            nn.Linear(12, 32),
            nn.ReLU(),
            nn.Linear(32, 12),
        )

        # 用于处理 occ 的网络
        self.embedding = nn.Sequential(
            nn.Linear(net_shape, 32),
            nn.ReLU(),
        ) # 5*12 -> 5*32
        
        self.lstm = nn.LSTM(
            input_size=32, hidden_size=64,
            num_layers=1, batch_first=True
        )
        self.relu = nn.ReLU()

        # occ+phase_info 特征结合
        self.output = nn.Sequential(
            nn.Linear(64+12, 32),
            nn.ReLU(),
            nn.Linear(32, features_dim)
        )

    def forward(self, observations):
        occ, phase_info = observations["occ"], observations["phase_info"]
        # 处理 phase info
        tf_embedding = self.phase_embedding(phase_info)

        # 处理 occ 特征
        embedding = self.embedding(occ)
        output, (hn, cn) = self.lstm(embedding)
        hn = hn.view(-1, 64)
        hn = self.relu(hn)

        # 两者结合, 得到全局特征
        int_embedding = torch.cat((hn, tf_embedding), dim=1)
        output = self.output(int_embedding)
        return output