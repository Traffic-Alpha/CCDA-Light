'''
@Author: WANG Maonan
@Date: 2024-05-01 19:17:16
@Description: Custom Model
@LastEditTime: 2024-05-01 19:38:01
'''
import torch.nn as nn
import gymnasium as gym
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor

class CustomModel(BaseFeaturesExtractor):
    def __init__(self, observation_space: gym.Space, features_dim: int = 16):
        """特征提取网络
        """
        super().__init__(observation_space, features_dim)
        net_shape = observation_space.shape[-1] # 64

        self.embedding = nn.Sequential(
            nn.Linear(net_shape, 128), # 64 -> 128
            nn.ReLU(),
            nn.Linear(128, 256), # 128 -> 256
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, features_dim)
        )

    def forward(self, observations):
        embedding = self.embedding(observations)
        return embedding