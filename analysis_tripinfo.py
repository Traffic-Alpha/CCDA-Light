'''
@Author: WANG Maonan
@Date: 2024-06-25 23:57:16
@Description: 分析 TripInfo 文件
LastEditTime: 2024-06-27 13:20:54
'''
from tshub.utils.init_log import set_logger
from tshub.utils.get_abs_path import get_abs_path
from tshub.sumo_tools.analysis_output.tripinfo_analysis import TripInfoAnalysis

# 初始化日志
current_file_path = get_abs_path(__file__)
set_logger(current_file_path('./'), file_log_level="INFO")

if __name__ == '__main__':
    action_types = ['ChooseNextPhase', 'NextorNot']
    for action_type in action_types:
        tripinfo_file = current_file_path(f"./{action_type}/exp_output/tripinfo.out_1.xml")
        tripinfo_parser = TripInfoAnalysis(tripinfo_file)
        print('===', action_type, '===')
        tripinfo_parser.print_stats()