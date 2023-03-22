###
 # @Author: WANG Maonan
 # @Date: 2022-10-11 22:22:07
 # @Description: 测试 adjust single phase 的模型
 # @LastEditTime: 2022-10-17 15:28:36
### 
FOLDER="/mnt/d/ubuntu_project/ActionsVSScenarios"

# fourWay, 4phases
for delta_times in None; do
    echo '==>' $delta_times

    for route_type in fluctuation stable; do
        echo '==> fourWay, 4phases' $delta_times, $route_type
        
        python ${FOLDER}/CycleSinglePhaseAdjust/evaluate_args.py --home_folder=./exp1 --net_folder=fourWay --net_id=4phases --delta_times=$delta_times --model_type=best --route_id=$route_type  --random_mask_obs=True
        echo '完成 Cycle Single Phase Adjustment 的测试。'
    done
done


# fourWay, 6phases
for delta_times in None; do
    echo '==>' $delta_times

    for route_type in fluctuation stable; do
        echo '==> fourWay, 6phases' $delta_times, $route_type
        
        python ${FOLDER}/CycleSinglePhaseAdjust/evaluate_args.py --home_folder=./exp1 --net_folder=fourWay --net_id=6phases --delta_times=$delta_times --model_type=best --route_id=$route_type  --random_mask_obs=True
        echo '完成 Cycle Single Phase Adjustment 的测试。'
    done
done


# TJunction, 3phases
for delta_times in None; do
    echo '==>' $delta_times

    for route_type in fluctuation stable; do
        echo '==> TJunction, 3phases' $delta_times, $route_type
        
        python ${FOLDER}/CycleSinglePhaseAdjust/evaluate_args.py --home_folder=./exp1 --net_folder=TJunction --net_id=3phases --delta_times=$delta_times --model_type=best --route_id=$route_type  --random_mask_obs=True
        echo '完成 Cycle Single Phase Adjustment 的测试。'
    done
done