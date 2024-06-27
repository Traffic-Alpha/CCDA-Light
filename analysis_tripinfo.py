'''
@Author: WANG Maonan
@Date: 2024-06-25 23:57:16
@Description: 分析 TripInfo 文件
@LastEditTime: 2024-06-28 00:37:29
'''
import argparse
from tshub.utils.init_log import set_logger
from tshub.utils.get_abs_path import get_abs_path
from tshub.sumo_tools.analysis_output.tripinfo_analysis import TripInfoAnalysis

# 初始化日志
current_file_path = get_abs_path(__file__)
set_logger(current_file_path('./'), file_log_level="INFO")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process delta_time.')
    parser.add_argument('--action_type', type=str, default='Choose_Next_Choose', help='The name of action type.')
    parser.add_argument('--delta_time', type=int, default=None, help='The delta time value.')
    args = parser.parse_args() # Parse the arguments
    delta_time = args.delta_time # Use the delta_time argument
    action_type = args.action_type

    # 解析 tripinfo xml 文件
    if delta_time == None:
        tripinfo_file = current_file_path(f"./{action_type}/exp_output/tripinfo.out_1.xml")
    else:
        tripinfo_file = current_file_path(f"./{action_type}/exp_output/{delta_time}/tripinfo.out_1.xml")
    tripinfo_parser = TripInfoAnalysis(tripinfo_file)
    print('===', action_type, '===')
    tripinfo_parser.print_stats()