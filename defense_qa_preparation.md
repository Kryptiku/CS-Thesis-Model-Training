# Thesis Defense Q&A Preparation Guide

**Thesis:** Enhancing Autonomous Navigation Robustness in Unstructured Environments using Quantum-Seeded Procedural Maze Generation

**Defense Date:** April 8, 2026

**Golden Rule:** Never apologize for null results. Say "fail to reject the null hypothesis" with the same confidence as "significant improvement found." Both are valid scientific outcomes.

---

## Section 1: Problem Definition & Research Gap

### Q1. What is the research gap that your study addresses?

**Answer:** "Existing research on Quantum Random Number Generators has been concentrated in cryptography and Monte Carlo simulations. Meanwhile, Procedural Content Generation for AI training environments exclusively uses Pseudo-Random Number Generators. No study has empirically tested whether replacing PRNG seeds with QRNG seeds in a procedural generation pipeline produces structurally different environments or improves DRL agent generalization. Our study is the first to bridge these two domains."

*Why this works:* Establishes novelty clearly. The gap is factual and verifiable from the literature.

---

### Q2. Why is this research problem important?

**Answer:** "DRL agents are known to overfit to their training environments -- they memorize layouts rather than learning general navigation strategies. The quality and diversity of training environments directly affects generalization. While visual domain randomization has been studied extensively, structural randomization at the seed level has not. If quantum-sourced entropy could produce more diverse environments, it would have practical implications for robotics, autonomous vehicles, and game AI."

*Why this works:* Connects the abstract research to real-world applications without overclaiming.

---

### Q3. Why mazes? Why not other types of procedural environments?

**Answer:** "Mazes provide a controlled, well-studied benchmark for navigation tasks. They have clearly defined structural metrics -- path length, tortuosity, dead-end count, junction proportions -- that allow objective, quantitative comparison between PRNG and QRNG outputs. More complex environments like 3D terrains or open-world maps would introduce additional variables that could confound the comparison. We needed to isolate the effect of the seed source, and mazes offer the cleanest experimental setup for that."

*Why this works:* Shows deliberate experimental design, not arbitrary choice.

---

### Q4. What is the difference between PRNG and QRNG?

**Answer:** "PRNGs are deterministic algorithms -- given the same seed, they produce the exact same sequence. They approximate randomness but are fundamentally periodic and predictable. We used the Mersenne Twister, which has a period of 2^19937 minus 1. QRNGs derive randomness from quantum mechanical phenomena -- in our case, vacuum fluctuations measured by the Australian National University's quantum hardware. This randomness is fundamentally non-deterministic and theoretically unpredictable. The key distinction is that PRNG randomness is algorithmic while QRNG randomness is physical."

*Why this works:* Demonstrates deep understanding of both technologies without overcomplicating.

---

### Q5. Why did you choose to compare QRNG specifically against Mersenne Twister?

**Answer:** "Mersenne Twister is the default PRNG in Python's random module and is the most widely used PRNG in scientific computing and game development. It has proven 623-dimensional equidistribution and the longest period among commonly used PRNGs. By choosing the strongest available PRNG as our baseline, we ensured a fair comparison -- any advantage QRNG shows would be against the best conventional alternative, not a weak strawman."

*Why this works:* Shows you chose the strongest baseline deliberately, which strengthens methodology.

---

### Q6. What are your specific objectives?

**Answer:** "We had three specific objectives. First, to determine how PRNG and QRNG seeds influence the structural complexity and diversity of generated mazes using statistical testing. Second, to determine the extent to which QRNG-based sources impact DRL agent training in terms of success rate and rewards. Third, to evaluate the generalization performance of QRNG-trained versus PRNG-trained agents on unseen maze environments."

*Why this works:* Concise, matches the manuscript exactly. Don't ad-lib here.

---

## Section 2: Methodology

### Q7. Why did you choose recursive backtracking as your maze generation algorithm?

**Answer:** "We chose recursive backtracking for three reasons. First, it is highly seed-sensitive -- every branching decision during generation is directly driven by the random number sequence, making it the most favorable algorithm for detecting differences between seed sources. Second, it guarantees solvable perfect mazes, which is required for RL training -- every generated maze has exactly one path between any two cells. Third, it is the most commonly used maze generation algorithm in PCG research, making our results comparable to existing work."

*Why this works:* Addresses the most likely attack vector proactively. Three concrete reasons.

---

### Q8. But recursive backtracking produces perfect mazes with strong structural constraints. Doesn't that guarantee a null result?

**Answer:** "That's an important observation, and it's exactly what our study established empirically. Before our work, this was an assumption without evidence. The literature on QRNG in Monte Carlo simulations -- specifically Cirauqui et al., 2024 -- showed measurable differences between PRNG and QRNG outputs in other domains. Whether those differences would manifest in procedural generation was unknown. Our contribution is proving that the generation algorithm acts as a structural bottleneck that homogenizes seed entropy -- this finding provides clear direction for future research to test less constrained algorithms like Wilson's or Prim's."

*Why this works:* Acknowledges the point, cites literature to show it wasn't obvious, reframes finding as contribution.

---

### Q9. Why didn't you test multiple maze generation algorithms?

**Answer:** "Testing multiple algorithms would constitute a different study with a broader scope. Our research question was specifically about whether seed-level entropy substitution alone affects procedural generation outcomes. By holding the algorithm constant, we isolated the seed source as the sole independent variable. Adding algorithms would introduce confounding variables. Our recommendation section explicitly identifies testing Wilson's and Prim's algorithms as the logical next step."

*Why this works:* Defends scope without being defensive. Shows understanding of variable isolation.

---

### Q10. Explain your seed generation process. How did you ensure fairness?

**Answer:** "For PRNG, we used Python's built-in random module which implements the Mersenne Twister algorithm to generate 64-bit integer seeds. For QRNG, we fetched raw 16-bit unsigned integers from the ANU Quantum Random Number API, which measures quantum vacuum fluctuations. Since the API outputs 16-bit blocks, we applied a bitwise concatenation strategy -- combining four consecutive 16-bit blocks into one 64-bit integer -- to match the PRNG seed format. We then validated both seed sets using Shannon entropy analysis and autocorrelation testing to confirm they met equivalent randomness standards before using them."

*Why this works:* Shows technical depth on a critical methodological detail.

---

### Q11. You used QRNG seeds to initialize the Mersenne Twister. Doesn't that defeat the purpose?

**Answer:** "This is our most important acknowledged limitation and our top recommendation for future work. In our design, the QRNG seed initializes Python's random module, which then uses Mersenne Twister for all subsequent random decisions during maze generation. This means the quantum randomness affects only the starting state of a deterministic algorithm. We chose this approach because it represents the most practical integration point -- replacing the seed source is the simplest way to introduce QRNG into existing pipelines. Our finding that this is insufficient is itself a contribution: it tells future researchers that seed-level substitution alone is not enough, and they should instead use QRNG bits directly at each decision point via a custom Fisher-Yates shuffle."

*Why this works:* Acknowledges head-on, explains the reasoning, and shows you've already identified the solution.

---

### Q12. How did you validate that your seeds were actually random?

**Answer:** "We applied two validation tests. First, Shannon entropy analysis on both seed sets, analyzing 4,915,200 bits per dataset. Both PRNG and QRNG achieved a binary Shannon entropy of 1.000000, which is the theoretical maximum for perfect randomness. The bit distributions were 49.99% versus 50.01% for both sources. Second, autocorrelation testing from lag 0 to lag 100, where both datasets showed mean absolute autocorrelation values below 0.004, well within the 95% confidence interval of plus or minus 0.000884. Only 3-4% of lags showed significance, below the 5% expected by chance. Both sources passed identically."

*Why this works:* Specific numbers show mastery. "Both sources passed identically" sets up the bottleneck argument.

---

### Q13. Why did you use three different DRL algorithms instead of just one?

**Answer:** "We used three algorithms -- DQN, A2C, and PPO -- because they represent the three major families of deep reinforcement learning: value-based, hybrid actor-critic, and policy gradient respectively. Our goal was to benchmark the randomness source, not the model. If QRNG showed an advantage with only one algorithm, we couldn't distinguish whether it was a seed effect or a model-specific interaction. By testing across three families, we can make a stronger claim about whether the seed source matters regardless of the learning approach. The consistent result across all three strengthens our conclusion."

*Why this works:* Explains the experimental design logic clearly.

---

### Q14. Why these specific hyperparameters? How did you choose them?

**Answer:** "The common environmental parameters -- 10 million timesteps, discount factor of 0.99, observation normalization, MLP policy -- were held constant across all agents to ensure identical learning conditions. The algorithm-specific hyperparameters -- learning rates, batch sizes, network architectures -- were empirically determined to ensure each algorithm operated within its stability region. For example, A2C used a smaller network of MLP 64-64 because its on-policy nature requires less capacity to avoid overfitting, while DQN and PPO used MLP 256-256 for their respective off-policy and batch-based approaches. The key point is that hyperparameters were identical between the PRNG and QRNG groups for each algorithm."

*Why this works:* Shows you understand not just what the hyperparameters are, but why they were chosen.

---

### Q15. Why 10 million timesteps?

**Answer:** "10 million timesteps was determined to be sufficient for convergence in our low-dimensional sensor-based task. The observation space is only 10-dimensional -- 8 LiDAR readings plus a 2D target vector -- which is much simpler than pixel-based environments that might require hundreds of millions of timesteps. Our training curves confirm that all algorithms reached stable performance well before the 10 million timestep budget, with success rates plateauing by approximately episode 20,000 to 25,000 for A2C and PPO."

*Why this works:* Justifies with evidence from your actual results.

---

### Q16. Why only 3 trials per model group?

**Answer:** "Three trials were chosen due to computational constraints -- training was conducted on local hardware without a dedicated GPU cluster. Each trial of 10 million timesteps required significant computation time. Three trials per condition, with six conditions total -- three algorithms times two seed sources -- resulted in 18 complete training runs. While three trials were sufficient to observe convergence trends and calculate mean performance, we acknowledge in our recommendations that 10 or more trials would provide stronger statistical evidence for the convergence stability differences we observed."

*Why this works:* Honest about limitations while showing the total scope was still substantial (18 runs).

---

### Q17. Explain your reward function. Why this structure?

**Answer:** "The reward function was designed to balance goal-seeking with exploration. The primary reward is +250 for reaching the goal, which provides a strong terminal signal. We added shaped rewards to address the sparse reward problem: +0.5 times distance improvement for moving closer to the goal, +2.0 for exploring new cells with progress, and +0.3 for exploration without progress. Penalties include -0.005 per step to encourage efficiency, -0.75 for wall collisions to discourage invalid moves, and -7 for timeout at 500 steps. This structure ensures the agent receives informative feedback throughout the episode rather than only at termination."

*Why this works:* Explains the design reasoning behind each component.

---

### Q18. Why did you use LiDAR-based observations instead of visual grid input?

**Answer:** "We used a sensor-based observation space to simulate realistic robotic perception. In real-world autonomous navigation, agents typically rely on sensor data like LiDAR rather than a bird's-eye view of the entire environment. Our 10-dimensional observation vector -- 8 ray-cast distances at 45-degree intervals plus a 2D target direction -- creates a partially observable environment, which is more challenging and more representative of real navigation scenarios. This choice also keeps the observation space low-dimensional, making training more computationally feasible."

*Why this works:* Connects to real-world applications and shows deliberate design.

---

## Section 3: Results & Statistical Analysis

### Q19. What statistical tests did you use and why?

**Answer:** "We followed a multi-stage statistical analysis. First, Shapiro-Wilk tests for normality on a subsample of 5,000 from each group, since the full 71,800 sample size causes sensitivity issues. All metrics rejected normality with p-values below 10 to the negative 20, so we used non-parametric tests. For univariate comparisons, we applied Mann-Whitney U tests on all eight structural metrics. For multivariate analysis, we ran PERMANOVA with Euclidean distance on z-score normalized metrics with 1,000 permutations. The significance level was alpha equals 0.05 throughout."

*Why this works:* Shows methodological rigor and understanding of why each test was appropriate.

---

### Q20. Why did you subsample to 5,000 instead of using all 71,800?

**Answer:** "The Shapiro-Wilk test is sensitive to sample size. With very large samples, even trivially small deviations from normality become statistically significant, which can lead to rejecting normality when the distribution is practically normal. We subsampled to n equals 5,000 to maintain statistical sensitivity while avoiding this large-sample artifact. This is a recommended practice in the statistical literature, as noted by Souza et al., 2023."

*Why this works:* Shows understanding of statistical nuance, not just mechanical test application.

---

### Q21. Your Mann-Whitney U tests all showed p > 0.05. What does this mean?

**Answer:** "It means we fail to reject the null hypothesis for every individual structural metric. The medians for path length, tortuosity, dead-end count, junction proportions, straight corridors, turning corridors, and mean turns per corridor are statistically identical between PRNG and QRNG mazes. For example, both groups had a median path length of 84.00, median tortuosity of 2.47, and median dead-end count of 12.00. The p-values ranged from 0.0749 to 0.5395, all well above the 0.05 threshold. There is no statistically significant difference in any individual structural feature."

*Why this works:* Specific numbers demonstrate mastery. Saying "fail to reject" is scientifically precise.

---

### Q22. What is PERMANOVA and why did you use it?

**Answer:** "PERMANOVA is a Permutational Multivariate Analysis of Variance. While Mann-Whitney U tests compare one metric at a time, PERMANOVA tests whether the combined structural profile -- all metrics considered together -- differs between groups. This is important because individual metrics might not differ significantly, but their joint distribution could. We applied PERMANOVA with Euclidean distance on z-score normalized metrics with 1,000 permutations. The result was a pseudo-F statistic of 0.501 with p equals 0.7493, confirming no significant multivariate effect of the RNG type on combined maze structure."

*Why this works:* Explains both what PERMANOVA is and why a univariate-only analysis would be insufficient.

---

### Q23. What is the Expressive Range Analysis and what did it show?

**Answer:** "Expressive Range Analysis is a technique from game design research that visualizes the diversity of a generator's output in a 2D feature space. We plotted linearity -- the proportion of straight corridors -- against leniency -- the negative ratio of dead-ends to total nodes. Each maze is a point, and we drew convex hulls around each group's distribution. The PRNG hull area was 0.013127 and the QRNG hull area was 0.012500 -- nearly identical, with almost complete overlap. This visually confirms that both generators produce the same range and variety of maze structures."

*Why this works:* Demonstrates understanding of a less common analytical technique.

---

### Q24. If your seeds both passed entropy tests identically, shouldn't you have expected the same maze output?

**Answer:** "Not necessarily. Two seed sources can have identical aggregate entropy statistics but differ in their sequential patterns -- how randomness is distributed across the sequence of decisions during maze generation. In Monte Carlo simulations, Cirauqui et al., 2024 found measurable differences between PRNG and QRNG outputs despite similar aggregate statistics. Our study tested whether this phenomenon extends to procedural generation. The finding that it does not -- at least with recursive backtracking -- is empirically novel."

*Why this works:* Uses literature to show the outcome wasn't predetermined.

---

## Section 4: DRL Training & Performance

### Q25. Why did DQN perform so poorly compared to A2C and PPO?

**Answer:** "DQN's poor performance -- below 17% success rate -- is architecturally expected. DQN is a value-based method that treats each observation as a complete representation of the environment state. However, our LiDAR-based environment is a Partially Observable Markov Decision Process -- the agent can only see 8 directional distances and a target vector, not the full maze. DQN cannot integrate information across time steps, so it repeatedly makes the same decisions in similar-looking corridors. This is consistent with Hausknecht and Stone, 2017, who showed standard DQN handles partial observability significantly worse than recurrent alternatives. Importantly, DQN performed equally poorly under both seed conditions, reinforcing that the seed source is not the differentiating factor."

*Why this works:* Technical explanation with literature support, and ties back to the main finding.

---

### Q26. If DQN was clearly unsuitable, why include it?

**Answer:** "We included DQN because it represents the value-based family of deep reinforcement learning. Our goal was to benchmark the seed source across all three major DRL families -- value-based, actor-critic, and policy gradient. Excluding DQN would leave a gap in our comparison. DQN's failure is actually informative: it confirms that under partial observability, even a strong randomness source cannot compensate for an architectural mismatch. We recommend replacing DQN with DRQN -- its recurrent variant with LSTM memory -- in future work for a fairer value-based comparison."

*Why this works:* Turns a weakness into a methodological justification.

---

### Q27. You mentioned QRNG showed tighter convergence clustering in PPO. Can you elaborate?

**Answer:** "In the PPO training curves, the three QRNG trials showed strikingly consistent convergence -- all three runs rose steeply in early episodes and converged tightly together, stabilizing around 85 to 90% success rate with minimal divergence. In contrast, the three PRNG trials showed more variability, with one trial experiencing a severe performance collapse at approximately episode 21,000 where the success rate dropped from 70% to below 10% before partially recovering. While this observation is suggestive, we have only 3 trials per condition, which is insufficient to statistically validate this difference. We list this as a recommendation for future work with 10 or more trials."

*Why this works:* Reports the observation honestly without overclaiming, shows scientific restraint.

---

### Q28. What was the overall algorithm ranking?

**Answer:** "The ranking was PPO greater than A2C greater than DQN, and this held consistently for both PRNG and QRNG groups. PPO achieved the highest success rates -- 73% to 99% final success rate across trials. A2C achieved moderate success -- 74% to 93%. DQN performed poorly -- 21% to 43%. This ranking is consistent with the reinforcement learning literature for partially observable, sensor-based navigation tasks, where policy gradient methods with entropy regularization tend to outperform value-based approaches."

*Why this works:* Clean, specific, and connected to established literature.

---

### Q29. Did PRNG or QRNG produce better training results?

**Answer:** "Neither produced consistently better results. For A2C, PRNG had slightly higher peak success rates but wider inter-trial variance, while QRNG showed tighter clustering. For DQN, QRNG occasionally achieved marginally higher final success rates, but the differences were small and inconsistent. For PPO, PRNG occasionally reached higher peaks -- up to 99% versus QRNG's 92% -- but QRNG showed more stable convergence without the performance collapse seen in one PRNG trial. Overall, no seed source produced a systematic advantage across algorithms."

*Why this works:* Balanced, specific, and avoids cherry-picking.

---

## Section 5: Generalization & Evaluation

### Q30. Explain your generalization testing strategy.

**Answer:** "After training, we froze each model's weights and evaluated on 1,000 novel mazes per condition using unseen seeds. We tested two conditions: intra-domain generalization -- where an agent trained on PRNG mazes is tested on unseen PRNG mazes, and the same for QRNG -- and cross-domain generalization -- where a PRNG-trained agent is tested on QRNG mazes and vice versa. The Generalization Gap is defined as the intra-domain success rate minus the cross-domain success rate. A gap near zero means the agent generalizes well; a positive gap indicates overfitting to the training distribution."

*Why this works:* Clear, structured explanation of a key experimental design element.

---

### Q31. What were the generalization gaps?

**Answer:** "All generalization gaps were small. For A2C: PRNG gap was +0.90 percentage points, QRNG gap was -0.80 percentage points. For DQN: PRNG gap was -1.33, QRNG gap was +2.57. For PPO: PRNG gap was +1.74, QRNG gap was -1.57. The maximum gap was only 2.57 percentage points for DQN-QRNG, and the direction was inconsistent -- sometimes positive, sometimes negative -- indicating no systematic overfitting to either distribution."

*Why this works:* Numbers from memory demonstrate mastery.

---

### Q32. The QRNG-trained PPO showed a negative generalization gap. Doesn't that suggest QRNG is better?

**Answer:** "The -1.57 percentage point gap means the QRNG-trained PPO performed slightly better on PRNG mazes than on its own QRNG training distribution. While this could suggest marginally better cross-domain transfer, the difference is too small to draw significant conclusions -- it's within the range of experimental noise given only 3 trials. The PRNG-trained PPO had a gap of +1.74, so both are within plus or minus 2 percentage points of zero. We report this observation transparently but do not claim it as evidence of QRNG superiority."

*Why this works:* Shows scientific honesty and statistical awareness.

---

### Q33. How generalizable are your findings?

**Answer:** "Our findings are directly generalizable to 2D maze navigation using recursive backtracking on 20 by 20 grids with the three DRL architectures tested. We can confidently say that for this configuration, seed-level randomness substitution does not affect outcomes. However, we explicitly acknowledge that the findings may not extend to larger maze sizes where structural memorization becomes harder, different generation algorithms with fewer structural constraints, 3D or continuous environments, or other PCG domains like terrain generation. These are all listed as recommendations for future work."

*Why this works:* Precise about what you can and cannot claim. Panelists respect this.

---

## Section 6: Limitations & Future Work

### Q34. What are the main limitations of your study?

**Answer:** "Four main limitations. First, the QRNG seeds initialized the Mersenne Twister rather than being used directly at each random decision point, limiting the expression of quantum entropy. Second, the study used only one maze generation algorithm -- recursive backtracking -- which imposes strong structural constraints. Third, the study was limited to 20 by 20, 2D mazes. Fourth, only 3 training trials per condition, which limits the statistical power for detecting subtle differences in training stability. All four are addressed in our recommendations."

*Why this works:* Owning limitations proactively is stronger than having them pointed out.

---

### Q35. If you could redo the study, what would you change?

**Answer:** "Two things. First, I would use QRNG bits directly in maze generation by implementing a custom Fisher-Yates shuffle that consumes raw quantum bits at each step, bypassing the Mersenne Twister entirely. This would test whether quantum entropy makes a difference when it's not filtered through a deterministic algorithm. Second, I would test at least two or three generation algorithms -- recursive backtracking, Wilson's algorithm, and randomized Prim's -- to determine whether the bottleneck finding is algorithm-specific or universal."

*Why this works:* Shows you've thought critically about your own work.

---

### Q36. What is the practical contribution if all results are null?

**Answer:** "Three contributions. First, we established that the procedural generation algorithm -- not the entropy source -- is the primary determinant of structural diversity. This saves future researchers from investing in expensive QRNG integration expecting improvements that won't materialize at the seed level. Second, we provide a reproducible benchmarking framework -- the seed-level substitution experimental design, the statistical validation pipeline, and the evaluation protocol -- that future researchers can replicate with different algorithms or domains. Third, we identified that the effect of seed entropy may be more apparent at the training stability level rather than the structural level, which is a new research direction."

*Why this works:* Three concrete contributions, none of which depend on positive results.

---

### Q37. Why should future researchers care about this study?

**Answer:** "Because we answered a question that was assumed but never tested. The assumption in PCG research is that the seed source doesn't matter as long as it passes basic randomness tests. We provide the first empirical confirmation of this assumption for recursive backtracking mazes -- and more importantly, we identified exactly where the bottleneck lies. Future researchers now know: if you want to benefit from better entropy sources, you need to change the generation algorithm, not just the seed. That's actionable guidance that didn't exist before our study."

*Why this works:* Reframes null result as foundational knowledge.

---

## Section 7: Conceptual & Theoretical

### Q38. What is the theoretical basis for expecting QRNG to produce different mazes?

**Answer:** "The theoretical basis comes from information theory. QRNG sequences are fundamentally non-deterministic -- they derive from quantum phenomena that are provably unpredictable, not just computationally hard to predict. In contrast, PRNG sequences are periodic and deterministic. The hypothesis was that this difference in entropy quality might propagate through the maze generation algorithm, producing a wider distribution of structural outcomes. Our study showed that with recursive backtracking, the algorithm's structural constraints absorb this entropy difference, producing statistically equivalent outputs."

*Why this works:* Demonstrates theoretical understanding while explaining why the theory didn't translate to practice.

---

### Q39. What is the Mersenne Twister's period, and why does it matter?

**Answer:** "The Mersenne Twister has a period of 2 to the power of 19937 minus 1 -- an astronomically large number. This means it would take an impractically long time before the sequence repeats. For our 71,800 seeds, we're sampling an infinitesimal fraction of this period, which means the PRNG behaves indistinguishably from a true random source at our scale. This is actually why the null result makes sense -- the Mersenne Twister is already 'random enough' for the number of seeds we tested. The distinction between PRNG and QRNG might only become meaningful at scales approaching the PRNG's period or in applications sensitive to sequential correlations."

*Why this works:* Shows deep understanding and pre-empts "your PRNG was too good" argument.

---

### Q40. What is a Partially Observable Markov Decision Process, and why is your environment one?

**Answer:** "A POMDP is a decision process where the agent cannot observe the full state of the environment. In a fully observable maze, the agent would see the entire grid. In our setup, the agent only receives 8 LiDAR distance readings and a 2D direction to the goal -- it cannot see around corners, cannot see the maze layout, and cannot distinguish between structurally different corridors that look identical from its local perspective. This partial observability is why DQN struggles -- it treats each observation as a complete state -- while A2C and PPO handle it better because their policy-based approaches can learn stochastic policies that explore when uncertain."

*Why this works:* Clear explanation connecting theory to your specific results.

---

### Q41. What is zero-shot generalization in the context of your study?

**Answer:** "Zero-shot generalization means the agent performs well on environments it has never seen during training, without any additional fine-tuning or adaptation. In our study, we evaluate this by testing trained agents on 1,000 completely novel mazes generated from unseen seeds. The agent must navigate these new mazes using only the navigation strategy it learned during training. The generalization gap quantifies how well this transfer works -- a gap near zero indicates strong zero-shot generalization."

*Why this works:* Connects the concept directly to your evaluation methodology.

---

## Section 8: Curveball / Stress-Test Questions

### Q42. Your study found nothing significant. How is this a contribution to Computer Science?

**Answer:** "Science advances by testing hypotheses, not by confirming them. The null result is the contribution. Before our study, no one knew whether QRNG seeds would improve procedural generation -- it was an open question. Now we know: with recursive backtracking, they don't. More importantly, we identified why -- the generation algorithm is the bottleneck. This is actionable knowledge. It's comparable to Edison's famous statement about finding 10,000 ways that don't work. We saved future researchers from pursuing seed-level QRNG integration with constrained algorithms, and redirected them toward the actual leverage point: the generation algorithm itself."

*Why this works:* Confident, quotable framing. Don't get defensive.

---

### Q43. Isn't this just an expensive way to confirm that Mersenne Twister is good enough?

**Answer:** "No -- that conclusion alone would not require this study. What we established is something stronger: that the maze generation algorithm homogenizes entropy from any source, regardless of quality. Even if we had used a weaker PRNG with known biases, recursive backtracking would likely produce similar structural distributions because its construction rules impose dominant patterns. This is a finding about the algorithm's information bottleneck, not about Mersenne Twister being sufficient."

*Why this works:* Elevates the finding from "PRNG is fine" to "the algorithm is the bottleneck."

---

### Q44. If you had unlimited time and resources, could you have found a significant result?

**Answer:** "Possibly, but through different experimental designs. With unlimited resources, I would first bypass the Mersenne Twister intermediary and use QRNG bits directly. Second, I would test with less constrained generation algorithms. Third, I would scale to much larger mazes -- 50 by 50 or 100 by 100 -- where structural diversity has more room to express itself. And fourth, I would run 30 or more trials per condition to detect subtle training stability effects. Our study established the baseline that seed-level substitution alone is insufficient -- these extensions would test whether direct quantum entropy integration makes a difference."

*Why this works:* Shows you understand the design space beyond your study.

---

### Q45. Why didn't you use a real quantum computer instead of an API?

**Answer:** "The ANU Quantum Random Number API measures quantum vacuum fluctuations using real quantum hardware -- a homodyne detector measuring the electromagnetic field of the vacuum state. It's not a simulation. The API provides a convenient interface to genuine quantum-derived randomness without requiring us to operate quantum hardware directly. This is the standard approach in QRNG research -- Cirauqui et al. and other studies in our literature review also used API-based quantum random number services. Building or operating our own quantum hardware would be outside the scope of a computer science thesis."

*Why this works:* Corrects a potential misconception and shows knowledge of the QRNG source.

---

### Q46. Your thesis title mentions "enhancing robustness." Didn't you fail to enhance anything?

**Answer:** "The title reflects the research objective, not the result. The study aimed to evaluate whether quantum-seeded procedural generation enhances robustness. The answer we found is: not under these experimental conditions. This is a valid and important scientific outcome. The title accurately describes what we investigated. The contribution is the evaluation itself and the discovery of the algorithm bottleneck."

*Why this works:* Direct, unapologetic. The title describes the investigation, which is standard academic practice.

---

### Q47. How do you know your QRNG seeds were genuinely quantum and not just noise?

**Answer:** "The ANU Quantum Random Number Server has been peer-reviewed and validated. It measures quantum vacuum fluctuations -- the inherent uncertainty in the electromagnetic field even in a perfect vacuum -- using a homodyne detector. This is a well-established quantum phenomenon. Additionally, all raw API responses, including 16-bit chunks, timestamps, and metadata, were logged in our raw_qrng_logs.json file for auditability. Our own Shannon entropy and autocorrelation tests confirmed the output met the expected properties of true random sequences."

*Why this works:* Shows auditability and knowledge of the quantum source.

---

### Q48. What happens if a future study with a different algorithm finds QRNG does make a difference?

**Answer:** "That would be entirely consistent with our findings. Our conclusion is not that QRNG is useless for procedural generation -- it's that QRNG's advantage is absorbed by the structural constraints of recursive backtracking. A less constrained algorithm might allow the entropy difference to express itself in the output. Such a finding would actually validate our bottleneck hypothesis by confirming that the algorithm -- not the entropy source -- is the critical variable."

*Why this works:* Shows your findings are compatible with any future outcome, which is the sign of a robust study.

---

### Q49. Is the result statistically valid with only 71,800 seeds? Is that enough?

**Answer:** "71,800 seeds per group is a large sample size for this type of study. Our statistical tests -- Mann-Whitney U and PERMANOVA -- are well-powered at this sample size. The p-values were not borderline; they ranged from 0.07 to 0.54 for Mann-Whitney U and 0.75 for PERMANOVA, all well above the 0.05 threshold. If there were a meaningful difference, 71,800 samples would be more than sufficient to detect it. The constraint was not statistical power but the ANU API rate limit of 100 calls with 1,024 numbers each per account, which determined our maximum seed count."

*Why this works:* Specific numbers and explanation of the constraint source.

---

### Q50. What is your single most important finding?

**Answer:** "The procedural generation algorithm -- not the source of randomness -- is the critical bottleneck for structural diversity in maze-based training environments. This finding reframes the problem for future researchers: instead of seeking better entropy sources, they should focus on designing generation algorithms that can express a wider range of structural outcomes."

*Why this works:* This should be your last answer if asked to summarize. Clean, confident, memorable.

---

## Quick Reference: Key Numbers to Memorize

| Metric | Value |
|--------|-------|
| Seeds per group | 71,800 |
| Total mazes | 143,600 |
| Maze size | 20 x 20 |
| Training timesteps | 10,000,000 |
| Trials per condition | 3 |
| Total training runs | 18 |
| Shannon entropy (both) | 1.000000 |
| PERMANOVA p-value | 0.7493 |
| Mann-Whitney U range | all p > 0.05 |
| Max generalization gap | 2.57 pp (DQN-QRNG) |
| PPO final SR range | 73%-99% (PRNG), 89%-92% (QRNG) |
| A2C final SR range | 74%-93% (PRNG), 80%-86% (QRNG) |
| DQN final SR range | 21%-35% (PRNG), 26%-43% (QRNG) |
| ERA hull PRNG | 0.013127 |
| ERA hull QRNG | 0.012500 |
| Algorithm ranking | PPO > A2C > DQN (both groups) |

---

## Rules of Engagement During Q&A

1. **Never start an answer with "I think" or "I believe."** Start with facts: "The data shows...", "Our results indicate...", "The study established..."
2. **If you don't know the answer, say so.** "That's outside the scope of our study, but based on the literature..." is better than guessing.
3. **Never contradict your own thesis.** If a panelist leads you toward contradicting your methodology, pause and redirect: "I understand the concern, but our approach was designed to..."
4. **Keep answers under 60 seconds.** If the panelist wants more, they'll ask a follow-up.
5. **All members must be able to answer all questions.** Even if you didn't present that section.
6. **When a panelist is right about a limitation, agree and redirect.** "Yes, that's a valid limitation, and it's exactly why we recommend [X] in our future work section."
7. **Practice the phrase "fail to reject the null hypothesis" until it sounds natural.** This is the scientifically correct language.
