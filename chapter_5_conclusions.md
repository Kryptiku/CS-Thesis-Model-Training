# **CHAPTER 5**

**SUMMARY, CONCLUSIONS, AND RECOMMENDATIONS**

## **5.2 Conclusions**

Based on the results and findings of the study, the following conclusions were drawn in accordance with the specific objectives:

1. QRNG and PRNG seeds produced no statistically significant differences in the structural complexity or diversity of procedurally generated maze environments. Both univariate (Mann-Whitney U, all p > 0.05) and multivariate (PERMANOVA, p = 0.7493) tests confirmed that the two seed sources yielded statistically equivalent maze distributions. The study established that the maze generation algorithm, not the entropy source, is the primary determinant of structural output in procedural content generation.

2. QRNG-seeded training environments did not significantly alter the learning rate of DRL agents compared to PRNG-seeded environments. Across A2C, DQN, and PPO, both seed conditions produced comparable training success rates and reward progression over 10 million timesteps. The study confirmed that seed-level entropy differences alone do not influence the training dynamics of DRL agents when the generated environments are structurally equivalent.

3. DRL agents trained on QRNG-seeded mazes did not achieve a consistent generalization advantage over PRNG-trained agents on unseen environments in terms of success rate, reward, efficiency, or generalization gap. All generalization gaps remained within plus or minus 2.6 percentage points across all architectures. The study validated that, within the scope of 2D maze navigation using recursive backtracking, the source of seed-level randomness has no measurable impact on the navigational robustness and zero-shot generalization capability of DRL agents.

## **5.3 Recommendations**

Based on the conclusions of the study, the following recommendations are proposed:

1. Since the study established that the recursive backtracking algorithm acts as the structural bottleneck, future studies should test QRNG seeds with generation algorithms that have higher sensitivity to input entropy, such as Wilson's algorithm, Prim's algorithm, or wave function collapse, to determine whether QRNG produces measurable structural differences when the algorithm does not constrain output diversity.

2. Future implementations should explore integrating QRNG entropy directly into the step-by-step decisions of the generation algorithm, rather than limiting its use to seed initialization, to test whether continuous quantum randomness throughout the generation process yields effects that single-seed substitution does not.

3. The experimental framework should be extended to larger maze sizes (30x30 or 40x40) and 3D navigation environments, where the increased state space and environmental dimensionality may amplify entropy differences that were undetectable in the 20x20 2D maze setting of this study.

4. Given the partial observability limitations observed in standard DQN during training, future studies should adopt recurrent DRL architectures such as DRQN or recurrent PPO, which integrate observations over time and may provide a more reliable value-based baseline for evaluating the effects of training environment diversity on agent generalization.

5. The observation that QRNG-trained PPO agents exhibited tighter inter-trial clustering warrants a dedicated training stability study with a larger number of runs (ten or more per condition) to determine whether QRNG-seeded environments consistently produce more reproducible convergence behavior across DRL architectures.

6. The seed-level substitution framework developed in this study should be replicated in other PCG domains, such as terrain generation, dungeon layout design, or road network simulation, to determine whether the findings are specific to maze generation or generalizable across procedural content types.

7. For practitioners in game development and simulation engineering, the findings support the use of PRNG seeds with recursive backtracking for procedurally generated maze environments, as QRNG introduces additional infrastructure requirements such as API dependency, rate limits, and non-reproducibility without measurable gains in structural diversity or agent performance within this scope.
