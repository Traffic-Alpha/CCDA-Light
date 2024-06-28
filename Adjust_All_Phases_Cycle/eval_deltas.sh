###
 # @Author: WANG Maonan
 # @Date: 2024-06-28 15:40:35
 # @Description: 测试不同的 delta time 的结果
 # @LastEditTime: 2024-06-28 15:40:36
### 
#!/bin/bash

# Array of delta time values to test
delta_times=(30 60 120 300)

# Loop through the delta time values and execute the command with each
for delta_time in "${delta_times[@]}"
do
  echo "Running with delta_time=${delta_time}"
  python eval_adjust_all_phases.py --delta_time "${delta_time}"
done