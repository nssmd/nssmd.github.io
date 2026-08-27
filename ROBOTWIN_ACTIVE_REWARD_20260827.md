# RoboTwin 当前统一 Reward

**生效范围：** E1-E7 的 Offline RL、Online RL 与 RFT  
**原则：** 先评价 WAM 预测视频，再评价预测能否被 IDM 实现，最后用真实
simulator 成功作为锚点。它不是 action reward，也不是 Selector。

## 1. 预测视频 Reward

```text
S_core = 0.30 * visible_progress_gain
       + 0.20 * goal_geometry
       + 0.15 * contact_sequence
       + 0.15 * physical_plausibility
       + 0.20 * terminal_stability

S_valid = object_target_correctness * S_core

P_fail = 0.35 * wrong_object_or_target
       + 0.25 * teleportation_or_discontinuity
       + 0.20 * unsafe_collision_or_drop
       + 0.20 * stage_regression_or_false_completion

R_video = clip(S_valid - P_fail, -1, 1)
```

`R_video` 只看执行前第一段 WAM 预测视频，不读取动作、simulator状态或真实
成败。

## 2. 预测与执行一致性

冻结 IDM 执行后，比较预测终态和真实视觉终态：

```text
R_realizable = max(R_video, 0) * R_agree
```

一致性只奖励本身正确的预测视频，不能让“预测失败、执行也失败”的路径得高分。

## 3. 当前总 Reward

```text
R_total = 0.55 * R_video
        + 0.20 * R_realizable
        + 0.25 * simulator_success
```

- 55%：直接预测视频质量；
- 20%：预测能否被冻结 IDM 实现；
- 25%：真实 RoboTwin 最终成功。

## 4. RL 与 RFT

同-state四条路径内：

```text
A_i = (R_total_i - mean_group) / (std_group + 1e-6)
```

RL 使用全部路径的组内 advantage；RFT 使用同一个 `R_total` 选取或加权高分
路径。没有 Selector，IDM 保持冻结。

## 5. 当前结果

E1-S1已经完成，真实simulator成败与scorer输入严格分离。

| 数据 | Reward-Top | Random期望 | 提升 |
|---|---:|---:|---:|
| 32条smoke | 6/8，75.0% | 59.4% | +15.6pp |
| 完整416条、104个state组 | 69/104，66.3% | 63.9% | +2.4pp |
| 19个成败分叉组 | 13/19，68.4% | 55.3% | +13.2pp |

完整416条的success-failure pair accuracy为56.7%。当前reward对Top-1选择有效，
下一步进入E1-S2 Offline RL/RFT Pilot。

## 6. 参考工作

- SARM / SARM2：stage-aware、阶段内细粒度进度；
- TOPReward：instruction-conditioned 视频进度；
- Robo-Dopamine / 2.0：step-aware、failure-aware process reward；
- RL-VLM-F：VLM pairwise preference；
- Robometer / ARM：跨轨迹排序与相对 advantage；
- Dream2Reward：预测变化与真实变化的 transition alignment；
- EVA：video world model 经 IDM 解码时的 executability gap；
- RoboAlign-R1 / RoboReward：机器人视频多维质量和失败样本；
- ReinFlow：随机 flow path 的 likelihood 与 RL 更新。

这些工作决定 reward 的结构，但 `0.55/0.20/0.25` 以及五个视频维度的初始
权重是本项目为 WAM + frozen IDM 范式设定的，需要由 E1 和消融实验验证。
