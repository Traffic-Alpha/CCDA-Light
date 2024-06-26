###
 # @Author: WANG Maonan
 # @Date: 2024-05-01 23:21:14
 # @Description: 训练不同的 delta time, nohup bash train_deltas.sh > train_deltas.log &
 # @LastEditTime: 2024-06-28 15:43:53
### 
#!/bin/bash

# Array of delta time values to test
delta_times=(30 60 120 300)

# Loop through the delta time values and execute the command with each
for delta_time in "${delta_times[@]}"
do
  echo "Running with delta_time=${delta_time}"
  python train_adjust_all_phases.py --delta_time "${delta_time}" --num_envs 20
done