'''
@Author: WANG Maonan
@Date: 2024-06-25 23:59:49
@Description: 绘制 Traffic Phase Duration 曲线
@LastEditTime: 2024-06-28 00:43:09
'''
import argparse
from tshub.utils.init_log import set_logger
from tshub.utils.get_abs_path import get_abs_path
from tshub.sumo_tools.analysis_output.tls_program_visualization import TLSProgram_PDVis

current_file_path = get_abs_path(__file__)
set_logger(current_file_path('./'), file_log_level="INFO")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process delta_time.')
    parser.add_argument('--action_type', type=str, default='Choose_Next_Choose', help='The name of action type.')
    parser.add_argument('--delta_time', type=int, default=None, help='The delta time value.')
    args = parser.parse_args() # Parse the arguments
    delta_time = args.delta_time # Use the delta_time argument
    action_type = args.action_type

    # Start Analysis tls_programs
    if delta_time == None:
        tls_program_file = current_file_path(f'./{action_type}/exp_output/add/tls_programs.out_1.xml')
    else:
        tls_program_file = current_file_path(f'./{action_type}/exp_output/{delta_time}/add/tls_programs.out_1.xml')
    tls_analysis = TLSProgram_PDVis(tls_program_file)

    # 将所有的 Traffic Phase 绘制在一起
    directions_state = [
        'grrrrrgGGGrgrrrgGGr',
        'GrrrrrGrrrGGrrrGrrG',
        'GGGGrrGrrrrGGGrGrrr',
        'GrrrGGGrrrrGrrGGrrr'
    ]
    tls_analysis.plot_allphase_ratio(
        directions_state, traffic_light_duration=120, 
        image_path=current_file_path(f"./all_phase_duration_{action_type}_{delta_time}.pdf")
    )

    # 绘制指定的 Traffic Phase Duration (使用折线图)
    directions_state = [
        'grrrrrgGGGrgrrrgGGr',
        'GGGGrrGrrrrGGGrGrrr',
    ]
    tls_analysis.plot_phase_ratio_line(
        phase_strs=directions_state,
        phase_label=['NS-SN', 'WE-EW'],
        fig_text=f'{action_type}',
        image_path=current_file_path(f"./phase_duration_line_{action_type}_{delta_time}.pdf")
    )