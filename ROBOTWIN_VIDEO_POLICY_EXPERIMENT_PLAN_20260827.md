# RoboTwin Video-Policy RL Experiment Plan

**Date:** 2026-08-27  
**Scope:** RoboTwin only  
**Backbones:** LingBot-VA and Fast-WAM  
**Frozen executor:** IDM/action decoder unless explicitly used as an ablation

## 1. Paper Thesis

The paper studies whether a World-Action Model can be improved by optimizing
its generated future videos as a policy, rather than only fine-tuning an action
model or imitating successful videos.

The main hypothesis is:

> Direct video-space online RL can expand the distribution of executable
> futures beyond a fixed offline dataset, and therefore improve robot success
> more efficiently than reward-filtered fine-tuning or offline video RL.

## 2. Claims

| Claim | Minimum convincing evidence |
|---|---|
| C1. A video reward can identify futures that are more likely to execute successfully. | On frozen same-state candidate banks, reward-top must beat random selection and correlate with simulator success across skill families. |
| C2. Online video-space RL improves the WAM more than offline RFT and offline RL under matched samples and gradient updates. | Ten independent seeds; fresh-state success curves versus cumulative samples and gradient steps; online RL must exceed both offline methods. |
| C3. The gain comes from optimizing the video policy, not the IDM, action policy, or a deterministic ODE mean. | Action-space RL, ODE-offline, fixed-SDE, and reward-component ablations. |
| C4. The method transfers across explicit and implicit WAM variants. | Matched LingBot-VA, Fast-WAM-IDM, and Fast-WAM direct-action experiments. |

## 3. RoboTwin Task Matrix

The task list is frozen before outcome screening. Tasks are not removed because
their first results are inconvenient.

### Main 12 Tasks

| Family | Task | Existing screen success |
|---|---|---:|
| Tool use | `beat_block_hammer` | 14/16 |
| Tool use | `stamp_seal` | 12/16 |
| Contact / articulation | `click_alarmclock` | 12/24 |
| Contact / articulation | `turn_switch` | 5/24 |
| Bimanual coordination | `lift_pot` | 18/24 |
| Bimanual coordination | `handover_mic` | 23/24 |
| Bimanual coordination | `scan_object` | 11/16 |
| Bimanual coordination | `place_dual_shoes` | 12/16 |
| Sequential manipulation | `place_bread_basket` | 7/24 |
| Sequential manipulation | `place_burger_fries` | 23/24 |
| Spatial relation | `place_a2b_left` | 13/16 |
| Precision-control anchor | `move_stapler_pad` | 7/24 |

### Held-Out Transfer Tasks

- `place_object_basket`
- `move_can_pot`
- `place_can_basket`
- `place_container_plate`

### Task-Selection Rule

1. Freeze skill families and task names first.
2. Search for informative environment states inside each task.
3. Never replace a difficult skill family with another placement task.
4. All methods use identical task, state, video, action, and flow-path seeds.

## 4. Existing Data

The historical RoboTwin screen contains:

- 20 tasks;
- 416 complete simulator rollouts;
- 266 success and 150 failure;
- zero infrastructure exclusions;
- four replayable video paths per environment state.

This dataset is used for reward calibration and pilot training. The ten-seed
main result uses a newly frozen state split.

## 5. Video-First Reward

Every WAM-generated video chunk receives its own reward. The main reward is not
an action score and is not only the final simulator verdict.

### 5.1 Predicted-Video Score

`R_video` is computed from the language instruction and uniformly sampled
frames from the imagined video:

- visible task progress;
- correct object and target identity;
- correct manipulation stage;
- temporal and contact continuity;
- physical plausibility;
- stable terminal configuration.

### 5.2 Plan-Execution Agreement

After the frozen IDM executes the video:

- compare predicted and realized visual progress;
- compare object relation, contact, and terminal configuration;
- penalize imagined success that cannot be realized.

This produces `R_agree`.

### 5.3 Terminal Outcome

`R_success` is the final RoboTwin simulator verdict and is used as an outcome
bonus and the authoritative evaluation metric.

### 5.4 Main Reward

All components are normalized within the same-state candidate group:

```text
R_total = 0.60 * R_video
        + 0.25 * R_agree
        + 0.15 * R_success
```

The weights are frozen before policy training. Video-only, agreement-only, and
terminal-only rewards are ablations.

## 6. Experiment Blocks

## B0. Reward Validity

**Purpose:** prove that the reward evaluates videos rather than merely
reconstructing the final action outcome.

- Data: historical 416-rollout candidate bank.
- Methods: video-only, execution-only, combined reward, random, oracle.
- Metrics:
  - same-state success-over-failure pair accuracy;
  - reward-top simulator success;
  - random-K simulator success;
  - rank correlation with task progress;
  - false-positive imagined-success rate.
- Gate:
  - combined reward-top must beat random on at least four skill families;
  - successful videos must rank above failed videos at least 70% of the time.

## B1. Offline RL vs Offline RFT

### Compared Systems

1. Base WAM.
2. Offline RFT: select reward-top video paths and maximize their likelihood.
3. Offline RL: use all paths with same-state group-relative video reward.

### Pilot

- 6 skill-balanced tasks.
- 3 independent seeds.
- 4 training states per task.
- 4 video paths per state.
- 288 training videos total.
- 10 fresh states per task for evaluation.

### Main

- 12 tasks.
- 10 independent seeds.
- Per seed: 4 training states per task and 4 paths per state.
- 1,920 complete training videos across all seeds.
- Fresh evaluation: 4 states per task, per seed, per policy.
- Primary metric: final RoboTwin task success.
- Secondary: video reward, plan-execution agreement, steps conditional on
  success, and policy KL.

## B2. Online RL vs Online RFT

Both methods receive exactly the same online samples.

### Online RFT

1. Collect four videos from each state.
2. Score every video.
3. Keep reward-top videos.
4. Fine-tune the video head.
5. Recollect with the updated WAM.

### Online RL

1. Collect the same four videos.
2. Score every video.
3. Compute same-state relative advantages.
4. Apply video-path PPO.
5. Recollect with the updated WAM.

### Curves

Evaluate frozen fresh states after:

```text
gradient steps:       0, 1, 2, 4, 8, 16
cumulative samples:   0, 192, 384, 768, 1536, 3072
```

Plot:

- gradient step versus success rate;
- cumulative simulator samples versus success rate;
- video reward versus realized success;
- success coverage across task families.

## B3. Real-Robot DAgger

Real-robot work is separated from the RoboTwin simulator denominator.

### Offline DAgger

- Collect human corrections.
- Aggregate the full correction dataset.
- Train between collection sessions.
- Evaluate the frozen checkpoint.

### Online DAgger

- Collect corrections in batches of ten episodes.
- Update the video head after each batch.
- Continue collection with the updated policy.

### Initial Real-Robot Skills

- switch/button interaction;
- precise object placement;
- bimanual handover;
- tool-target alignment.

Metrics include success, interventions, correction frames, samples to success,
and wall time.

## B4. Required Ablations

| Ablation | Question |
|---|---|
| Action-space RL | Is directly optimizing IDM/action diffusion better than video-space RL? |
| ODE offline | Does deterministic reward-weighted video fitting work without stochastic path optimization? |
| Fixed SDE | Is learned exploration necessary? |
| Mean-only deployment | Does the learned video mean explain the gain? |
| Video-only reward | Can imagined progress alone guide learning? |
| Execution-only reward | Is the video scorer unnecessary? |
| No agreement reward | Does plan-execution consistency matter? |
| Terminal-only reward | Is dense per-video credit necessary? |
| Offline data only | Is online recollection necessary? |

## B5. Cross-Model Experiments

### LingBot-VA

- Original explicit future-video generation plus frozen IDM.
- Offline RFT.
- Offline video RL.
- Online video RL.

### Fast-WAM-IDM

- Enable its future-video / IDM path.
- Apply the same reward and matched RL/RFT protocol.

### Fast-WAM Direct Action

- Keep the original direct-action path.
- Run action-space RL as the architecture-matched comparison.
- Compare against Fast-WAM-IDM video-space RL.

## 7. Metrics

### Primary

- final simulator task success;
- task-family macro success;
- ten-seed mean and confidence interval;
- samples required to reach a fixed success level.

### Reward Validity

- reward-top success;
- success/failure pair accuracy;
- calibration of video score versus actual success;
- imagined-success false-positive rate.

### Efficiency

- simulator episodes;
- WAM calls;
- gradient steps;
- GPU time;
- wall time;
- tokens/VLM calls used by the video scorer.

## 8. Run Order And ETA

| Stage | Work | Estimated time on 8 GPUs |
|---|---|---:|
| M0 | Dataset index, case site, reward-scoring smoke | 6-10 hours |
| M1 | Reward validity on existing 416 rollouts | 8-12 hours |
| M2 | Offline RL/RFT pilot | 8-12 hours |
| M3 | Ten-seed offline main | 2-3 days |
| M4 | Online RL/RFT learning curves | 3-5 days |
| M5 | Required ablations | 2-3 days |
| M6 | LingBot-VA/Fast-WAM cross-model study | 3-5 days |
| M7 | Real-robot DAgger | 3-5 hardware days |

Paper-minimum simulation evidence is expected in approximately 5-7 days.
The complete simulation package including cross-model extras is approximately
10-14 days. Real-robot time is separate.

## 9. Stop / Go Gates

1. Do not start policy training until video reward beats random selection.
2. Do not promote an offline checkpoint from training loss.
3. Do not claim online benefit unless it beats online RFT at matched samples.
4. Do not claim video-space benefit unless it beats action-space RL.
5. Do not claim architecture generality until both LingBot-VA and Fast-WAM are
   evaluated.
6. Count success only from the final RoboTwin verdict.

## 10. Paper Tables And Figures

- **Table 1:** 12-task ten-seed main comparison.
- **Figure 3:** gradient steps and cumulative samples versus success.
- **Table 2:** action-space, ODE, reward, and online-refresh ablations.
- **Table 3:** LingBot-VA versus Fast-WAM.
- **Figure 4:** predicted video, realized video, reward decomposition, and
  terminal outcome case studies.
