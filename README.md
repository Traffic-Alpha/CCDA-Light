<!--
 * @Author: WANG Maonan
 * @Date: 2023-03-22 16:59:42
 * @Description: README for Paper AAP with CCDA
 * @LastEditTime: 2024-06-28 00:46:11
-->
# Traffic Signal Cycle Control with Centralized Critic and Decentralized Actors under Varying Intervention Frequencies

This repository contains the code for the paper "Traffic Signal Cycle Control with Centralized Critic and Decentralized Actors under Varying Intervention Frequencies".

- [Traffic Signal Cycle Control with Centralized Critic and Decentralized Actors under Varying Intervention Frequencies](#traffic-signal-cycle-control-with-centralized-critic-and-decentralized-actors-under-varying-intervention-frequencies)
  - [🎉 News](#-news)
  - [🔑 Key Points](#-key-points)
  - [📥 Installation](#-installation)
  - [🏃‍♂️ Training](#️-training)
  - [🧪 Evaluation](#-evaluation)
  - [📚 Citation](#-citation)

## 🎉 News

1. 我们实现了信号灯控制中所有的，同时上传了模型权重，可以通过 eval 
2. We have transitioned the simulation platform in the project from Aiolos to [TransSimHub](https://github.com/Traffic-Alpha/TransSimHub) (TSHub). We extend our gratitude to our colleagues at SenseTime, **@KanYuheng (阚宇衡)**, **@MaZian (马子安)**, and **@XuChengcheng (徐承成)** (listed alphabetically) for their contributions. The development of TransSimHub (TSHub) is built upon the foundation of Aiolos.

## 🔑 Key Points

- **Adaptation to Varying Intervention Frequencies**: The intervention frequency significantly impacts the effectiveness of traffic signal control systems, influenced by factors such as resource limitations, safety, traffic flow disruption, and system stability. This research introduces varying intervention frequencies to the TSC system, defining it as the rate at which traffic signals are adjusted in response to changing traffic conditions. This approach is particularly beneficial for scenarios requiring manual verification, where lower frequencies may be preferable.

<div align=center>
   <img src="./_assets/intervention_frequency.png" width="50%" >
</div>
<p align="center">An example of applying the intervention frequency based on cycle-based control action design in a four-phase traffic signal system</p>


- **Enhanced Action Utilization**: To accommodate varying intervention frequencies, particularly lower frequencies, it is crucial for the control agent to maximize the impact of each action taken. Our research introduces a novel action strategy named `adjust all phases`, which allows for the simultaneous adjustment of all traffic phases within a single cycle, thereby increasing the effectiveness of each intervention.

<div align=center>
   <img src="./_assets/adjust_all_phases.png" width="50%" >
</div>
<p align="center">An example of adjust all phases in a four phases traffic signal system</p>


- **Efficient Management of Large Action Spaces**: This research employs a Centralized Critic and Decentralized Actors (CCDA) architecture to effectively manage large action spaces. Decentralized actors are responsible for adjusting individual signal phases, which reduces the complexity of the action space. Simultaneously, a centralized critic evaluates the overall traffic scenario, ensuring coordinated actions among the decentralized actors, thus enhancing overall system performance.

<div align=center>
   <img src="./_assets/overall_framework.png" width="50%" >
</div>
<p align="center">The framework of our method with the intervention frequency</p>


## 📥 Installation

Before using, make sure [TSHub](https://github.com/Traffic-Alpha/TransSimHub/tree/main) is installed.

```shell
git clone https://github.com/Traffic-Alpha/TransSimHub.git
cd TransSimHub
pip install -e ".[rl]"
```

## 🏃‍♂️ Training

安装完毕 `TSHub` 之后就可以开始训练。我们将 5 种不同的 `agent design` 分别放在 5 个文件夹中，分别是目前已有的四种方法：

- [Choose Next Phase](./Choose_Next_Phase/), choosing a phase among all possible phases at each time step.
- [Next or Not](./Next_or_Not/), determining whether to change to the next phase or not at each time step. 需要注意，此时 state 中需要包含 traffic phase 的信息，因此每次 0 和 1 表示的相位会有所不同。
- [Set Phase duration](./Set_Current_Phase_Duration/), setting the phase duration at the beginning of each phase.
- [Adjust Single Phase](./Adjust_Single_Phase_Cycle/), modifying only one phase in the whole cycle. 

The following figure illustrates examples of these four action designs for a TSC system with four phases, with the assumption that the starting time is at time $t$.

<div align=center>
   <img src="./_assets/four_common_action_designs.png" width="80%" >
</div>
<p align="center">For Common Agent Design for TSC system.</p>

除此之外，还有本文提出的 [Adjust All Phases](./Adjust_All_Phases_Cycle/) 的方法。每一个文件夹中的文件夹结构如下所示：

```
- METHOD_NAME # 方法的名字
   - train_utils/ # 包含训练相关的代码，例如网络结构
   - env_utils/ # 环境相关代码，state, action, reward
   - train_METHOD_NAME.py # 训练的代码
   - eval_METHOD_NAME.py # 测试代码
   - train_deltas.sh # 方便在不同 delta time 下进行训练
```

于是我们可以通过运行 `train_METHOD_NAME.py` 来进行训练。例如对于 `Adjust_Single_Phase_Cycle`，可以运行下面的命令，此时表示同时开启 20 个仿真，且动作间隔是 60s：

```shell
python train_adjust_single_phase.py --delta_time 60 --num_envs 20
```

为了更加方便的训练在不同 `delta time` 下的结果，我们也可以通过运行 `train_deltas.sh` 来快速训练在不同 `delta time` 下的结果。

```shell
nohup bash train_deltas.sh > train_deltas.log &
```

训练之后会生成 `log` 和 `save_models` 两个文件夹。其中 `log` 中保存着训练过程中的每一局仿真的累计奖励，用于绘制奖励曲线的变化。`save_models` 文件夹保存着训练过程中保存的模型权重，用于进行测试。我们可以运行 `plot_rewards.py` 来将 `log` 文件夹中的结果绘制为 reward curve：

```shell
python plot_rewards.py --action_type Adjust_All_Phases_Cycle --delta_time 60
```

下面是我们运行 `Adjust All Phases` 的 reward curve 的结果：


## 🧪 Evaluation

After training, you can test it by loading the model weights in `save_models`. Run `eval_METHOD_NAME.py` to test. For example, for `Adjust All Phases`, we test the results when `delta time` is 60.

```shell
python eval_adjust_all_phases.py --delta_time 60
```

Running the above test script will get the `exp_output` file, which contains the vehicle information `tripinfo.out_1.xml` and the signal light phase information `./add/tls_programs.out_1.xml`. You can run `analysis_tripinfo.py` to analyze the `tripinfo.out_1.xml` file:

```shell
python analysis_tripinfo.py --action_type Adjust_All_Phases_Cycle --delta_time 60
```

At this time, statistics of different attributes will be output, such as travel time, waiting time, etc.:

```
Statistics for travelTime:
  Mean: 111.31
  Variance: 3493.35
  Max: 323.00
  Min: 41.00
  Percentile_25: 64.00
  Percentile_50: 88.00
  Percentile_75: 148.00

Statistics for waitingTime:
  Mean: 44.33
  Variance: 3021.38
  Max: 236.00
  Min: 0.00
  Percentile_25: 0.00
  Percentile_50: 20.00
  Percentile_75: 74.00

Statistics for waitingCount:
  Mean: 0.86
  Variance: 0.74
  Max: 8.00
  Min: 0.00
  Percentile_25: 0.00
  Percentile_50: 1.00
  Percentile_75: 1.00
```

In addition, you can run `plot_tls_program.py` to plot the phase change of the traffic signal light. Note that since `Choose Next Phase` has no concept of the signal light cycle, it cannot plot the phase change. Below we plot the phase change of `Adjust All Phase` when the interval is 60s as an example:

```shell
python plot_tls_program.py --action_type Adjust_All_Phases_Cycle --delta_time 60
```

The generated figures are as follows, showing the green time ratio of all phases and the specified phase respectively:



## 📚 Citation

If you find this work useful, please cite our papers:

```bibtex
@article{wang2024traffic,
   title={Traffic Signal Cycle Control with Centralized Critic and Decentralized Actors under Varying Intervention Frequencies}, 
   author={Maonan Wang and Yirong Chen and Yuheng Kan and Chengcheng Xu and Michael Lepech and Man-On Pun and Xi Xiong},
   year={2024},
   journal={arXiv preprint arXiv:2406.08248},
}
```