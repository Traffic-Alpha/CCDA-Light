# MDLight under varying intervention frequencies - 中文文档

[MDLight under varying intervention frequencies](./README.md)

## 目录

- [MDLight under varying intervention frequencies - 中文文档](#mdlight-under-varying-intervention-frequencies---中文文档)
  - [目录](#目录)
  - [什么是交互限制](#什么是交互限制)
  - [SUMO 网络介绍](#sumo-网络介绍)
  - [在基于强化学习的信号灯控制中的五种动作设计](#在基于强化学习的信号灯控制中的五种动作设计)
  - [快速开始](#快速开始)


`MDLight` 是论文 `A multi-discrete reinforcement learning framework for adaptive traffic signal cycle control under varying intervention frequencies` 的代码实现。

在这篇工作中，我们提出了一个可以适应于不同交互频率的信号灯控制的框架。交互频率在实际落地中是非常重要的，由于（1）计算资源，（2）安全的考虑，（3）交通流的分布和（4）系统的稳定性，不同的环境需要有不同的交互频率。因此设计一个方法在不同的交互频率下都有好的效果就至关重要。下图展示本文提出的框架的主要内容，包含（1）一个新的动作设计和（2）一个 Multi-discrete 策略的优化方法：

<div align=center>
  <img src ="./doc/overall_structure.png" width="70%" height="auto" style="margin: 0 1%;"/>
</div>

在本文中，我们主要做了以下的几点：

- 将交互频率引入信号灯控制系统，并测试了目前大部分方法在不同交互频率下的效果。
- 我们提出了 MDLight 的框架，该框架利用 `adjust all phases` 和 mulit-discrete 策略优化方法，从而在不同交互频率下都有好的效果。


## 什么是交互限制

在基于强化学习的信号灯控制系统中，交互限制是指智能体修改信号灯的时间间隔。下图展示了将交互限制用在周期调整的动作上的结果：

<div align=center><img src ="./doc/intervention_frequency.png"/></div>


## SUMO 网络介绍

[Nets](./nets) 文件夹包含 SUMO 的地图和车流文件。下图展示了本文中所使用的三个路网，三个路口的拓扑结构和相位结构分别如下所示：

- **INT-1**, 十字路口，且包含 $4$ 相位；
- **INT-2**, 十字路口，且包含 $6$ 相位；
- **INT-3**, 丁字路口，且包含 $3$ 相位；

<div align=center><img src ="./doc/SUMO_Nets.png"/></div>


## 在基于强化学习的信号灯控制中的五种动作设计

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

- [MDLight (Discrete)](./CyclePhaseAdjust_Discrete/)：这种方法直接应用调整所有相位，其中动作空间涵盖所有阶段持续时间变化的所有可能组合。然而，当阶段数变大时，动作空间将呈指数增长。这种方法中使用了 PPO-Clip 模型来进行训练。
- [MDLight (Multi-Discrete)](./CyclePhaseAdjust_MultiDiscrete/)：与简单调整所有阶段方法相比，MDLight（多离散）通过为每个相位使用单个离散动作的向量将离散动作转换为多离散动作。这种方法显着减小了动作空间的大小，尤其是当信号相位数很大时。此外，利用多离散策略优化算法来优化策略，提升了收敛的速度和稳定性。


## 快速开始

所有的脚本文件都可以在文件夹 [scripts](./scripts/) 中找到。例如，我们可以运行下面的命令，来分别为五种动作设计在路口 **INT-1**，$\Delta=60$ 下训练模型：

```shell
bash ./scripts/delta_60/fourWay_4phase_stable.sh
```
