'''
@Author: WANG Maonan
@Date: 2024-05-05 23:33:07
@Description: 分析 rou 文件
@LastEditTime: 2024-05-05 23:58:08
'''
from tshub.utils.init_log import set_logger
from tshub.utils.get_abs_path import get_abs_path
from tshub.sumo_tools.analysis_output.route_analysis import count_vehicles_for_multiple_edges, plot_vehicle_counts

# 初始化日志
current_file_path = get_abs_path(__file__)
set_logger(current_file_path('./'))

route_file = current_file_path('./fourWay/routes/fluctuation.rou.xml')

# 'WE-EW': ['gsndj_n7 gsndj_n6', 'gsndj_s4 gsndj_s5'],
# 'NS-SN': ['29257863#2 29257863#5', '161701303#7.248 161701303#10']

edge_vehs = count_vehicles_for_multiple_edges(
    xml_path=route_file,
    edges_list=["gsndj_s4 gsndj_s5", "29257863#2 29257863#5"],
    interval=120
)

# 更新 key, 图片的 legend
edge_vehs['WE-EW'] = edge_vehs.pop("gsndj_s4 gsndj_s5")
edge_vehs['NS-SN'] = edge_vehs.pop("29257863#2 29257863#5")

plot_vehicle_counts(edge_vehs, current_file_path('./route.png'))