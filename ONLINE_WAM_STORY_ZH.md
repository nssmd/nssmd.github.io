# Online-WAM：给世界动作模型加入在线训练

> **核心主张：** 预训练好的 World Action Model 不应该在部署后保持静止。它应该利用真实交互中的成功和失败，持续改进自己生成的未来视频与机器人行为。Online-WAM 把 WAM 内部的视频生成轨迹变成可优化的随机策略，用最终任务成功率直接进行在线强化学习。

## 最新实验结果（2026-08-26）

### 1. 复杂 reward 已经有效

当前 reward 不再只有“成功 1、失败 0”，而是逐段评价：

- 末端是否接近目标物；
- 是否建立抓取；
- 是否把物体抬离支撑面；
- 是否向目标容器运输；
- 是否稳定完成放置；
- 是否扰动无关物体；
- 最终任务是否成功，以及用了多少步。

在 seed0 的 128 条 R0 轨迹、32 个同-state 四路径组上：

| 指标 | 二元 reward | 复杂阶段 reward |
|---|---:|---:|
| 有非零训练信号的组 | 14 / 32 | **32 / 32** |
| 有非零 actor 梯度的视频决策 | 219 / 506 | **506 / 506** |
| 成功路径排在失败路径前 | 46 / 46 | **46 / 46** |

只使用不含终局成功标签的运动学过程分，也能排对 45 / 46 个成功-失败配对。

### 2. Reward 剪枝有效

在 32 个同-state 组里：

- 随机选择一路，预期成功 8 / 32；
- 选择 reward 最高的一路，成功 15 / 32；
- 同-state oracle 上限也是 15 / 32。

14 个同时存在成功和失败的组，Reward-Top 14 / 14 选中成功路径。

### 3. 单 seed PPO 没有提高成功率

在 8 个任务、每任务 2 个未训练状态上，采用完全 matched 的三方评测：

| 方法 | 成功 |
|---|---:|
| Base WAM | **4 / 16** |
| Binary-reward LoRA | 2 / 16 |
| Shaped-reward LoRA | 2 / 16 |

Shaped 相对 Binary 有 1 个救回和 1 个退化，净提升为 0；相对 Base 有 0 个救回和 2 个退化。

这说明：

> Reward 已经能判断哪条视频未来更好，但 128 条单-seed 数据和 4-epoch PPO 还不能把这种排序能力稳定地写进视频生成头。

当前正在完成 10-seed 全量 reward replay，并将 1280 条轨迹合并训练一个 pooled Video-Head LoRA。Selector 和 IDM 始终冻结。

## 摘要

World Action Model（WAM）同时预测未来世界状态和机器人动作。它的关键优势是：机器人控制建立在一个显式的未来预测上，模型不仅输出“怎么动”，还输出“动完之后世界会变成什么样”。

但当前大多数 WAM 主要依赖离线训练：

```text
离线机器人数据
  → 预训练 WAM
  → 部署固定模型
  → 执行任务
```

模型在部署时产生了大量新的成功和失败，但这些结果通常不会自动回到 WAM 中。于是模型可能反复想象错误的抓取、接触、物体运动或最终状态，却无法从自己的错误中持续改进。

Online-WAM 增加了一个完整在线闭环：

1. 从同一个机器人状态生成多个随机视频动作未来；
2. 执行每个未来对应的机器人动作；
3. 从环境获得最终成功或失败；
4. 将 reward 归因到完整视频生成路径；
5. 更新 WAM 内部视频生成头；
6. 部署新 WAM，进入下一轮交互。

本文研究的核心问题是：

> **一个预训练 video-action WAM，能否通过在线交互和最终任务 reward，持续提高机器人成功率？**

---

## 1. 背景

### 1.1 从动作策略到世界动作模型

传统机器人策略直接学习：

```text
当前观察 + 任务 → 动作
```

WAM 学习的是：

```text
当前观察 + 任务
  → 未来世界如何变化
  → 与该未来一致的机器人动作
```

视频未来承担了 visual planning 的作用，可以表达：

- 物体应该如何移动；
- 夹爪应该在什么位置建立接触；
- 抓取是否稳定；
- 物体最后应该处于什么空间关系。

UniPi、Video Language Planning、LingBot-VA 和 DreamZero 等工作已经证明，视频生成可以成为机器人规划和控制的核心表示。

### 1.2 WAM 缺少在线训练

现有 WAM 的主要问题不是模型没有能力，而是部署流程没有闭环。

离线训练优化的是：

- demonstration likelihood；
- 视频重建或生成质量；
- 动作预测误差。

部署真正关心的是：

- 机器人是否完成任务；
- 抓取是否稳定；
- 物体是否进入目标区域；
- 长时执行是否成功。

Online-WAM 要补上的就是：

```text
预训练 WAM
  → 在线交互
  → 最终任务 reward
  → 更新未来生成分布
  → 新 WAM
```

---

## 2. Motivation

### 2.1 离线生成概率不等于任务成功

一个未来视频可以视觉上合理，但任务上失败：

- 抓到了错误物体；
- 接触发生但抓取不稳定；
- 物体移动了但没有放入目标区域；
- 最终画面接近目标，但 simulator predicate 没有满足；
- 中间误差导致后续状态偏离训练数据。

因此，部署环境提供的任务 reward 是离线数据无法完全替代的监督信号。

### 2.2 当前策略会制造新的状态分布

机器人执行中的小误差会改变下一帧观察。模型很快进入 demonstration 中较少出现的状态。

在线交互提供了最有价值的数据：

- 当前策略真正访问到的状态；
- 当前模型真正产生的失败；
- 同一状态下偶然出现的成功未来；
- 最终任务是否完成。

### 2.3 在线学习需要多样性

原始 deterministic ODE 对同一状态通常只产生一条生成路径。在线 RL 需要比较多个可能未来：

```text
同一个 state
  ├── future A → failure
  ├── future B → success
  ├── future C → failure
  └── future D → success
```

这种比较比不同 episode 之间的比较更干净，因为任务、初始状态和物体配置都相同，主要差异来自 WAM 采样出的未来。

### 2.4 为什么直接更新 WAM

本文不是在冻结 WAM 外面增加一个新模块，而是研究 WAM 本身能否成为 online learner。

我们更新内部视频生成分布，同时保持 action head 和 IDM/action flow 不变。这样行为变化可以明确归因到：

> WAM 对未来世界的预测发生了变化。

---

## 3. 问题定义

定义：

- \(o_t\)：当前机器人观察；
- \(c\)：语言任务；
- \(\tau^v\)：视频 latent 生成轨迹；
- \(\hat V\)：解码后的未来视频；
- \(a_{t:t+H}\)：未来对应的动作；
- \(R\in\{0,1\}\)：最终任务 reward。

WAM 定义视频未来策略：

\[
\tau^v\sim\pi_\theta(\tau^v\mid o_t,c).
\]

冻结的动作转换模块输出动作：

\[
a_{t:t+H}=g_{\mathrm{frozen}}(o_t,c,\hat V).
\]

环境返回：

\[
R(\tau^v)=
\begin{cases}
1,&\text{完整任务成功},\\
0,&\text{完整任务失败}.
\end{cases}
\]

在线目标为：

\[
\max_\theta
\mathbb E_{\tau^v\sim\pi_\theta}
\left[R(\tau^v)\right].
\]

关键技术问题是：如何计算完整视频生成路径的概率，并用任务 reward 优化它。

---

## 4. 方法

### 4.1 将确定性视频 ODE 变成随机在线策略

原始 flow sampler：

\[
z_{k+1}
=
z_k+\Delta t f_\theta(z_k,t_k\mid o,c).
\]

Online-WAM 加入可复现 Gaussian noise：

\[
z_{k+1}
=
z_k+\Delta t f_{\theta,\phi}(z_k,t_k\mid o,c)
+\sigma_k\sqrt{\Delta t}\epsilon_k,
\qquad
\epsilon_k\sim\mathcal N(0,I).
\]

其中：

- \(\theta\) 是冻结的预训练参数；
- \(\phi\) 是视频输出头内部的 LoRA；
- \(\sigma_k\) 是第 \(k\) 个 flow step 的探索强度。

所有 noise seed 和 latent transition 都会保存，因此完整路径可以精确 replay。

### 4.2 计算视频路径概率

Gaussian transition 给出：

\[
\log\pi_{\phi,\sigma}(\tau^v\mid o,c)
=
\sum_k
\log\mathcal N
\left(
z_{k+1};
z_k+\Delta t f_{\theta,\phi},
\sigma_k^2\Delta t I
\right).
\]

因此可以计算 PPO 所需的新旧策略 likelihood ratio。

### 4.3 同状态生成四个未来

每个 task-state 采样 \(K=4\) 条路径：

\[
G_s=
\{\tau^v_{s,1},\tau^v_{s,2},\tau^v_{s,3},\tau^v_{s,4}\}.
\]

每个未来独立转成动作并在环境中执行，最终得到四个 reward。

### 4.4 同状态 group-relative credit

\[
A_{s,i}
=
R_{s,i}
-
\frac{1}{K}\sum_{j=1}^{K}R_{s,j}.
\]

如果一组结果为 `[1, 0, 0, 1]`：

- 两条成功 future 获得正 advantage；
- 两条失败 future 获得负 advantage。

全成功或全失败组的中心化 advantage 为零，不提供相对策略梯度。

### 4.5 PPO 更新

\[
\rho_{s,i}
=
\exp
\left[
\log\pi_{\phi,\sigma}(\tau^v_{s,i})
-
\log\pi_{\mathrm{old}}(\tau^v_{s,i})
\right].
\]

\[
\mathcal L_{\mathrm{PPO}}
=
-
\mathbb E
\left[
\min
\left(
\rho A,
\operatorname{clip}(\rho,1-\epsilon,1+\epsilon)A
\right)
\right].
\]

Reward 绑定在完整视频路径上，所以 PPO 直接改变哪些未来更容易被 WAM 生成。

### 4.6 参数高效在线更新

当前训练：

- `transformer.proj_out` 内部 rank-8 LoRA；
- 20-step noise schedule。

保持冻结：

- WAM backbone；
- 原始 video projection；
- VAE decoder；
- text encoder；
- action head；
- IDM/action flow。

小规模参数更新可以降低显存、限制灾难性遗忘，并支持多轮在线训练。

### 4.7 多轮闭环

```text
R0 WAM
  → 收集 1,280 条在线轨迹
  → PPO
R1 WAM
  → 新 state panel
  → PPO
R2 WAM
  → 新 state panel
  → PPO
R3 WAM
  → matched final evaluation
```

---

## 5. 论文贡献

### Contribution 1：WAM 的在线后训练问题

我们将部署阶段机器人交互正式建模为预训练 WAM 的在线训练信号，闭合“预测未来—执行动作—获得结果—更新模型”的循环。

### Contribution 2：可计算 likelihood 的随机视频策略

我们把内部 deterministic video flow 转换为可 replay 的 stochastic path，使完整视频生成轨迹可以计算 likelihood，并支持 on-policy RL。

### Contribution 3：同状态终局 reward 归因

我们从同一个 simulator state 生成多个未来，并使用 group-relative PPO 将最终任务 reward 直接归因到不同视觉未来的相对概率。

### Contribution 4：可扩展评测协议

我们建立多轮、十 seed 的 LIBERO 评测协议，明确区分在线数据收集、训练、matched evaluation、泛化、消融、效率和真机实验。

这些才是论文贡献。LoRA、噪声或具体工程实现只是让 Online-WAM 闭环成立的技术组件。

---

## 6. Related Work

### 6.1 视频生成作为机器人规划

#### UniPi

UniPi 将 text-conditioned video generation 作为通用策略表示，再把预测视频转换成动作。

**与本文区别：**

- UniPi 证明视频生成可以表示策略；
- Online-WAM 研究部署后的 WAM 如何通过在线 reward 持续改进。

论文：https://arxiv.org/abs/2302.00111

#### Video Language Planning

Video Language Planning 使用视频和语言计划进行搜索，并将中间视觉目标转成动作。

**与本文区别：**

- VLP 主要通过 inference-time search 和 value function 改进规划；
- Online-WAM 通过真实交互更新未来生成模型参数。

论文：https://arxiv.org/abs/2310.10625

#### NovaPlan 等闭环视频规划

近期视频规划方法增加了执行监控、关键点、几何约束和在线 replanning。

**与本文区别：**

- 这些方法重点是单次任务内的闭环规划；
- Online-WAM 重点是跨交互轮次的模型学习。

论文：https://arxiv.org/abs/2602.20119

### 6.2 World Action Model

#### LingBot-VA

LingBot-VA 将机器人控制建模为 causal world modeling，联合预测视觉动态和机器人动作。

**与本文区别：**

- LingBot-VA 提供预训练 video-action architecture；
- Online-WAM 给其内部生成过程加入 simulator-grounded online RL。

论文：https://arxiv.org/abs/2601.21998

#### DreamZero

DreamZero 证明联合生成 video 和 action 的 WAM 可以实现 zero-shot 物理泛化与闭环控制。

**与本文区别：**

- DreamZero 重点是大规模预训练和 zero-shot capability；
- Online-WAM 重点是部署后如何从成功和失败中持续学习。

论文：https://arxiv.org/abs/2602.15922

### 6.3 自我改进视觉机器人规划

#### SILVR

SILVR 将离线数据和在线经验结合，迭代改进 task-specific visual planner，是最接近本文的 related work。

**Online-WAM 的区别：**

1. 目标是联合 video-action WAM，而不是单独 task video planner；
2. 在线策略是完整、可 replay 的内部 flow path；
3. 使用显式 path likelihood 和 group-relative PPO；
4. 下游 action conversion 保持不变，从而隔离 WAM adaptation。

论文：https://arxiv.org/abs/2506.06658

### 6.4 Diffusion / Flow 动作策略

Diffusion Policy 使用 conditional diffusion 建模多模态机器人动作。Flow-matching policy 使用连续生成轨迹建模 action distribution。

**与本文区别：**

- 这些方法直接优化动作分布；
- Online-WAM 优化动作执行之前的未来视频轨迹。

论文：

- Diffusion Policy：https://arxiv.org/abs/2303.04137
- Flow Matching：https://arxiv.org/abs/2210.02747

### 6.5 Diffusion / Flow 模型的 RL

DDPO、DPOK 和 AlignProp 使用 reward 或 preference 优化扩散生成模型。ReinFlow 为 flow-based robot policy 构造 stochastic path likelihood，并进行在线 RL。

**与本文区别：**

- 现有机器人 flow RL 主要优化 action-flow policy；
- Online-WAM 将 likelihood-based RL 放到 WAM 内部视频生成路径上。

论文：

- DDPO：https://arxiv.org/abs/2305.13301
- DPOK：https://arxiv.org/abs/2305.16381
- AlignProp：https://arxiv.org/abs/2307.11464
- ReinFlow：https://arxiv.org/abs/2505.22094

### 6.6 World-model RL

Dreamer、DayDreamer 和 TD-MPC2 学习 latent dynamics，并在模型中进行 imagined rollout。

**与本文区别：**

- 传统 world-model RL 通常包含单独 actor、critic 或 planner；
- Online-WAM 把高维未来视频生成轨迹本身作为接受 reward 的策略对象。

论文：

- DreamerV3：https://arxiv.org/abs/2301.04104
- DayDreamer：https://arxiv.org/abs/2206.14176
- TD-MPC2：https://arxiv.org/abs/2310.16828

### 6.7 Online / Offline-to-Online Robot Learning

QT-Opt、RLPD 等工作表明，离线数据初始化的机器人策略可以通过真实交互继续提高。

**与本文区别：**

- 它们主要更新 action policy 和 value function；
- Online-WAM 更新预训练 WAM 的未来生成机制。

论文：

- QT-Opt：https://arxiv.org/abs/1806.10293
- RLPD：https://arxiv.org/abs/2302.02948

### 6.8 参数高效机器人适配

LoRA 和 adapter 可以用较少参数更新大型预训练模型。

在本文中，参数高效不是核心贡献，而是实现多轮在线 WAM 更新、降低遗忘和显存成本的手段。

论文：https://arxiv.org/abs/2106.09685

---

## 7. 完整实验计划

### 7.1 主实验

比较：

- R0：预训练模型；
- R1：一次在线更新；
- R2：两次在线更新；
- R3：三次在线更新。

要求：

- 完全相同的 evaluation tasks；
- 完全相同的 fresh states；
- 完全相同的 stochastic seeds；
- 10 个独立 training seeds；
- deterministic mean 和 stochastic mode。

指标：

- overall simulator success；
- 每个 task 的成功率；
- 每个 seed 的成功率；
- paired R1-R0、R2-R0、R3-R0 提升；
- confidence interval；
- held-out task success；
- policy calls、wall time 和推理成本。

### 7.2 当前已完成结果

#### Screening

- Deterministic ODE：7 / 120 成功；
- Stochastic SDE pool：15 / 239 成功。

两组 screening 用于发现可学习任务，不是最终 matched ODE-SDE 结论。

#### R0

- 1,280 / 1,280 条完整轨迹；
- 289 success；
- 991 failure；
- 0 infra；
- 22.6% episode success。

#### Reward-bearing groups

- 320 个同状态四路径组；
- 129 个组同时包含成功和失败。

#### 第一次在线更新

- 10 个 PPO update 全部完成；
- 10 个 R1 checkpoint；
- mean LoRA update norm：0.03027；
- maximum replay error：0.01619；
- maximum KL：\(3.42\times10^{-9}\)；
- 成功 path 的平均 log-probability 增量高于失败 path。

#### 当前 R1

R1 checkpoint 正在新的 state panel 上运行。当前使用 8 张 GPU、20 个 rollout worker。

---

## 8. 必须完成的消融

### 8.1 探索消融

| 消融 | 回答的问题 |
|---|---|
| Deterministic ODE | 随机探索是否必要？ |
| Fixed SDE | 固定噪声是否已经足够？ |
| Learned SDE | 学习 noise schedule 是否有效？ |
| \(K=1,2,4,8\) paths | 每个 state 需要多少未来？ |
| 不同初始 \(\sigma\) | 对噪声大小是否敏感？ |

### 8.2 更新参数消融

| 消融 | 回答的问题 |
|---|---|
| Video-head LoRA only | 只更新视频头是否足够？ |
| Noise schedule only | 只改变探索是否有效？ |
| LoRA + noise | 完整方法是否最好？ |
| Action head only | 直接更新动作是否更强或更不稳定？ |
| Video + action heads | 联合更新是否值得？ |
| LoRA rank 4/8/16 | 需要多大 adaptation capacity？ |

### 8.3 Reward 与 credit 消融

| 消融 | 回答的问题 |
|---|---|
| 正确 terminal reward | 完整方法 |
| task 内 shuffled reward | 是否依赖正确归因？ |
| uniform reward | 无信息 reward 时是否仍会变化？ |
| ungrouped advantage | 同状态 grouping 是否重要？ |
| terminal vs stage reward | dense credit 是否更好？ |
| success-only fine-tuning | RL 是否优于只拟合成功轨迹？ |

### 8.4 Online training 消融

- R0/R1/R2/R3 online learning curve；
- 25%/50%/100% online data；
- 只训练最新 round vs replay 旧 round；
- shared WAM vs task-specific WAM；
- 是否需要更新更深层 WAM block。

### 8.5 泛化实验

- held-out initial states；
- held-out tasks；
- held-out objects；
- spatial → object task transfer；
- 新相机、光照和背景；
- clutter 和 distractor；
- 更长 horizon。

### 8.6 效率实验

- WAM call 数；
- 生成 frame 数；
- episode wall time；
- GPU memory；
- 每提升一个成功率点需要多少 online trajectories；
- LoRA 前后 inference latency。

---

## 9. Case Study

每个 case 使用同一个 observation 和任务，对比：

1. 初始机器人画面；
2. R0 预测视频；
3. R1/R2/R3 预测视频；
4. 对应动作轨迹；
5. simulator execution；
6. 最终 verdict；
7. 变化原因。

推荐：

- 不稳定抓取变成稳定抓取；
- 正确物体但错误目标变成正确放置；
- 过早松爪变成完成放置；
- 抽屉碰撞变成成功打开；
- 在线训练仍无法解决的失败案例。

---

## 10. 真机实验计划

### 10.1 最小真机实验

比较：

- pretrained R0；
- simulator-trained R3；
- R3 + 少量真实在线适配。

选择 3-5 个桌面任务：

- 物体放入容器；
- 碗或杯子放置；
- 打开抽屉；
- articulated object interaction；
- 空间关系放置。

每个 checkpoint、每个任务至少：

- 20 次 trial；
- 多个初始位置；
- 多个光照和背景条件。

指标：

- task success；
- human intervention rate；
- collision / force-limit event；
- 平均完成时间；
- WAM call 数；
- recovery 次数。

### 10.2 真实在线适配

每个任务收集：

- 20-50 次真实交互；
- reward 来自人类或独立视觉 verifier；
- policy 执行前不能看到 reward；
- 使用 action clipping 和 workspace boundary。

比较：

1. 不做真实适配；
2. 只拟合成功轨迹；
3. Online-WAM terminal-reward PPO。

核心真机问题：

> WAM 能否用少量真实任务结果持续改进，而不需要重训完整机器人策略？

### 10.3 Sim-to-Real 诊断

- 视频预测 calibration；
- 物体轨迹一致性；
- grasp-contact timing；
- domain shift sensitivity；
- action latency；
- failure recovery；
- simulator task forgetting。

### 10.4 安全约束

- 受限 Cartesian workspace；
- velocity 和 force limit；
- emergency stop；
- human reset；
- collision monitoring；
- 不允许超出预定义任务几何范围的自主探索。

---

## 11. 论文图表计划

### Figure 1：方法总览

```text
观察 + 任务
  → 随机 WAM 未来
  → 冻结 action conversion
  → 环境执行
  → terminal reward
  → group-relative PPO
  → 更新 WAM
```

### Figure 2：为什么需要在线训练

同一个 state 展示：

- 一个视觉合理但任务失败的未来；
- 一个真正完成任务的未来。

### Figure 3：主 learning curve

R0/R1/R2/R3 matched success，附 10-seed confidence interval。

### Figure 4：核心消融

ODE、fixed SDE、learned SDE、LoRA-only、noise-only、shuffled reward。

### Figure 5：预测视频 Case Study

展示训练前后 future video、action 和 simulator verdict。

### Figure 6：真机

R0、simulator-trained、real-online-adapted 的成功率和 sample efficiency。

---

## 12. 最终论文定位

这篇论文的核心不是：

- 给 flow 加噪声；
- 使用 LoRA；
- 只调一个 LIBERO task；
- 在多个视频之间做选择。

真正的论文主张是：

> **将预训练 World Action Model 变成能够通过机器人交互持续改进的在线学习系统。**

SDE path、likelihood、group-relative PPO 和 LoRA 是让 WAM online training 闭环成立的技术组件。

---

## 参考文献

1. UniPi: https://arxiv.org/abs/2302.00111
2. Video Language Planning: https://arxiv.org/abs/2310.10625
3. LingBot-VA: https://arxiv.org/abs/2601.21998
4. DreamZero: https://arxiv.org/abs/2602.15922
5. SILVR: https://arxiv.org/abs/2506.06658
6. Diffusion Policy: https://arxiv.org/abs/2303.04137
7. Flow Matching: https://arxiv.org/abs/2210.02747
8. ReinFlow: https://arxiv.org/abs/2505.22094
9. DDPO: https://arxiv.org/abs/2305.13301
10. DPOK: https://arxiv.org/abs/2305.16381
11. AlignProp: https://arxiv.org/abs/2307.11464
12. DreamerV3: https://arxiv.org/abs/2301.04104
13. DayDreamer: https://arxiv.org/abs/2206.14176
14. TD-MPC2: https://arxiv.org/abs/2310.16828
15. QT-Opt: https://arxiv.org/abs/1806.10293
16. RLPD: https://arxiv.org/abs/2302.02948
17. LoRA: https://arxiv.org/abs/2106.09685
