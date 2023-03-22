'''
@Author: WANG Maonan
@Date: 2022-03-15 12:02:58
@Description: 创建 ChoosePhase 环境
@LastEditTime: 2022-09-19 20:54:01
'''
import os
import gym
from typing import List, Callable

from aiolos.AssembleEnvs.KeepChangePhaseEnv import KeepChangePhaseSUMOEnvironment
from stable_baselines3.common.monitor import Monitor
from .envWrapper import env_wrapper

from aiolos.utils.get_abs_path import getAbsPath
from aiolos.trafficLog.initLog import init_logging

def make_env(            
            tls_id:str,
            num_seconds:int,
            sumo_cfg:str,
            net_file:str,
            route_files:List[str],
            log_file:str,
            env_index:int,
            is_libsumo:bool=False,
            trip_info:str=None,
            statistic_output:str=None,
            summary:str=None,
            queue_output:str=None,
            tls_state_add:List[str]=None,
            delta_times:int=5,
            min_green:int=5,
            yellow_times:int=3,
            use_gui:bool=False,
            remote_port:int=None, # 设置端口, 使用 libsumo 不要开启这个
            num_clients:int=1,
            mode:str='train', # 模式, eval 是不会自动 reset 的
            is_shuffle:bool=False # 是否对 movement 进行乱序
        ) -> Callable:
    """
    创建 Set Phase Duration Discrete, 离散的修改 phase duration

    Args:
        tls_id (str): 控制的信号灯的 id
        num_seconds (int): 总的仿真时间, 到达仿真时间则结束
        sumo_cfg (str): sumo config 文件
        net_file (str): net 文件
        route_files (List[str]): route 文件列表, reset 的时候会从中随机选择一个
        trip_info (str, optional): 如果不是 None, 则输出仿真过程的 trip_info, 包含每辆车的信息; 如果是 None, 则不输出. Defaults to None.
        statistic_output (str, optional): 如果不是 None, 则输出仿真过程的 statistic out, 包含仿真总的等待时间等; 如果是 None, 则不输出.. Defaults to None.
        tls_state_add (List, optional): 添加指定的 tls add 文件, 输出信号灯的变化情况. Defaults to None.
        min_green (int, optional): 最小绿灯时间. Defaults to 5.
        use_gui (bool, optional): 是否使用 sumo-gui 打开. Defaults to False.
    """
    def _init() -> gym.Env:
        pathConvert = getAbsPath(__file__)
        init_logging(log_path=pathConvert('../'), prefix=f'PID_{os.getpid()}', log_level=0)

        env = KeepChangePhaseSUMOEnvironment(
                                    sumo_cfg=sumo_cfg,
                                    net_file=net_file,
                                    route_file=route_files[0],
                                    trip_info=trip_info,
                                    statistic_output=statistic_output,
                                    summary=summary,
                                    queue_output=queue_output,
                                    tls_state_add=tls_state_add,
                                    use_gui=use_gui,
                                    is_libsumo=is_libsumo,
                                    tls_list=[tls_id],
                                    num_seconds=num_seconds,
                                    delta_times={tls_id:delta_times},
                                    min_greens={tls_id:min_green},
                                    yellow_times={tls_id:yellow_times},
                                    is_movement=True,
                                    remote_port=remote_port, # 指定之后可以与 Carla 联动
                                    num_clients=num_clients # 如果要和 carla 联动, 这里需要设置为 2
                                ) # 创建 Next ot Not 环境
        env = env_wrapper(
            env=env,
            tls_id=tls_id, 
            route_files=route_files, 
            is_movement=True,
            mode=mode,
            is_shuffle=is_shuffle
        )
        return Monitor(env, filename=f'{log_file}/{env_index}')
        
    return _init