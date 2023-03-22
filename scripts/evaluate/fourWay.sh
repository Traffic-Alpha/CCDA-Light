#!/bin/sh
###
 # @Author: WANG Maonan
 # @Date: 2022-08-22 21:40:18
 # @Description: 训练所有的动作
 # sbatch -J fourWay_4phase -p CPU -n 1 -c 1 -w st-node-157 fourWay_4phase.sh > fourWay_4phase.log &
 # @LastEditTime: 2023-03-22 23:23:25
###

FOLDER="/mnt/d/ubuntu_project/ActionsVSScenarios"

for delta_times in None 60 120 300; do
    echo '==>' $delta_times

    for net_type in 4phases 6phases; do
        echo '===>' $delta_times $net_type

        python ${FOLDER}/ChooseNextPhase/evaluate.py --net_folder=fourWay --net_id=$net_type --delta_times=$delta_times
        echo '完成 Choose Next Phase 的测试。'

        python ${FOLDER}/CyclePhaseAdjust_Discrete/evaluate.py --net_folder=fourWay --net_id=$net_type --delta_times=$delta_times
        echo '完成 Cycle Phase Adjustment (Discrete) 的测试。'

        python ${FOLDER}/CyclePhaseAdjust_MultiDiscrete/evaluate.py --net_folder=fourWay --net_id=$net_type --delta_times=$delta_times
        echo '完成 Cycle Phase Adjustment (Multi-Discrete) 的测试。'

        python ${FOLDER}/CycleSinglePhaseAdjust/evaluate.py --net_folder=fourWay --net_id=$net_type --delta_times=$delta_times
        echo '完成 Cycle Single Phase Adjustment 的测试。'

        python ${FOLDER}/NextorNot/evaluate.py --net_folder=fourWay --net_id=$net_type --delta_times=$delta_times
        echo '完成 Next or Not 的测试。'

        python ${FOLDER}/SetCurrentPhaseDuration/evaluate.py --net_folder=fourWay --net_id=$net_type --delta_times=$delta_times
        echo '完成 Set Phase Duration 的测试。'
    done
done