'''
@Author: WANG Maonan
@Date: 2022-04-12 12:02:58
@Description: PhaseNet, 每个 phase 为一个 agent
@LastEditTime: 2022-06-17 17:16:39
'''
import gym
import numpy as np
from gym import spaces

import torch
import torch.nn as nn
from stable_baselines3.common.torch_layers import BaseFeaturesExtractor

class IntersectionInfo(BaseFeaturesExtractor):
    def __init__(self, observation_space: gym.Space, features_dim: int = 64):
        """特征提取网络
        """
        super().__init__(observation_space, features_dim)
        net_shape = observation_space.shape # 每个 movement 的特征数量, 8 个 moovement, 就是 (1, 8, K)

        self.view_conv = nn.Sequential(
            nn.Conv2d(1, 128, kernel_size=(1, net_shape[-1]), padding=0), # 1*8*K -> 128*8*1
            nn.ReLU(),
            nn.Conv2d(128, 256, kernel_size=(8,1), padding=0), # 128*8*1 -> 256*1*1
            nn.ReLU(),
        )
        view_out_size = self._get_conv_out(net_shape)

        self.fc = nn.Sequential(
            nn.Linear(view_out_size, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, features_dim)
        )

    def _get_conv_out(self, shape):
        o = self.view_conv(torch.zeros(1, 1, *shape))
        return int(np.prod(o.size()))


    def forward(self, observations):
        observations.unsqueeze_(1) # 从 (N, 8, K) --> (N, 1, 8, K)
        batch_size = observations.size()[0]
        conv_out = self.view_conv(observations).view(batch_size, -1)
        return self.fc(conv_out)