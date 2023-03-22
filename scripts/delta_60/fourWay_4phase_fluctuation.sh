#!/bin/sh
###
 # @Author: WANG Maonan
 # @Date: 2022-08-22 21:40:18
 # @Description: 训练所有的动作
 # nohup srun -J fourWay_4phase_fluctuation -p CPU -n 1 -c 30 -w st-node-158 bash fourWay_4phase_fluctuation.sh > node_158_fluctuation.log &
 # sbatch -J fourWay_4phase_fluctuation -p CPU -n 1 -c 30 -w st-node-158 fourWay_4phase_fluctuation.sh > node_158_fluctuation.log &
 # @LastEditTime: 2022-08-22 21:59:13
###

FOLDER="/mnt/nfs/data/wangmaonan/ActionsVSScenarios"


python ${FOLDER}/ChooseNextPhase/train.py --net_folder=fourWay --net_id=4phases --route_id=fluctuation --delta_times=60
echo '完成 Choose Next Phase 的训练'

python ${FOLDER}/CyclePhaseAdjust_Discrete/train.py --net_folder=fourWay --net_id=4phases --route_id=fluctuation --delta_times=60
echo '完成 Cycle Phase Adjustment (Discrete) 的训练'

python ${FOLDER}/CyclePhaseAdjust_MultiDiscrete/train.py --net_folder=fourWay --net_id=4phases --route_id=fluctuation --delta_times=60
echo '完成 Cycle Phase Adjustment (Multi-Discrete) 的训练'

python ${FOLDER}/CycleSinglePhaseAdjust/train.py --net_folder=fourWay --net_id=4phases --route_id=fluctuation --delta_times=60
echo '完成 Cycle Single Phase Adjustment 的训练'

python ${FOLDER}/NextorNot/train.py --net_folder=fourWay --net_id=4phases --route_id=fluctuation --delta_times=60
echo '完成 Next or Not 的训练'

python ${FOLDER}/SetCurrentPhaseDuration/train.py --net_folder=fourWay --net_id=4phases --route_id=fluctuation --delta_times=60
echo '完成 Set Phase Duration 的训练'