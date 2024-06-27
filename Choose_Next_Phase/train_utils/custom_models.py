'''
@Author: WANG Maonan
@Date: 2024-05-01 19:17:16
@Description: Custom Model
@LastEditTime: 2024-06-18 22:37:07
'''
import torch.nn as nn
import gymnasium as gym
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor

class CustomModel(BaseFeaturesExtractor):
    def __init__(self, observation_space: gym.Space, features_dim: int = 16):
        """特征提取网络
        """
        super().__init__(observation_space, features_dim)
        net_shape = observation_space.shape[-1] # 12

        self.embedding = nn.Sequential(
            nn.Linear(net_shape, 32),
            nn.ReLU(),
        ) # 5*12 -> 5*32
        
        self.lstm = nn.LSTM(
            input_size=32, hidden_size=64,
            num_layers=1, batch_first=True
        )
        self.relu = nn.ReLU()

        self.output = nn.Sequential(
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, features_dim)
        )

    def forward(self, observations):
        embedding = self.embedding(observations)

        output, (hn, cn) = self.lstm(embedding)
        hn = hn.view(-1, 64)
        hn = self.relu(hn)
        
        output = self.output(hn)
        return output