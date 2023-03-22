###
 # @Author: WANG Maonan
 # @Date: 2022-10-17 15:48:41
 # @Description: 每次调整所有的 phase, 使用 multi-discrete 作为模型的设计
 # @LastEditTime: 2022-10-17 15:48:26
### 
FOLDER="/mnt/d/ubuntu_project/ActionsVSScenarios"

# fourWay, 4phases
for delta_times in None; do
    echo '==>' $delta_times

    for route_type in fluctuation stable; do
        echo '==> fourWay, 4phases' $delta_times, $route_type
        
        python ${FOLDER}/CyclePhaseAdjust_MultiDiscrete/evaluate_args.py --home_folder=./-6_6_3 --net_folder=fourWay --net_id=4phases --delta_times=$delta_times --model_type=best --route_id=$route_type  --random_mask_obs=True
        echo '完成 Cycle All Phases Adjustment (Multi-Discrete) 的测试。'
    done
done


# fourWay, 6phases
for delta_times in None; do
    echo '==>' $delta_times

    for route_type in fluctuation stable; do
        echo '==> fourWay, 6phases' $delta_times, $route_type
        
        python ${FOLDER}/CyclePhaseAdjust_MultiDiscrete/evaluate_args.py --home_folder=./-6_6_3 --net_folder=fourWay --net_id=6phases --delta_times=$delta_times --model_type=best --route_id=$route_type  --random_mask_obs=True
        echo '完成 Cycle All Phases Adjustment (Multi-Discrete) 的测试。'
    done
done


# TJunction, 3phases
for delta_times in None; do
    echo '==>' $delta_times

    for route_type in fluctuation stable; do
        echo '==> TJunction, 3phases' $delta_times, $route_type
        
        python ${FOLDER}/CyclePhaseAdjust_MultiDiscrete/evaluate_args.py --home_folder=./-6_6_3 --net_folder=TJunction --net_id=3phases --delta_times=$delta_times --model_type=best --route_id=$route_type  --random_mask_obs=True
        echo '完成 Cycle All Phases Adjustment (Multi-Discrete) 的测试。'
    done
done