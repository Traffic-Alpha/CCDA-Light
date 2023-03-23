# TSC Adjust All Phases - 中文文档

`TSC-AdjustAllPhases` 是论文 `A Practical and Reliable Framework for Real-World Adaptive Traffic Signal Cycle Control Using Reinforcement Learning` 的代码实现。下图展示了本文所提出的整体框架。

<div align=center><img src ="./doc/overall_structure.png"/></div>

在本文中，我们主要做了以下的几点：

- 我们提出了一种自适应控制框架，该框架利用 `adjust all phases` 和 PPO 算法按照一个周期调整所有相位的时长。
- 引入干预频率来限制 `agent` 与 `env` 之间的交互。
- 除了效率之外，还提出了三种新的评估指标来综合衡量不同 TSC 方法的性能。


## 项目大纲

- [TSC Adjust All Phases - 中文文档](#tsc-adjust-all-phases---中文文档)
  - [项目大纲](#项目大纲)
  - [SUMO 网络介绍](#sumo-网络介绍)
  - [五种动作设计](#五种动作设计)
  - [Getting Start](#getting-start)


## SUMO 网络介绍


[Nets](./nets) 文件夹包含 SUMO 的地图和车流文件。下图展示了本文中所使用的三个路网，三个路口的拓扑结构和相位结构分别如下所示：

- **INT-1**, 十字路口，且包含 $4$ 相位；
- **INT-2**, 十字路口，且包含 $6$ 相位；
- **INT-3**, 丁字路口，且包含 $3$ 相位；

<div align=center><img src ="./doc/SUMO_Nets.png"/></div>


## 五种动作设计

目前在基于强化学习的信控领域，有以下四种常见的动作设计，分别是：

- [Choose next phase](./ChooseNextPhase), 每个时间步会从所有可能的相位中选择一个相位。
- [Next or not](./NextorNot/), 每个时间步会决定保持当前的相位，或是切换到下一个相位。
- [Set current phase duration](./SetCurrentPhaseDuration/), 在每一个相位开始的阶段，会给当前的相位设置一个持续的时间。
- [Adjust single phase](./CycleSinglePhaseAdjust/), 每一个周期只调整一个相位，且每次调整的时间为 $[-5, 0, 5]$。

下图展示了上面这四种动作在 $4$ 相位下的结果。假设开始时间是 $t$：

<div align=center><img src ="./doc/four_common_action_designs.png"/></div>


在本文中，我们提出了一种名为 `adjust all phases` 的新的动作设计，它可以修改一个周期内所有阶段的持续时间。下图说明了 `adjust all phases` 的动作设计示例。

<div align=center><img src ="./doc/adjust_all_phases.png"/></div>

对于本文提出的动作 `adjust all phases`，共有下面两种变形:

- [Adjust All Phases (Discrete)](./CyclePhaseAdjust_Discrete/)：离散变化直接应用调整所有阶段，其中动作空间涵盖所有阶段持续时间变化的所有可能组合，这种方法会导致动作空间随着相位变大而指数上升。
- [Adjust All Phases (Multi-Discrete)](./CyclePhaseAdjust_MultiDiscrete/)：Multi-discrete 通过为每个相位使用单个离散动作的向量，将离散动作（discrete）转换为多离散动作（multi-discrete）。


## Getting Start

所有的脚本文件都可以在文件夹 [scripts](./scripts/) 中找到。例如，我们可以运行下面的命令，来分别为五种动作设计在路口 **INT-1**，$\Delta=60$ 下训练模型：

```shell
bash ./scripts/delta_60/fourWay_4phase_stable.sh
```
