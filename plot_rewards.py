'''
@Author: WANG Maonan
@Date: 2024-04-15 21:58:59
@Description: 绘制 Reward Curve with Standard Deviation
@LastEditTime: 2024-06-28 00:12:36
'''
import argparse
from tshub.utils.get_abs_path import get_abs_path
from tshub.utils.plot_reward_curves import plot_reward_curve
path_convert = get_abs_path(__file__)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process delta_time.')
    parser.add_argument('--action_type', type=str, default='Choose_Next_Choose', help='The name of action type.')
    parser.add_argument('--delta_time', type=int, default=None, help='The delta time value.')
    args = parser.parse_args() # Parse the arguments
    delta_time = args.delta_time # Use the delta_time argument
    action_type = args.action_type

    # 开始绘图
    if delta_time == None: 
        log_files = [
            path_convert(f'./{action_type}/log/{i}.monitor.csv')
            for i in range(20)
        ]
    else:
        log_files = [
            path_convert(f'./{action_type}/log/{delta_time}/{i}.monitor.csv')
            for i in range(20)
        ]
    output_file = path_convert(f'./reward_{action_type}_{delta_time}.png')
    plot_reward_curve(log_files, output_file, window_size=2, fill_outliers=False)