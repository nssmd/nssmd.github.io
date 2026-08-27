# RoboTwin 实验编号、实时状态与排期

**更新时间：** 2026-08-27 08:52 PDT  
**实验范围：** 仅 RoboTwin  
**当前实验：** E1 · Offline RL vs Offline RFT  
**当前步骤：** E1-S2a · Pilot数据采集运行中

## 1. 实验编号

| 编号 | 实验 | 步骤 |
|---|---|---|
| E1 | Offline RL vs Offline RFT | S1 数据与评分；S2 Pilot训练；S3 Pilot评测；S4 10-seed主训练；S5主评测 |
| E2 | Online RL vs Online RFT | S1状态集与Base；S2 Online RFT；S3 Online RL；S4六个checkpoint评测；S5画sample/step-success曲线 |
| E3 | Offline DAgger vs Online DAgger | S1硬件与任务；S2 Offline DAgger；S3 Online DAgger；S4统一真机评测 |
| E4 | Action-space RL消融 | S1复用冻结数据；S2训练；S3 matched fresh evaluation |
| E5 | ODE Offline消融 | S1训练；S2 matched fresh evaluation；S3与E1汇总 |
| E6 | Fast-WAM-IDM RL / RFT | S1接口与checkpoint；S2训练；S3 fresh evaluation |
| E7 | LingBot-VA原版 RL / RFT | S1原版checkpoint；S2 RFT；S3 RL；S4 fresh evaluation |

## 2. 当前正在做什么

### E1-S1 · 直接预测视频 Reward Smoke

| 子步骤 | 工作量 | 完成 | 状态 | ETA |
|---|---:|---:|---|---|
| E1-S1a | 32条视频评分吞吐smoke | 32 / 32 | 完成 | Reward-Top 75.0%，Random 59.4% |
| E1-S1b | 416条历史视频评分记录 | 416 / 416 | 完成 | 成败分叉组 +13.2pp |
| E1-S2a | Pilot训练数据采集 | 288条新rollout | 14 / 288 | 10 success / 4 failure / 0 infra |
| E1-S2b | Offline RL / RFT Pilot训练 | 36个task-seed-method jobs | 0 / 36 | 数据完成后启动 |
| E1-S3 | Pilot fresh evaluation | 540个episode | 0 / 540 | 按当前8 workers约4小时 |

E1-S1已经完成。E1-S2a已在PAI-4041启动：6个任务、12个state、每个state
4条ReinFlow路径，共288条新rollout；12个worker共享8张L20X。

**Reward状态说明：** 历史 RoboTwin RL 使用的是机器人执行后的 simulator
stage reward；它读取真实执行的分阶段进度与最终成功，不是直接看预测视频。
E1-S1 正在单独验证新的 direct-video scorer，只看执行前第一段 WAM 预测视频。
它通过 reward-top 对比 random 后，才决定是否用于 E1-S2 的 RL / RFT。

## 3. 已经完成了什么

| 项目 | 结果 |
|---|---|
| 历史数据盘点 | 20个任务，416条完整rollout |
| 数据结果 | 266 success / 150 failure / 0 infra |
| Low-seed fresh evaluation | 13 / 22 提升到 15 / 22 |
| 完整 learned-SDE evaluation | 68 / 110 提升到 71 / 110 |
| ODE mean-only evaluation | 145 / 220 下降到 133 / 220 |
| Case Study | 5个case，10段预测/执行视频 |
| 主任务集合 | 12个RoboTwin任务已固定 |

## 4. Data

### 已有数据

- 20个 RoboTwin 任务
- 416条完整视频与仿真执行 rollout
- 266条成功，占63.9%
- 150条失败，占36.1%
- 0条基础设施失败

### E1 Offline

| 阶段 | Tasks | Seeds | States / task / seed | Paths / state | 总视频 |
|---|---:|---:|---:|---:|---:|
| Pilot | 6 | 3 | 4 | 4 | 288 |
| Main | 12 | 10 | 4 | 4 | 1,920 |

### E2 Online

- 12个任务
- 10个独立seed
- RL和RFT各自最多3,072条online sample
- 在0、192、384、768、1,536、3,072条sample时评测

## 5. Task

| 类别 | RoboTwin任务 |
|---|---|
| 工具使用 | `beat_block_hammer` |
| 工具使用 | `stamp_seal` |
| 接触与关节 | `click_alarmclock` |
| 接触与关节 | `turn_switch` |
| 双臂协作 | `lift_pot` |
| 双臂协作 | `handover_mic` |
| 双臂协作 | `scan_object` |
| 双臂协作 | `place_dual_shoes` |
| 多物体序列 | `place_bread_basket` |
| 多物体序列 | `place_burger_fries` |
| 空间关系 | `place_a2b_left` |
| 精确控制 | `move_stapler_pad` |

## 6. ETA计算依据

2026-08-27 01:06 PDT 实测：

- PAI-4041：8张 NVIDIA L20X
- 每张显存：143.8GB
- 当时可用：8 / 8张
- PAI-4042有其他训练和评测，不计入本实验算力
- 仿真排期按8个并发worker计算
- 历史同管线中位耗时按185秒/episode计算
- 加15%调度、重启和落盘开销
- 视频评分不使用GPU episode公式，先测E1-S1a的32条真实吞吐

仿真估算公式：

```text
wall_hours = episodes × 185秒 ÷ 8 workers ÷ 3600 × 1.15
```

## 7. 以后做什么

| 顺序 | 编号 | 实验 | 规模 | 当前步骤 | 按当前算力预计 |
|---:|---|---|---|---|---|
| 1 | E1 | Offline RL vs Offline RFT | Pilot 6 tasks × 3 seeds；Main 12 tasks × 10 seeds | S1 / 5 | Pilot 8-10小时；Main 30-40小时 |
| 2 | E2 | Online RL vs Online RFT | 12 tasks × 10 seeds；3,072 samples / method | S0 / 5 | 4-5天 |
| 3 | E4 | Action-space RL消融 | 12 tasks × 3 seeds | S0 / 3 | 8-12小时 |
| 4 | E5 | ODE Offline消融 | 12 tasks × 3 seeds | S0 / 3 | 8-12小时 |
| 5 | E6 | Fast-WAM-IDM RL / RFT | 至少8 tasks × 3 seeds | S0 / 3 | 12-18小时 |
| 6 | E7 | LingBot-VA原版 RL / RFT | 至少8 tasks × 3 seeds | S0 / 4 | 12-18小时 |
| 7 | E3 | Offline DAgger vs Online DAgger | 4类真机任务 | S0 / 4 | GPU无法决定；硬件排期后计算 |

除真机外，在PAI-4041持续提供8张卡且没有基础设施中断的前提下，当前完整仿真排期约8-10天。E1-S1a完成后会用实测评分吞吐更新这一数字。
