# TSC Adjust All Phases

[TSC Adjust All Phases（中文文档）](./README_zh_CN.md)

`TSC-AdjustAllPhases` is an implementation of `A Practical and Reliable Framework for Real-World Adaptive Traffic Signal Cycle Control Using Reinforcement Learning`. 

We pay more attention to the following points:

- We present an adaptive control framework that utilizes a novel action design adjust all phases with a multi-discrete PPO algorithm for the TSC problem.
- Intervention frequency is introduced to restrict the interaction between the agent and the environment. 
- Besides efficiency, three novel evaluation metrics are proposed to comprehensively measure the performance of different TSC methods.



## Outline

- [TSC Adjust All Phases](#tsc-adjust-all-phases)
  - [Outline](#outline)
  - [SUMO Network](#sumo-network)
  - [Five Action Designs](#five-action-designs)
  - [Getting Start](#getting-start)


## SUMO Network

The [nets](./nets) folder includes the sumo maps and routes. As depicted in the following figure, the topologies and phases of the three intersections are described as follows:

- **INT-1**, a 4-way intersection with $4$ phases; 
- **INT-2**, a 4-way intersection with $6$ phases; 
- **INT-3**, the 3-way intersection scenario with $3$ phases.

<div align=center><img src ="./doc/SUMO_Nets.png"/></div>


## Five Action Designs

The existing RL-based studies primarily employ one of the following four action designs:

- [Choose next phase](./ChooseNextPhase), choosing a phase among all possible phases at each time step.
- [Next or not](./NextorNot/), determining whether to change to the next phase or not at each time step. 
- [Set current phase duration](./SetCurrentPhaseDuration/), setting the phase duration at the beginning of each phase.
- [Adjust single phase](./CycleSinglePhaseAdjust/), modifying only one phase in the whole cycle. 

The following figure illustrates examples of these four action designs for a TSC system with four phases, with the assumption that the starting time is at time $t$.

<div align=center><img src ="./doc/four_common_action_designs.png"/></div>

In this paper, we propose a novel action design named `adjust all phases`, which can modify the duration of all phases in one cycle. The following figure illustrates examples of action design `adjust all phases`.

<div align=center><img src ="./doc/adjust_all_phases.png"/></div>

There are two variants of `adjust all phases`:

- [Adjust All Phases (Discrete)](./CyclePhaseAdjust_Discrete/). The discrete variation directly applies adjust all phases, where the action space covers all possible combinations of all phase duration changes.
- [Adjust All Phases (Multi-Discrete)](./CyclePhaseAdjust_MultiDiscrete/). The multi-discrete variation converts discrete actions to multi-discrete actions by using a vector of individual discrete actions for each phase.


## Getting Start

All the scripts can be found in [scripts](./scripts/). For example, we can run the following command to train the models with of five action designs separately on $\Delta=60$, **INT-1**:

```shell
bash ./scripts/delta_60/fourWay_4phase_stable.sh
```
