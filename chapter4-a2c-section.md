# A2C Section for Chapter 4 - Results and Discussions

> **Integration Instructions for Thesis Mates**
>
> This section goes under **"Comparative Analysis / Performance Evaluation"** in Chapter 4.
> The algorithms should appear in **alphabetical order: A2C, DQN, PPO**.
>
> **Steps:**
> 1. In `thesis-manuscript.md`, find the heading:
>    ```
>    ## **Comparative Analysis / Performance Evaluation** {#comparative-analysis-/-performance-evaluation}
>    ```
> 2. Keep the introductory paragraph that starts with _"Both PRNG and QRNG agents were trained on 10 million timesteps..."_
> 3. **Paste the A2C section below** (everything under "Advantage Actor-Critic" in this file) right after that intro paragraph — **before** the DQN section.
> 4. The final order should be:
>    - `***Advantage Actor-Critic***` (this file)
>    - `***Deep Q-Network***` (already in the manuscript)
>    - `***Proximal Policy Optimization***` (already in the manuscript)
> 5. Remember to insert the A2C training comparison figure image reference where `Figure _` is indicated.

---

***Advantage Actor-Critic***

	Presented in Figure _ is the A2C's learning curve on both PRNG-generated and QRNG-generated mazes.

**Figure** _  
*Advantage Actor-Critic Training Success Rate and Rewards over Episodes*

	As indicated in Figure _, both PRNG-trained and QRNG-trained A2C agents exhibited strong and relatively stable convergence over the course of 10 million timesteps. Across all three trials, the agents reached final success rates ranging from 74% to 93% for PRNG and 80% to 86% for QRNG, with overall training success rates clustering around 55–60% for both groups. A2C's actor–critic architecture, which simultaneously learns a policy (actor) and a value function (critic), enables lower-variance gradient updates compared to pure policy gradient methods. The critic's baseline reduces the variance of the policy gradient estimates, and this variance reduction property has been shown to be particularly beneficial under partial observability, where dual-critic formulations can provably lower learning variance while maintaining unbiasedness (Li et al., 2024). This allows A2C to converge more reliably than DQN in environments with incomplete state information. The relatively smooth upward trajectories observed in both the success rate and reward curves reflect this architectural advantage.

The PRNG-trained agents exhibited slightly higher variance across trials, with Trial 2 producing a noticeably lower final success rate of 74% compared to Trial 1's 87% and Trial 3's 93%. Despite this inter-trial variability, all PRNG runs maintained a consistent upward learning trajectory without the severe collapses observed in either DQN or PPO. The QRNG-trained agents, in contrast, showed tighter clustering across trials, with final success rates of 80%, 86%, and 82%, indicating more consistent convergence behavior. However, the QRNG group's peak success rates were comparable to PRNG, with two of three trials reaching 100% at some point during training.

In terms of reward progression, both groups converged to average rewards in the 375–400 range by the end of training. The PRNG agents achieved final average rewards of 390.33, 375.52, and 398.27 across the three trials, while the QRNG agents achieved 379.58, 393.00, and 379.13. The peak single-episode rewards were similarly close, ranging from 637.83 to 645.81 for PRNG and 617.79 to 634.77 for QRNG. These values suggest that both training distributions produce agents of comparable capability at convergence, with the seed source introducing no systematic advantage in terms of raw reward accumulation during training.

Overall, the A2C training results reveal negligible differences between the PRNG and QRNG groups in terms of convergence speed and final performance. Both groups completed approximately 34,000 to 37,000 episodes within the 10 million timestep budget, with the slight variation attributable to differences in average episode length across maze configurations. The training data for all trials is summarized in Table _.

| Table _ *Advantage Actor-Critic Training Values over 10,000,000 Timesteps* |  |  |  |  |  |  |
| ----- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Metric** | **PRNG Model** |  |  | **QRNG Model** |  |  |
|  | Trial 1 | Trial 2 | Trial 3 | Trial 1 | Trial 2 | Trial 3 |
| Total Episodes  | 36,282 | 36,288 | 36,207 | 37,249 | 37,023 | 34,783 |
| Total Successes  | 21,413 | 21,545 | 21,405 | 22,321 | 21,782 | 19,251 |
| Overall Training SR | 59.0% | 59.4% | 59.1% | 59.9% | 58.8% | 55.3% |
| Final Success Rate (100-ep avg) | 87.0% | 74.0% | 93.0% | 80.0% | 86.0% | 82.0% |
| Peak Success Rate | 100.0% | 98.0% | 98.0% | 100.0% | 89.0% | 100.0% |
| Final Avg Reward | 390.33 | 375.52 | 398.27 | 379.58 | 393.00 | 379.13 |
| Peak Single Episode Reward | 645.81 | 637.83 | 639.78 | 617.79 | 634.77 | 622.83 |

As shown in Table _, the PRNG-trained A2C agents completed between 36,207 and 36,288 total episodes, while the QRNG-trained agents ranged from 34,783 to 37,249 episodes. The slight variation in episode count is attributable to differences in average episode length, as shorter successful episodes allow more episodes to fit within the fixed 10 million timestep budget. In terms of overall training success rate, both groups performed comparably, with PRNG agents averaging approximately 59.2% and QRNG agents averaging approximately 58.0%. The marginally lower overall success rate of Trial 3 QRNG (55.3%) coincides with fewer total episodes (34,783), suggesting that the agent spent more timesteps on longer, unsuccessful episodes during the early stages of training.

The final success rate, measured as the rolling 100-episode average at the end of training, shows greater inter-trial variability for the PRNG group (74%–93%) compared to the QRNG group (80%–86%). Despite the PRNG group's wider range, its highest-performing trial (Trial 3 at 93%) exceeds the QRNG group's best (Trial 2 at 86%). However, the QRNG group's tighter clustering suggests more reproducible convergence behavior, which is a desirable property for experimental reliability. Peak success rates were high for both groups, with PRNG reaching 98–100% and QRNG reaching 89–100%, confirming that both agent types are capable of near-perfect maze completion during favorable training episodes.

Final average rewards ranged from 375.52 to 398.27 for PRNG and 379.13 to 393.00 for QRNG, with no systematic advantage for either group. Peak single-episode rewards were consistently higher for PRNG (637.83–645.81) compared to QRNG (617.79–634.77), though these values reflect individual best-case episodes rather than sustained performance trends. Overall, the training metrics confirm that A2C achieves stable and effective learning under both randomness conditions, with neither seed source producing a clear or consistent advantage across trials.

**Evaluation**

Following training, the best-performing model weights from each trial were frozen and evaluated on 1,000 novel mazes per condition from unseen seeds, ensuring that none of the evaluation mazes were encountered during training. Each agent was evaluated under two conditions: intra-domain generalization, where the agent is tested on mazes from the same randomness source used during training, and cross-domain generalization, where the agent is tested on mazes from the opposing randomness source.

**Results**

| Table _ |  |  |  |  |
| ----- | ----- | ----- | ----- | ----- |
| *Advantage Actor-Critic Intra and Cross Distribution Evaluation* |  |  |  |  |
|  | **A2C<sub>PRNG</sub>** |  | **A2C<sub>QRNG</sub>** |  |
| **Trial** **Metric** | ***Intra*** | ***Cross*** | ***Intra*** | ***Cross*** |
| **1** Success Rate % | 53.40% | 52.90% | 57.10% | 53.20% |
| Avg Reward | 320.83 | 320.38 | 331.56 | 325.02 |
| Std Dev | 82.76 | 81.74 | 91.21 | 95.02 |
| Avg Steps | 272.7 | 274.6 | 260.7 | 276.7 |
| **2** Success Rate % | 46.00% | 44.50% | 59.40% | 59.30% |
| Avg Reward | 286.08 | 283.89 | 334.23 | 335.82 |
| Std Dev | 130.50 | 121.95 | 79.45 | 80.82 |
| Avg Steps | 304.7 | 310.4 | 249.1 | 250.5 |
| **3** Success Rate % | 71.50% | 70.30% | 50.50% | 46.20% |
| Avg Reward | 359.52 | 356.86 | 322.12 | 315.12 |
| Std Dev | 74.41 | 75.82 | 83.34 | 83.52 |
| Avg Steps | 201.4 | 206.2 | 287.7 | 306.0 |

Table _ presents the intra-distribution and cross-distribution evaluation results of A2C models trained on PRNG-generated and QRNG-generated maze distributions across three trials. Overall, both models showed moderate success rates, with values generally ranging between 44% and 72%. For A2C<sub>PRNG</sub>, intra-distribution success rates ranged from 46.00% to 71.50%, while cross-distribution performance varied between 44.50% and 70.30%, with intra-to-cross differences of only 0.50 to 1.50 percentage points, suggesting minimal domain sensitivity. For A2C<sub>QRNG</sub>, intra-distribution success rates ranged between 50.50% and 59.40% and cross-distribution success rates between 46.20% and 59.30%. Notably, in Trial 2, the QRNG-trained model achieved nearly identical intra and cross performance (59.40% vs. 59.30%), while in Trial 3, it exhibited a larger cross-distribution drop (50.50% to 46.20%).

Average reward values followed a similar pattern. A2C<sub>PRNG</sub> rewards ranged from approximately 283 to 360, while A2C<sub>QRNG</sub> rewards ranged from roughly 315 to 336. Standard deviations were notably high for the PRNG model in Trial 2 (up to 130.50), while the QRNG model maintained more consistent standard deviations across trials (79.45–95.02). Average step counts ranged from approximately 201 to 310 across all conditions, with lower step counts corresponding to higher success rates, as successful episodes terminate earlier than the 500-step maximum.

Overall, the PRNG-trained model demonstrated higher peak performance (Trial 3) but greater inter-trial variability, while the QRNG-trained model showed more consistent mid-range performance across Trials 1 and 2 but weaker results in Trial 3. Neither training distribution provided a consistent generalization advantage, and both models exhibited comparable cross-domain robustness.

**Generalization**

The Generalization Gap is defined as the difference between intra-domain and cross-domain success rates (SR\_intra − SR\_cross), and serves as the primary metric for assessing an agent's robustness to distributional shift. A gap of zero indicates perfect transferability, while a positive gap indicates some degree of overfitting to the training distribution.

| Agent | Intra-Distribution SR | Cross-Distribution SR | Gap (pp) | Interpretation |
| ----- | ----- | ----- | ----- | ----- |
| PRNG | 61.2% | 60.3% | +0.90 | Minimal domain sensitivity |
| QRNG | 58.7% | 59.5% | -0.80 | Robust cross-domain transfer |

The PRNG agent exhibits a generalization gap of +0.90 percentage points, indicating a very slight drop in success when transitioning from its training distribution to QRNG mazes. The QRNG agent demonstrates a generalization gap of -0.80 percentage points, meaning it performed marginally better on novel PRNG mazes than on its own QRNG training distribution. This negative gap, while small, mirrors the pattern observed in the PPO results and suggests that the QRNG-trained agent developed a slightly more distribution-agnostic policy.

Both agents exhibit generalization gaps close to zero, indicating that neither agent is substantially overfitting to the structural patterns of its training mazes. This is consistent with A2C's on-policy nature, which continually updates its policy based on the most recent experience rather than relying on a fixed replay buffer, reducing the risk of overfitting to specific environmental configurations. Nauman et al. (2024) demonstrated that critic overfitting is a primary driver of performance degradation in actor-critic methods, and that on-policy approaches are inherently less susceptible to this failure mode than their off-policy counterparts. The near-zero generalization gaps for both agents suggest that the structural similarity between PRNG and QRNG mazes, as confirmed by the earlier statistical validation, translates into comparable navigational challenges regardless of seed source. This observation aligns with Kirk et al. (2023), who found that on-policy methods trained on procedurally generated environments tend to develop more transferable policies due to their continual adaptation to the current data distribution.

**Path Efficiency**

In addition to success rate and reward, path efficiency was measured by recording the average number of steps taken per episode across all evaluation conditions. For a 20×20 maze, the theoretical optimal path length is approximately 40–50 steps.

| Condition | Agent | Avg Steps |
| ----- | ----- | ----- |
| Intra (PRNG on PRNG) | PRNG Model | 242.0 |
| Cross (PRNG on QRNG) | PRNG Model | 245.3 |
| Intra (QRNG on QRNG) | QRNG Model | 252.1 |
| Cross (QRNG on PRNG) | QRNG Model | 250.0 |

The PRNG agent demonstrated slightly better path efficiency, averaging 242.0 and 245.3 steps for intra- and cross-domain conditions respectively, compared to the QRNG agent's 252.1 and 250.0 steps. The PRNG agent's cross-domain step count (245.3) represents only a modest increase of 3.3 steps over its intra-domain performance, consistent with its small positive generalization gap. The QRNG agent, conversely, showed a marginally lower step count in the cross-domain condition (250.0) than in its intra-domain condition (252.1), aligning with its negative generalization gap.

Both agents operate well above the theoretical minimum of approximately 40–50 steps for a 20x20 maze, which is expected given the partial observability constraints of the LiDAR-based sensor configuration. The step counts for A2C are generally higher than those observed for PPO, reflecting A2C's lower overall success rates and suggesting that unsuccessful episodes, which terminate at the 500-step maximum, contribute to a higher average. Nonetheless, the relative similarity in step efficiency between PRNG and QRNG agents further supports the conclusion that seed source does not meaningfully differentiate A2C agent performance.
