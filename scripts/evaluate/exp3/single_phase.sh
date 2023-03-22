###
 # @Author: WANG Maonan
 # @Date: 2022-10-10 14:19:11
 # @Description: 测试动作 adjust single phases
 # @LastEditTime: 2022-10-11 16:25:33
### 
FOLDER="/mnt/d/ubuntu_project/ActionsVSScenarios"

for delta_times in 600 1200 1800 2400 3000; do
    echo '==>' $delta_times

    for route_type in fluctuation stable; do
        echo '==>' $route_type
        
        python ${FOLDER}/CycleSinglePhaseAdjust/evaluate_args.py --home_folder=./exp3/$route_type --net_folder=fourWay --net_id=4phases --delta_times=$delta_times --model_type=best --route_id=$route_type
        echo '完成 Cycle Single Phase Adjustment 的测试。'
    done
done