'''
@Author: WANG Maonan
@Date: 2022-06-16 21:36:37
@Description: 训练网络, 测试分为四个阶段:
- 使用同一个路网, 不进行 shuffle
- 使用同一个路网, 进行 shuffle
- 使用同一个路网, 但是包含不同的信号灯结构, 且进行 shuffle
- 使用不同的路网, 包含不同的信号灯结构, 且进行 shuffle
- srun -J SetPhaseDuration -p CPU -n 1 -c 30 -w st-node-158 python train.py > node_158.log &
@LastEditTime: 2022-08-19 20:39:13
'''
import os
import argparse
from typing import Callable
import torch
from stable_baselines3 import A2C, PPO
from stable_baselines3.common.callbacks import CallbackList, EvalCallback, StopTrainingOnNoModelImprovement, CheckpointCallback
from stable_baselines3.common.vec_env import SubprocVecEnv, VecNormalize
from stable_baselines3.common.callbacks import BaseCallback
from lib import makeENV, models

from aiolos.utils.get_abs_path import getAbsPath
from aiolos.trafficLog.initLog import init_logging

class VecNormalizeCallback(BaseCallback):
    """保存环境标准化之后的值
    """
    def __init__(self, save_freq: int, save_path: str, name_prefix: str = "vec_normalize", verbose: int = 0):
        super(VecNormalizeCallback, self).__init__(verbose)
        self.save_freq = save_freq
        self.save_path = save_path
        self.name_prefix = name_prefix

    def _init_callback(self) -> None:
        # Create folder if needed
        if self.save_path is not None:
            os.makedirs(self.save_path, exist_ok=True)

    def _on_step(self) -> bool:
        if self.n_calls % self.save_freq == 0:
            path = os.path.join(self.save_path, f"{self.name_prefix}_{self.num_timesteps}_steps.pkl")
            self.model.get_vec_normalize_env().save(path)
            if self.verbose > 1:
                print(f"Saving VecNormalize to {path}")
        return True


class BestVecNormalizeCallback(BaseCallback):
    """保存最优的环境
    """
    def __init__(self, save_path: str, verbose: int = 0):
        super(BestVecNormalizeCallback, self).__init__(verbose)
        self.save_path = save_path

    def _init_callback(self) -> None:
        # Create folder if needed
        if self.save_path is not None:
            os.makedirs(self.save_path, exist_ok=True)

    def _on_step(self) -> bool:
        path = os.path.join(self.save_path, f"best_vec_normalize.pkl")
        self.model.get_vec_normalize_env().save(path)
        if self.verbose > 1:
            print(f"Saving Best VecNormalize to {path}")
        return True


def linear_schedule(initial_value: float) -> Callable[[float], float]:
    """
    Linear learning rate schedule.

    :param initial_value: Initial learning rate.
    :return: schedule that computes
      current learning rate depending on remaining progress
    """
    def func(progress_remaining: float) -> float:
        """
        Progress will decrease from 1 (beginning) to 0.

        :param progress_remaining:
        :return: current learning rate
        """
        return progress_remaining * initial_value

    return func


if __name__ == '__main__':
    pathConvert = getAbsPath(__file__)
    init_logging(log_path=pathConvert('./'), log_level=0)

    # 路网参数
    parser = argparse.ArgumentParser("Run Choose Next Phase experiments.")
    parser.add_argument("--net_folder", type=str, required=True, help="路网的文件夹.")
    parser.add_argument("--net_id", type=str, required=True, help="不同的信号灯组合.")
    parser.add_argument("--route_id", type=str, required=True, help="不同的流量.")
    parser.add_argument("--delta_times", required=True, help="做动作的间隔.")

    args = parser.parse_args()
    net_folder, net_id, route_id = args.net_folder, args.net_id, args.route_id # fluctuation, stable
    if args.delta_times == 'None':
        delta_times = None
    else:
        delta_times = int(args.delta_times) # 做动作的间隔
    # net_folder, net_id, route_id = 'fourWay', '4phases', 'fluctuation' # fluctuation, stable
    # delta_times = 5 # 做动作的间隔

    # #######
    # 训练参数
    # #######
    NUM_CPUS = 30
    EPISODE_STEP = int(7000/35) if delta_times==None else int(7000/delta_times) # 每一次仿真的交互次数, 7000/delta time (总的仿真时间/每一步的时间)
    EVAL_FREQ = EPISODE_STEP*2 # 测试的频率 (不需要乘 NUM_CPUS)
    SAVE_FREQ = EPISODE_STEP*2 # 保存的频率

    N_STEPS = EPISODE_STEP # 多少 steps 记录一次结果 7000/NUM_CPUS
    N_EPOCHS = 4
    BATCH_SIZE = 256
    SHFFLE = False # 是否进行数据增强
    ACTION_TYPE = 'discrete' # 'discrete', 'minorEdit', 'continue'
    MODEL_NAME = 'PPO' # 后面选择算法
    MODEL_PATH = pathConvert(f'./models/{delta_times}/{net_folder}/{net_id}/{route_id}/')
    LOG_PATH = pathConvert(f'./log/{delta_times}/{net_folder}/{net_id}/{route_id}/') # 存放仿真过程的数据, 每个仿真每一轮的数据
    TENSORBOARD_PATH = pathConvert('./tensorboard_logs/') # tensorboard 的存储路径
    if not os.path.exists(MODEL_PATH):
        os.makedirs(MODEL_PATH)
    if not os.path.exists(TENSORBOARD_PATH):
        os.makedirs(TENSORBOARD_PATH)
    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH)
        
    # #########
    # 初始化环境
    # #########
    tls_id = 'htddj_gsndj'
    sumo_cfg = pathConvert(f'../nets/{net_folder}/env/single_junction.sumocfg')
    net_file = pathConvert(f'../nets/{net_folder}/env/{net_id}.net.xml')
    route_list = [pathConvert(f'../nets/{net_folder}/routes/{route_id}.rou.xml')]

    params = {
        'tls_id':tls_id,
        'num_seconds':7000,
        'sumo_cfg':sumo_cfg,
        'net_file':net_file,
        'route_files':route_list,
        'is_shuffle':SHFFLE,
        'is_libsumo':True,
        'use_gui':False,
        'min_green':5,
        'delta_times':delta_times,
        'log_file':LOG_PATH,
        'action_type':ACTION_TYPE,
    }
    env = SubprocVecEnv([makeENV.make_env(env_index=f'{i}', **params) for i in range(NUM_CPUS)])
    env = VecNormalize(env, norm_obs=True, norm_reward=True) # 进行标准化 (不对 obs 进行标准化)
    
    # ########
    # callback
    # ########
    stop_callback = StopTrainingOnNoModelImprovement(
        max_no_improvement_evals=15,
        verbose=True
    ) # 何时停止

    # 保存 best model 和 best vec norm
    best_vec_normalize_callback = BestVecNormalizeCallback(save_path=MODEL_PATH)
    eval_callback = EvalCallback(
        env,
        eval_freq=EVAL_FREQ, # 一把交互 30000/5=6000
        best_model_save_path=MODEL_PATH,
        callback_after_eval=stop_callback, # 每次验证之后调用, 是否已经不变了, 需要停止
        callback_on_new_best=best_vec_normalize_callback, # 有了新的模型之后保存 vec
        verbose=1
    ) # 保存最优模型

    checkpoint_callback = CheckpointCallback(
        save_freq=SAVE_FREQ,
        save_path=MODEL_PATH,
    ) # 定时保存模型
    vec_normalize_callback = VecNormalizeCallback(
        save_freq=SAVE_FREQ,
        save_path=MODEL_PATH,
    ) # 保存环境参数
    callback_list = CallbackList([eval_callback])


    # ###########
    # start train
    # ###########
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    policy_kwargs = dict(
        features_extractor_class=models.IntersectionInfo,
        features_extractor_kwargs=dict(features_dim=32), # features_dim 提取的特征维数
    )
    if MODEL_NAME == 'A2C':
        model = A2C(
            "MlpPolicy", 
            env, 
            verbose=True, 
            policy_kwargs=policy_kwargs, 
            learning_rate=linear_schedule(7e-4), 
            tensorboard_log=TENSORBOARD_PATH, 
            device=device
        ) # 存放 log 的目录
    else:
        model = PPO(
            "MlpPolicy", 
            env, 
            verbose=True, 
            policy_kwargs=policy_kwargs, 
            n_steps=N_STEPS,
            n_epochs=N_EPOCHS,
            batch_size=BATCH_SIZE,
            learning_rate=linear_schedule(3e-4), 
            tensorboard_log=TENSORBOARD_PATH, 
            device=device
        )
    model.learn(total_timesteps=1e6, tb_log_name=f'{delta_times}_{net_folder}_{net_id}_{route_id}', callback=callback_list) # log 的名称

    # #################
    # 保存 model 和 env
    # #################
    env.save(f'{MODEL_PATH}/last_vec_normalize.pkl')
    model.save(f'{MODEL_PATH}/last_model.zip')
    print('训练结束, 达到最大步数.')
    
    env.close()