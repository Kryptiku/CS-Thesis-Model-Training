**Enhancing Autonomous Navigation Robustness in**   
**Unstructured Environments using**   
**Quantum-Seeded Procedural Maze Generation**

A Thesis Manuscript presented to the Faculty of   
College of Informatics and Computing Sciences    
BATANGAS STATE UNIVERSITY   
The National Engineering University  
Batangas City 

# TITLE PAGE

In Partial Fulfillment   
of the Requirements for the Degree   
Bachelor of Science in Computer Science

Antony, Aldrich Ryan V.  
Baricante, Mark Angelo R.  
Mirabel, Kevin Hans Aurick S.

John Richard M. Esguerra, MSCS  
Supervisor

April 2026

# **CHAPTER 1**

**INTRODUCTION**

## **1.1 Background of the Study**

Procedural generation (PG) is a method for creating content using algorithms which define the rules of what is being generated. The application of PG can relate to many fields, such as game development, as a means to automate level design and reduce development costs and effort (Zhang et al., 2022). Another application is in the entertainment and simulation domains, where procedural content generation techniques are increasingly used not only for creating diverse virtual environments but also as a means of increasing generality in machine learning by generating varied training environments that improve agent generalization (Risi & Togelius, 2020). Lastly is to leverage procedural generation in order to benchmark reinforcement learning, not only for benchmarking but also as a means for training artificial intelligence models, since for most cases, the procurement of training data could prove to be costly and time-consuming (Cobbe et al., 2020; Schmedemann et al., 2022). By generating diverse and functional environments, PCG helps ML systems learn robust, transferable policies rather than brittle and overfitted ones. A good example is for car training data. As the trend for self-driving cars has been on the rise, there is a need for training data in order for the car to make decisions without human intervention. However, other than hardware limitations and algorithmic constraints, autonomous vehicles face a number of technical and non-technical challenges in terms of real-time implementation, safety, and reliability (Kaur & Rampersad, 2023), which is why efforts have been made to use PG in simulating road networks. All of these highlight the versatility of procedural generation as a tool in different fields like game development, generating terrain in creative fields, and creating diverse simulations.

The key to diversity in PG is randomness. Traditionally, randomness in applications such as video games, simulations, cryptographic protocols, randomized algorithms, and Monte Carlo techniques relies on pseudo-random number generators (PRNGs), which produce deterministic sequences that imitate true randomness and are not only fast but also efficient for computational use (Bhattacharjee & Das, 2022; Fort, 2015). PRNGs are limited to their deterministic nature, not reaching true unpredictability, potentially reducing diversity in generated content, which may contribute to overfitting, a possibility that this study seeks to evaluate, where the agent memorizes the specific layout or the underlying algorithmic patterns of the training environment rather than learning generalizable navigation strategies (Zhang et al., 2018), and to add the security risk it brings up for cryptographic-related contexts, as it is possible to replicate outputs once the seed is known.

More recently, Quantum Random Number Generators (QRNGs) have emerged, taking advantage of the principles of quantum mechanics, based on fundamentally unpredictable phenomena like superposition and measurement collapse, to generate randomness that is theoretically impossible to predict or replicate (Bhattacharjee & Das, 2022; Jozwiak et al., 2024), showing QRNG’s reliability in cryptographic fields. This study hypothesizes that QRNG may provide a more structurally diverse source of randomness

However, despite the potential that QRNGs offer, research on their use has been limited to cryptography and security. Its potential in PG, which primarily relies on randomness to create unpredictable outcomes, has been ignored. PG continues to rely on PRNG as its default source of randomness in order to create or generate outputs such as maps, terrains, simulations, and mazes. While PRNGs today dominate in domains such as cryptography, simulations, and games, the application of QRNG remains unexplored outside security contexts. 

### ***Statement of the Problem***

Deep Reinforcement Learning (DRL) agents frequently suffer from overfitting, where they memorize training environments rather than learning generalized navigation logic. This causes agents to fail when encountering novel layouts in unstructured environments. While existing solutions primarily address this through visual domain randomization (changing textures, colors, or lighting), there is a significant lack of research regarding structural randomization.

Standard Procedural Content Generation (PCG) relies on Pseudo-Random Number Generators (PRNGs), which are inherently deterministic and prone to periodicity. It remains distinctively unclear whether this lack of true entropy restricts the Zero-Shot Generalization capabilities of DRL agents. Consequently, there is a need to determine if introducing true stochasticity via Quantum Random Number Generators (QRNGs) can mitigate structural overfitting and improve navigational robustness.

The study seeks to answer the following questions:

1. How do training environments generated via PRNG differ from QRNG in terms of structural complexity metrics and diversity, as quantified through topological, statistical, and distributional approaches?  
2. How do different sources of randomness in the training environment affect the learning rate of various DRL agents?  
3. How does the DRL agent trained on QRNG-seeded environments perform when navigating unseen maze structures compared to the baseline PRNG model?

## **1.2 Objectives of the Study**

The study aims to address the gap by conducting an exploratory benchmark of QRNG against PRNG in maze generations using the recursive backtracking algorithm. By comparing the structural diversity and unpredictability of the generated mazes, the study explores whether QRNGs provide any substantial and measurable benefits in procedural generation for training DRL agents. Significant differences would indicate a potential for QRNGs' use in procedural generative content, while minimal differences would suggest their advantages in this domain are limited, though other applications or contexts may still benefit from quantum randomness.

### ***General Objective***

To evaluate the impact of quantum random number generator (QRNG) seeds compared to pseudo-random number generator (PRNG) seeds when applied to procedural generation in training  and evaluating DRL agents to navigate through the maze.

### ***Specific Objectives***

1. To determine how different sources of randomness (PRNGs and QRNGs) influence the structural complexity and diversity of the maze training environments.  
2. To determine the extent to which QRNG-based sources impact the training of autonomous navigation models in terms of success rate and rewards over episodes.  
3. To evaluate the performance of DRL agents trained in QRNG‑seeded versus PRNG‑seeded mazes on unseen environments, in terms of success rate, reward, efficiency, and generalization.

## **1.3 Novelty Claims**

This study presents a novel study on the use of Quantum Random Number Generators (QRNGs) as a source of randomness for Procedural Content Generation (PCG), outside of their usual application in cryptography. Existing research is seen to rely on pseudo-random number generators (PRNGs) and focuses primarily on visual domain randomization in training environments in an attempt to improve generalization in Deep Reinforcement Learning (DRL) agents. This study introduces a controlled seed-level substitution experimental setup, where QRNG-generated entropy replaces PRNG seeds while keeping the maze generation algorithm and training pipeline as a constant. The study further contributes by quantitatively analyzing structural diversity using topological and statistical maze metrics and by evaluating the effects of quantum-seeded environments across multiple DRL architectures (DQN, A2C, and PPO) as a means of benchmarking the randomness itself and its effect, rather than model superiority. With this approach, the research reframes quantum randomness as a potential tool for enhancing structural diversity and generalization in reinforcement learning environments.

## **1.4 Scope and Limitations**

The study focuses on evaluating the impact of Quantum Random Number Generator (QRNG) seeds compared to Pseudo-Random Number Generator (PRNG) seeds when applied to procedural generation for enhancing the robustness of Deep Reinforcement Learning (DRL) agents in autonomous navigation.

The randomness sources for the experimental group involve using the Australian National University’s (ANU) Entropy-as-a-Service (EaaS) to procure true quantum seeds. For the control group, the study will use PRNG seeds generated from Python’s built-in deterministic random module. These seeds will drive a recursive backtracking algorithm to generate 2D maze environments. All implementations will be conducted in Python.

To benchmark the effect of these randomness sources on navigational robustness, the study utilizes three distinct DRL architectures: Deep Q-Network (DQN), Advantage Actor-Critic (A2C), and Proximal Policy Optimization (PPO). It is important to note that these models possess different hyperparameters and learning approaches (e.g., value-based vs. policy-gradient). Consequently, this research does not aim to compare the performance of the models against each other (e.g., determining if PPO is better than DQN). Instead, these models serve as benchmarking tools to evaluate the source of randomness itself. The primary objective is to determine if training on QRNG-seeded environments yields consistently more robust agents compared to their PRNG-trained counterparts, regardless of the specific model architecture used. Furthermore, this study explicitly establishes the Pseudo-Random Number Generator (PRNG) utilizing the Mersenne Twister algorithm as the performance baseline. Improvement, in this context is not measured by the agents achieving an arbitrary high score, but is strictly defined by the comparative difference in navigation success rates and generalization capabilities between the QRNG-trained agents (experimental group) and the PRNG-trained agents (control group) when exposed to identical, unseen testing environments.

The study is delimited to 2D maze structures; 3D environments or other complex terrains are not within the scope. Furthermore, subjective factors such as maze playability, user preference, and game-level design are excluded. The evaluation focuses strictly on structural statistical properties and the quantitative performance metrics of the DRL agents. Finally, the study analyzes only seed-level randomness and does not cover long-form RNG sequences or time-series randomness behavior.

## **1.5 Significance of the Study**

The findings of this study may offer valuable insights for several groups. For game developers who could utilize QRNG in order to create more unpredictable and unique maze structures, improving the replayability and quality of the games being developed, especially for infinitely generating worlds, as then the true limit would be the amount of assets for the game to use. Simulation engineers may benefit from the simulation appearing to be more realistic and randomly generated. It can also reduce the structural bias, which will improve the reliability of simulation outputs. This also relates to AI training and benchmarking as a means for creating even more unpredictable scenarios for models to try and overcome in order to improve the quality of the models. Computer science students, as this study may help or inspire students to expand their knowledge on how quantum randomness can affect the quality of the algorithmic output and evaluating QRNG beyond conventional methodologies. Future researchers may use the results of this study to serve as benchmark data on the differences of seed generation randomness between PRNG and QRNG in terms of procedural maze generation. Lastly, to the field of cryptography, as the insights may prove to be useful to improve the implementation of cryptographic systems. This research aligns with SDG 9: (Industry, Innovation, and Infrastructure), as it investigates the possible application of quantum-based randomness to enhance procedural generation and strengthen the reliability of autonomous systems. The research might help in building robust digital infrastructure and advanced AI technologies for simulations and robotics by improving the generalization and consistency of DRL agents through training in various environments.

## **1.6 Definition of Terms**

1. **Procedural Generation.** a technique used in computing to create data algorithmically rather than manually, creating a variety of maze environments for reinforcement learning agent training.  
2. **Pseudo-Random Number Generators.** Deterministic algorithms that produce sequences resembling randomness, used as the baseline source of seeds for maze generation.  
3. **Quantum Random Number Generators.**  Devices that take advantage of quantum phenomena to produce true randomness, applied in the study to generate seeds for maze environments.  
4. **Recursive Backtracking.** A maze generation algorithm that explores and backtracks through cells, chosen in the study for its simplicity, seed sensitivity, and ability to produce solvable perfect mazes.  
5. **Seed.** An initial value that determines the sequence of random numbers, directly influencing the structure of mazes generated in the experiments.  
6. **Environment.** The maze in which an agent operates, generated procedurally using PRNG or QRNG seeds.  
7. **Unstructured Environments.** Environments lacking predictable geometric patterns, serving as the test scenarios where agents must navigate without relying on regular structures.  
8. **Reinforcement Learning.** A machine learning paradigm where agents learn by interacting with environments and receiving rewards, forming the basis of the study’s training approach.  
9. **LiDAR.** A sensor technology that measures distances using laser light in robotics, referenced and simulated in the study as part of the data that the agent receives.  
10. **Generalization.** The ability of agents to apply learned navigation strategies to unseen environments, serving as a key performance metric in the experiments.

# **CHAPTER 3**

**RESEARCH METHODOLOGY**

## 

## **3.1 Research Design**

The study uses a comparative experimental research design to determine how much PRNGs and QRNGs influence the structural outcomes of procedural maze generation and its effect on the performance and generalization of different RL agents. The study uses the seed sources, PRNG and QRNG, as the independent and primary variable by using an identical maze generation algorithm, which is recursive backtracking. Using controlled tests, the study will evaluate the seeds’ statistical randomness along with the generated mazes’ complexity and variability. To extend this analysis toward navigation performance, reinforcement learning agents, namely Deep Q-Network (DQN), Proximal Policy Optimization (PPO), and Advantage Actor-Critic (A2C), are trained within the generated mazes to evaluate how the randomness source of the environment affects learning dynamics, policy effectiveness, and generalization. The combination of RL training and evaluation guarantees that the research assesses the variability and diversity of procedural structures while also methodically investigating their effects on the capacity of autonomous agents to adapt and generalize

## **3.2 Model Formulation**

### ***Theoretical Framework***

The theoretical foundation of this study rests on two intersecting domains, which is procedural content generation through seeded randomness, and deep reinforcement learning for autonomous navigation. The core hypothesis is that the entropy quality of the seed source, whether pseudo-random or quantum-random, has an effect on the structural complexity and diversity of generated mazes, which in turn shapes the learning dynamics and generalization capability of trained RL agents.

### ***Mathematical Model and Algorithm Design***

This study will use the recursive backtracking algorithm as the main instrument for producing the maze dataset. For the seed generation, PRNG will use Python’s random module to generate the PRNG seeds, while the QRNG seeds will be from ANU-QRNG. Both seed groups will be stored in CSV format separately. Once the seeds are ready, each seed will be fed into the recursive backtracking algorithm to generate one 20×20 maze. The output mazes will be directly converted to the needed metrics via a script in Python and saved in CSV format.

To ensure the fairness of the randomness comparison, the study will standardize the bit-width of the seeds used for both groups to 64-bit integers. PRNG, which is the control group, will use Python’s built-in random module that utilizes the Mersenne-Twister algorithm. This algorithm is chosen because of its proven 623-dimensional equidistribution and a period of 219937\-1, which eliminates the possibility of cycle repetition. The system will generate standard 64-bit integer seeds, which serve as the controlled pseudo-random baseline.

Moreover, the QRNG, which is the experimental group, will use the Australian National University’s Quantum API. This AQN API measures the vacuum fluctuations to generate true random numbers. Since the API outputs data in uint16 (16-bit) blocks, the study will use a bitwise concatenation strategy to match the 64-bit integer seeds of PRNG. This ensures QRNG seeds will have the same value range and bit density as the PRNG seeds.

Before utilizing the collected seeds for the recursive backtracking algorithm, the researchers will perform statistical diagnostics to ensure the quality of randomness for both PRNG and QRNG seeds. This validation is an important step to ensure that the bitwise concatenation strategy did not introduce artificial correlations and met the necessary unpredictability standards. Two tests are applied:

1. **Shannon Entropy.** This metric will measure the density and unpredictability of the generated seeds. Ideally, a truly random sequence of *n* outcomes should have an entropy close to log2(*n*). The researchers will calculate the Shannon entropy of both PRNG and QRNG seeds. High entropy values will indicate that the seeds contain enough randomness and are free from bias that could affect the maze structure.  
2. **Autocorrelation.** This ensures the independence between trials. It measures the correlation between a seed (*St* ) and its delayed version (*St \+k*). High autocorrelation indicates the previous seed could predict the next seed, which would invalidate the independence of the generated mazes. It also confirms the concatenated QRNG seeds will have statistical independence just like the PRNG baseline.

### ***Deep Reinforcement Learning Implementation***

This experiment tests whether quantum-seeded randomness improves how well navigation agents hold up outside their training data. To do that, the training pipeline compares three well-established Deep Reinforcement Learning approaches: Deep Q-Network (DQN), Advantage Actor-Critic (A2C), and Proximal Policy Optimization (PPO). Together, they cover value-based learning (DQN), policy optimization (PPO), and a hybrid actor–critic setup (A2C).

**Environment Configuration.** The maze environments will be wrapped as a custom Gymnasium interface. Unlike visual grid-based inputs, this study utilizes a sensor-based observation space to simulate realistic robotic perception.

* **Observation Space (10-Dimensional Vector):** The agent receives a normalized vector of 10 floating-point values:  
  * **LiDAR Readings (8 values):** Eight ray-casts distributed radially (0°, 45°, 90°, …) to detect distance to the nearest wall.  
  * **Target Vector (2 values)**: The relative *(x, y)* direction or polar coordinates pointing toward the goal.  
* **Action Space:** A discrete space of four actions: *A \= {Up, Down, Left, Right}.*   
* **Termination Conditions:** An episode terminates if the agent reaches the goal or exceeds a maximum of 500 steps.  
* **Reward Function:** A sparse reward structure is implemented to minimize reward hacking and prioritize shortest-path seeking:  
  * *Rgoal*  \= \+200.0 (Task Completion)  
  * *Rstep*  \= \-0.01 (Base Step Penalty)  
  * *Rcollision*  \= \-1.0 (Wall Collision Penalty)  
  * R*exploration* \= \+0.1 (Exploration Bonus)  
  * R*productive* \= \+2.0 (Productive Exploration Bonus)  
  * R*timeout*  \= \-10.0 (Timeout Penalty) 	

**Model Architecture.** Since the input is a 1-dimensional feature vector rather than a 2D image, the agents will utilize a Multi-Layer Perceptron (MLP) policy (MlpPolicy) rather than a CNN.

* **Input Layer:** The network accepts a 10-float observation vector, representing the 8-ray LiDAR readings and the 2-dimensional relative target coordinates.  
* **Output Layer:** Maps the processed features to the 4 discrete actions.

### ***Variables and Assumptions***

The independent variable is the seed source type (PRNG or QRNG). The dependent variables include maze structural metrics (path length, tortuosity, dead-end count, junction proportions) and RL agent performance metrics (success rate, cumulative reward, steps taken, generalization gap). The study assumes that the recursive backtracking algorithm is held constant across both groups, and that all other training conditions are identical, isolating seed entropy as the sole differentiating factor.

## **3.3 Simulation Environment**

	Simulations will be conducted on local hardware and Google Colab for simultaneous training, with model checkpoints saved every 10,000 steps to monitor the learning curve. The maze generation pipeline and all statistical analyses will be implemented in Python. The maze environments will be wrapped as a custom Gymnasium interface for the RL training phase. The following libraries and frameworks are used: Python's built-in random module (Mersenne-Twister PRNG), the ANU Quantum Random Number API (QRNG), scipy.stats for statistical testing, and Stable-Baselines3 for DQN, A2C, and PPO implementations.

Since the outputs of QRNG are non-deterministic, all the generated values will be logged and reused as fixed inputs to ensure reproducibility and fairness in comparison with PRNG.

## **3.4 Technical Constraints**

The following constraints were identified as affecting the scope and configuration of this study.

**Table \_.** *Technical Constraints of the Study*

| Constraint Area | Description | Impact on the Study |
| ----- | ----- | ----- |
| QRNG API Access | ANU Quantum API has a request limit of 100 calls, with up to 1,024 numbers per call | Limited the total number of QRNG seeds collectable for the study. The study managed to gather 287,200 raw 16-bit seeds, summing up to 71,800 64-bit concatenated seeds |
| Hardware | Experiments conducted on local hardware with no dedicated GPU cluster | Limited model complexity and may result in longer training times |
| Non-Determinism of QRNG | QRNG outputs are inherently non-reproducible on re-query | All raw API responses and raw 16-bit chunks are stored in a raw\_qrng\_logs.json and raw\_qrng\_seeds.csv file consecutively to preserve auditability |
| Seed Bit-Width Matching | QRNG outputs in uint16 (16-bit) blocks, while PRNG uses 64-bit integers | Bitwise concatenation strategy was applied, statistical validation (Shannon entropy, autocorrelation) was required to verify no artificial correlations were introduced |

The constraints that were identified played a role in determining the scope of experimentation and model configuration. In QRNG, unlike PRNG where seeds can be generated using only a formula, it is mandatory that a quantum computer is used to generate non-deterministic randomness. In this regard, external API connectivity was used from a trusted quantum provider such as the ANU Quantum Random Number Server. This ensures that the QRNG seeds will still have the non-deterministic randomness since it is generating seeds from a real quantum number generator.

## **3.5 Experimental Setup**

### ***Data Collection***

This study will collect quantitative data from two randomness sources, a Pseudo-random Number Generator (PRNG) and a Quantum Random Number Generator (QRNG). Each seed will produce one 20×20 maze so that the structural differences between the two random number generators can be compared. The API has a request limit of 100 calls, with up to 1,024 numbers, which enabled the study to gather 71,800 concatenated QRNG numbers. In terms of reproducibility, all the raw API responses (raw 16-bit chunks, timestamps, and metadata) will be stored in a raw\_qrng\_logs.json file. The final output for both groups will be saved in separate CSV files (prng\_seeds.csv and qrng\_seeds.csv). The separation will keep the exact quantum data retrieval instance preserved for auditability and maintainability of the input dataset. The collected dataset will be the basis for comparing the randomness between PRNG and QRNG on procedural maze generation and will serve as the evidence for evaluating the differences in maze structure and unpredictability or extent of the entropy.

### ***Comparative Training Protocol***

The study utilizes a Two-Group Comparative Design. For each algorithm (DQN, A2C, PPO), two distinct instances are initialized, resulting in six total trained agents.

1. **Control Group *(AgentPRNG)*.** Trained exclusively on the PRNG Training Set at 10 Million timesteps. This establishes the baseline performance for standard procedural generation.  
2. **Experimental Group *(AgentQRNG)*.**  Trained exclusively on the QRNG Training Set at 10 Million timesteps. This tests the hypothesis that higher entropy in quantum seeds produces more diverse training scenarios, reducing overfitting.

In this comparative protocol, the PRNG-trained models serve as the stationary baseline against which quantum advantage is measured. Consequently, the study focuses on the *delta* or relative performance gap between the two groups. Improvement is quantitatively assessed by determining if the ***AgentQRNG*** yields statistically higher mean rewards and success rates than the ***AgentPRNG*** baseline across the validation sets, isolating the quality of the seed entropy as the sole differentiating factor.

### ***Training Hyperparameters***

To ensure the validity of the comparison, Common Environmental Parameters (Table 2\) will be held constant across all agents to ensure they face identical learning conditions. However, Algorithm-Specific Hyperparameters (Table 3\) are empirically determined. This approach ensures that each algorithm operates within its intended stability region.

**Table \_.** *Common Environmental Parameters (applied to all agents)*

| Parameter | Value | Justification |
| :---- | :---- | :---- |
| Total Timesteps | 1 x 106  | Sufficient for convergence in low-dimensional sensor tasks. |
| Discount Factor (ˠ) | 0.99 | Prioritizes long-term goal reaching over short-term survival. |
| Observation Normalization | True | LiDAR readings normalized to \[0, 1\] range to prevent gradient instability. |
| Policy | MlpPolicy | Enables feature extraction from vector-based observations using a multilayer perceptron. |
| Action Space | Discrete(4) | Standard movement {Up, Down, Left, Right}. |

**Table \_.** *Algorithm-Specific Configurations*

| Parameter | DQN | A2C | PPO |
| :---- | :---- | :---- | :---- |
| Learning Rate | 1 x 10\-3 | 7 x 10\-4 | 3 x 10\-4 |
| Batch Size | 512 | N/A (Rollout-based) | 512 |
| Buffer Size | 500,000 | N/A | N/A |
| n\_steps (Rollout) | N/A | 5 | 2048 |
| Exploration / Entropy | ε-greedy (1.0 to 0.05) | Entropy Coeff: 0.0 | Entropy Coeff: 0.01 |
| Network Architecture | MLP (256, 256\) | MLP (64, 64\) | MLP (256, 256\) |

### ***Generalization Testing Strategy***

Post training, the weights of all agents are frozen to prevent further learning. The Generalization Gap is then measured by evaluating the agents on the Test Sets (100 mazes per testing strategy).

1. **Intra-Domain Generalization.** *AgentPRNG* is tested on unseen PRNG mazes and *AgentQRNG* is tested on unseen QRNG mazes to measure standard robustness.  
2. **Cross-Domain Generalization:** *AgentQRNG* is tested on unseen PRNG mazes to determine if quantum-trained agents are more robust when facing standard structures, and *AgentPRNG* are tested on unseen QRNG mazes.

## **3.6 Evaluation Metrics**

This section outlines how the QRNG and PRNG seeds and generated mazes will be evaluated.

### ***Maze Structural Evaluation***

Each generated maze is converted to two graph representations: a cell graph where each path cell is a node and orthogonal adjacency (N, E, W, S) defines edges, and corridor graph where maximal degree‑2 chains are collapsed into single corridor edges, while junctions and dead ends become nodes. This transformation reduces pixel noise and yields corridor‑level features, providing a higher-level abstraction of maze topology.

* **Path length.** The shortest path length from the designated start-to-finish using Dijkstra. The mean, median, IQR, and distribution of both PRNG and QRNG groups will be recorded, and visualized with histograms and boxplots.  
* **Path tortuosity.** Referring to how much the path winds, path tortuosity translates to maze difficulty (Wilson et al., 2021). This will be recorded using the formula Tortuosity=shortest pathManhattan distance. Path tortuosity is often skewed with outliers, this being very winding mazes. To maintain statistical integrity, the median and IQR will be recorded instead of the mean.  
* **Dead-end count**. This is the number of nodes with degree-1 in a corridor graph. Degree-1 nodes in the corridor graph will be counted, finding the mean, SD, and median of degree-1 nodes in each maze group will be recorded. The distribution will be visualized with histogram and boxplots.  
* **Junction proportions**. The proportion of nodes with degree-3 and degree-4 relative to the total number of junction nodes.  For each corridor graph, compute p3=degree-3junctionsand p4=degree-4junctions for recording. Group means will be visualized with histograms, and bootstrap with 95% CI.  
* **Turns and straightaways**. Degree-2 chains are collapsed into corridor edges after recording counts of straight corridors and counts of turns per corridor. Collapsed corridor edges will be identified and classified as straight (no internal turns) or turning (contains a turn). The study will report the histogram and the mean turns.

For maze diversity, the following will be visualized to show if there is a difference in diversity of mazes among PRNG generated mazes and QRNG generated mazes.

**Expressive Range Analysis (ERA)**. Two metrics will be chosen as axes for ERA, Linearity and Leniency. To ensure proper measurement, the cell graph of the maze will be used to compute both. The convex hull area of the ERA cloud of PRNG and QRNG will be visualized and measured, where a larger area indicates greater expressive range, meaning greater diversity.

* Linearity is the fraction of straight corridor length over the total corridor length. To compute, the sum of lengths of degree-2 nodes with no turns divided by the total number of corridors (degree-2 nodes).  
  Linearity=degree-2 nodes with no turnsall degree-2 nodes  
* Leniency is the fraction of negative of the sum of all dead-ends divided by the total number of cells.  
  Leniency=-(Dead-end nodes)all nodes  
* Scatter Plot of Linearity vs. Leniency, using different colors and semi-transparent markers for PRNG and QRNG points.  
* Convex hull is the area of the smallest convex polygon that contains all the points in a group, and will be computed using Gauss area formula A=12|i=1n(xiyi+1-(yixi+1)|.

### ***Reinforcement learning agent metrics***

**Agent Training Metrics.** Three RL models will train on PRNG-generated mazes. A separate training process will be conducted for QRNG-generated mazes. The following will be recorded during training.

* **Training Reward over Episodes**. The cumulative rewards per episode of the agents on QRNG and PRNG training of the agents are recorded and are shown in a time-series graph. Plotting this over time highlights learning, showing whether agents improve steadily and when their performance stabilizes.  
  * **Success Rate % (SR) over Episodes.** This shows the progress of learning and generalization of the agents in both QRNG and PRNG mazes.

**Agent Evaluation Metrics.** The AgentQRNG and AgentPRNG will be evaluated in novel mazes of both sources, and the following metrics recorded.

* **Success Rate % (SR).** This reflects the agent’s reliability in solving novel tasks  
  * **Reward.** This summarizes the overall navigation quality, combining positive outcomes with penalties for the agent’s inefficiency or invalid moves.  
    * **Amount of Steps Taken.** The amount of steps measures path efficiency, indicating whether solutions are near‑optimal or unnecessarily long.  
      * **Generalization Gap.** *SRintra \- SRcross*, quantifies the drop in success between familiar and unfamiliar maze distributions, which serves as a key indicator of robustness and resistance to overfitting.

## **3.7 Benchmarking Framework**

### ***3.7.1 Baseline Methods***

The PRNG-trained agents (AgentPRNG) serve as the baseline for comparison in this study. Specifically, DQN, A2C, and PPO trained on PRNG-seeded mazes establish the standard procedural generation benchmark. These algorithms were selected because they represent distinct families of deep reinforcement learning: value-based (DQN), policy gradient (PPO), and hybrid actor-critic (A2C). This allows for a broad and representative comparison. The PRNG-trained models serve as the stationary baseline against which quantum advantage is measured.

### ***3.7.2 Benchmark Datasets or Test Instances***

The benchmark dataset consists of synthetically generated 20×20 mazes produced by the recursive backtracking algorithm. Separate maze sets are generated from PRNG seeds and QRNG seeds, with 10 Million timesteps, evaluated to approximately 33,000 to 38,000 mazes used for training and 100  mazes per unseen test instance. All raw seeds are stored in prng\_seeds.csv and qrng\_seeds.csv for auditability.

### ***3.7.3 Performance Evaluation and Validation***

Performance is evaluated across both intra-domain and cross-domain conditions, as described in the Generalization Testing Strategy section. Quantitative differences in success rate, reward, and steps taken between AgentPRNG and AgentQRNG are assessed using the statistical procedures defined in Section 3.8. Model checkpoints are saved every 10,000 steps throughout training to enable continuous monitoring of the learning curve and to support post-hoc validation of convergence behavior.

## **3.8 Statistical Validation**

This section covers what to do with the evaluated metrics, testing for statistical and practical significance towards maze structures, maze diversity of each group, and solver behavior. A significance level of  \= 0.05 was used with a sample size of 5,000 out of the 71,800 seeds as the following tests are sensitive to outliers at samples higher than 5,000.

### ***One variable tests***

**1\. Testing for Normality.** The mentioned data will be tested for normality before undergoing other tests. Normality testing is done to validate assumptions of parametric tests, and adjusted if necessary. The recorded variables will go through the Shapiro-Wilk test, as research has shown that the efficiency of the Shapiro-Wilk test is sensitive to sample size, with low sample counts generating bias in normality analysis (Souza et al., 2023). If Shapiro-Wilk detects non-normality, non-parametric tests will be considered. The Python library scipy.stats has Shapiro-Wilk as one of its tests, which will be used for automation of tests.

**2\. Comparison tests.** The study will use independent samples t-test since the difference of structural quality of PRNG mazes and QRNG mazes will be compared, which are independent from each other. The Welch t-test is recommended as best practice when comparing two independent groups, as it allows for unequal standard deviations between groups and has almost as much statistical power as Student's t-test (West, 2021). Independent samples t-test use the formula:  
t \= (x1 \-  x2)s12n1 \+ s22n2  
where x1and x2 are the means of the two samples, s1 and s2 are the standard deviations, and n1 and n2 are the sizes, where equal variances are assumed. If the calculated pα (which is 0.05), there is a significant difference between the two means.  
	In the case of a non-normal distribution, the statistical tool Mann-Whitney U will be used as a nonparametric test. Mann-Whitney U is used to determine if there is a significant difference between two groups by ranking all data points from two independent groups from lowest to highest, assigning average ranks for ties. As a nonparametric alternative to the t-test, Mann-Whitney's U test compares two independent groups without requiring the assumption of normality, though it does assume exchangeability between the groups (Karch, 2021). Mann-Whitney U uses the formulaUc=ncntnc(nc+1)2-Rt and Ut=ncntnt(nt+1)2-Rc, where nc and nt are the sample sizes for the control and treated groups, and Rc and Rt are the sums of the ranks for each group. If p \< α (which is 0.05), reject H₀ → conclude a statistically significant difference.

### ***Multivariate testing***

**1\. Permutational Multivariate Analysis of Variance (PERMANOVA)** will be applied towards the metrics that are found to be non-normal distributions. PERMANOVA is a non-parametric method that operates directly on distance matrices. PERMANOVA partitions the variation in the distance matrix among groups and assesses significance through a number of permutations, thereby providing a robust test of group differences without requiring normalization.

The null hypothesis will be tested with 𝞪 \= 0.05: Ho \= There is no significant difference between corridor length, betweenness centrality, and spectral features between PRNG mazes and QRNG mazes.

After PERMANOVA is performed, the primary test statistic reported will be pseudo-F, which comes from the ratio of between-group to within-group variation in the distance matrix. Significance of the pseudo-F will be assessed through permutation tests (1000). If the null hypothesis is rejected, analysis will be done to identify which specific metrics contributed strongly to the result. This will be done by using pair-wise PERMANOVA tests on pairs of metrics.

**2\. Multivariate Analysis of Variance (MANOVA)** will use the mean vectors of normalized structural maze metrics. The goal of MANOVA is to determine whether the means of the dependent variable differ significantly across groups while considering the interrelationships between the variables. This is the multivariate version of ANOVA. Prior to conducting MANOVA, the provided data will first need to be screened and tested against core assumptions such as independence of observations, absence of univariate and multivariate outliers, linearity, multivariate normality, and homogeneity of covariance matrices.

The hypotheses for MANOVA will be tested with a 𝞪 \= 0.05: Null Hypothesis (H0)  \= The means of the dependent variables which are the structural maze metrics are equal across the two groups (PRNG and QRNG). There is no significant multivariate effect of the RNG type on the combined structural metrics of the mazes.

After the one-way MANOVA is performed, the primary test statistic reported will be Wilk’s Lambda (Λ). If the null hypothesis is rejected, a follow up test will be performed for further analysis in order to pinpoint the source of the difference, this is done by performing separate univariate F-tests for each dependent variable in order to determine which is the specific structural metric that contributed to the overall multivariate effect. The effect size for the significant multivariate test will then be reported using partial eta squared (ɳp2).

### ***Null Hypothesis (Ho)***

1. There is no significant difference in the structural complexity and diversity of mazes generated using QRNG seeds in comparison to mazes generated using PRNG seeds.  
2. There is no significant difference in the learning curve (success rate and cumulative rewards) between DRL agents trained in PRNG-generated mazes and DRL agents trained in QRNG-generated mazes.  
3. DRL agents trained on QRNG-seeded mazes do not generalize better on unseen maze structures than agents trained on PRNG-seeded mazes.

### ***Alternative Hypothesis (H1)***

1. There is a significant difference in the structural complexity and diversity of mazes generated using QRNG seeds in comparison to mazes generated using PRNG seeds.  
2. There is a significant difference in the learning curve (success rate and cumulative rewards) between DRL agents trained in PRNG-generated mazes and DRL agents trained in QRNG-generated mazes.  
3. DRL agents trained on QRNG-seeded mazes generalize better on unseen maze structures than agents trained on PRNG-seeded mazes.

## **3.9 Ethical Considerations**

This study does not involve human subjects, survey responses, or sensitive personal data. The data collected consists entirely of computationally generated maze structures and agent performance metrics. The quantum random seeds are retrieved from the publicly accessible ANU Quantum Random Number Server, which does not require the collection of personally identifiable information. Accordingly, no informed consent procedures or institutional ethics approval for human subjects research are required for this study.

## **3.10 Reproducibility Statement**

## To ensure transparency and reproducibility of results, the following measures were implemented in this study.

## ***3.10.1 Code Availability***

## The complete source code used for seed generation, maze construction, RL training, and statistical evaluation will be archived and submitted as part of the technical documentation. The code includes detailed comments and execution instructions to facilitate replication.

## ***3.10.2 Dataset Accessibility***

## All raw API responses (raw 16-bit chunks, timestamps, and metadata) will be stored in a raw\_qrng\_logs.json file. The final seed outputs for both groups will be saved in separate CSV files (prng\_seeds.csv and qrng\_seeds.csv). The separation keeps the exact quantum data retrieval instance preserved for auditability and maintainability of the input dataset. Since the outputs of QRNG are non-deterministic, all generated values will be logged and reused as fixed inputs to ensure reproducibility and fairness in comparison with PRNG.

## ***3.10.3 Version Control***.

## 

## ***3.10.4 Random Seed Settings***

## To maintain consistency in model training and evaluation, all PRNG seeds are deterministically generated and logged prior to experimentation. QRNG seeds, being non-deterministic at the point of generation, are similarly fixed by storing the retrieved values before use. Training will occur on local hardware and Google Colab for simultaneous training, with model checkpoints saved every 10,000 steps to monitor the learning curve and ensure that the reported performance metrics can be replicated under identical computational conditions.

## 

# 

# **CHAPTER 4**

**RESULTS AND DISCUSSIONS**

This chapter presents the data gathered from the procedural generation of maze environments and the subsequent training of Deep Reinforcement Learning (DRL) agents. The findings are organized into three main sections: the initial presentation of environmental structural metrics, a comparative performance evaluation of the agents navigating these environments, and an analysis of the performance trade-offs associated with utilizing Quantum Random Number Generators (QRNG) versus traditional Pseudo-Random Number Generators (PRNG).

## **Presentation of Results**

	First, the two RNGs are tested for Shannon entropy and autocorrelation, revealing a small discrepancy between their randomness. 

	To further evaluate the structural complexity and inherent difficulty of the procedurally generated environments, five key topological metrics were determined and analyzed, that being the path length, path tortuosity, dead-end count, junction proportion, and corridor turns.![][image1]![][image2]

**Statistical Validation**

To ensure the mathematical rigor of the comparison between the Control Group (PRNG) and the Experimental Group (QRNG), a multi-stage statistical analysis was performed on the three primary topological metrics: shortest path length, dead-end count, and tortuosity**.**

1. Normality Testing Before conducting comparative tests, the distribution of the data was assessed using the Shapiro-Wilk test**.** Due to the large total sample size (approx. 71,800 per group), a sub-sample of 5,000 was utilized for each test to maintain statistical sensitivity.  
   

| Metric | Group | W-Statistic | P-value | Result |
| :---: | :---: | :---: | :---: | :---: |
| Shortest Path Length | PRNG | 0.9721 | 3.71x10\-30 | Non-Normal |
| Shortest Path Length | QRNG | 0.9744 | 4.88x10\-29 | Non-Normal |
| Dead-end Count | PRNG | 0.9751 | 1.06x10\-28 | Non-Normal |
| Dead-end Count | QRNG | 0.9749 | 8.95x10\-29 | Non-Normal |
| Tortuosity | PRNG | 0.9761 | 3.64x10\-28 | Non-Normal |
| Tortuosity | QRNG | 0.9755 | 1.77x10\-28 | Non-Normal |
| Junction P3 | PRNG | 0.3066 | 2.23x10\-87 | Non-Normal |
| Junction P3 | QRNG | 0.3052 | 2.00x10\-87 | Non-Normal |
| Junction P4 | PRNG | 0.3135 | 3.75x10\-87 | Non-Normal |
| Junction P4 | QRNG | 0.3004 | 1.40x10\-87 | Non-Normal |
| Straight Corridors | PRNG | 0.9868 | 2.89x10\-21 | Non-Normal |
| Straight Corridors | QRNG | 0.9880 | 3.01x10\-20 | Non-Normal |
| Turning Corridors | PRNG | 0.9808 | 1.61x10\-25 | Non-Normal |
| Turning Corridors | QRNG | 0.9811 | 2.76x10\-25 | Non-Normal |
| Turns Total | PRNG | 0.9960 | 1.29x10\-10 | Non-Normal |
| Turns Total | QRNG | 0.9957 | 6.19x10\-11 | Non-Normal |
| Mean Turns Per Corridor | PRNG | 0.9694 | 2.17x10\-31 | Non-Normal |
| Mean Turns Per Corridor | QRNG | 0.9629 | 5.29x10\-34 | Non-Normal |

As shown in table \_\_\_\_all metrics for both groups returned p-values significantly below 0.05, leading to the rejection of the null hypothesis of normality. Consequently, non-parametric tests were employed for all subsequent comparisons.

2. Univariate Group Comparisons The Mann-Whitney U test was used to compare the medians of the independent PRNG and QRNG samples.

| Metric | PRNG Median | QRNG Median | U-Statistic | P-value |
| :---: | :---: | :---: | :---: | :---: |
| Shortest Path Length |  84.00 | 84.00 | 2,951,379,324 | 0.7982 |
| Dead-end Count | 12.00 | 12.00 | 2,952,793,045 | 0.6715 |
| Tortuosity | 2.47  | 2.47 | 2,951,379,324 | 0.7982 |
| Junction P3 | 1.00 | 1.00 | 2,942,843,616 | 0.1252 |
| Junction P4 | 0.00 | 0.00 | 2,955,473,184 | 0.1252 |
| Straight Corridors | 12.00 | 12.00 | 2,957,372,030 | 0.3425 |
| Turning Corridors | 13.00 | 13.00 | 2,944,203,066 | 0.5645 |
| Turns Total | 46.00 | 46.00 | 2,940,175,813 | 0.3002 |
| Mean Turns Per Corridor | 1.78 | 1.78 | 2,941,772,091 | 0.3953 |

The univariate analysis reveals that the medians for all three metrics are identical between the two groups. With p-values well above the 0.05 threshold, there is no statistically significant difference in the individual structural features of the mazes

.

3. Multivariate Analysis (PERMANOVA) To determine if a difference existed in the combined structural profile (the interrelationship between all metrics), a Permutational Multivariate Analysis of Variance (PERMANOVA) was conducted using Euclidean distance on z-scored metrics.

| Statistic | Value |
| :---: | :---: |
| Pseudo-F Statistic | 0.501039 |
| P-value | 0.749251 |
| Permutations | 1000 |
| Decision | Fail to reject H0 |

The PERMANOVA result (p=0.749251) confirms that there is no significant multivariate effect of the RNG type on the combined structural metrics of the mazes.

## **Comparative Analysis / Performance Evaluation**

Both PRNG and QRNG agents were trained on 10 million timesteps using the PPO algorithm with 12 parallel environments, each exploring unique maze sequences via seed offset indexing. Training logs were maintained throughout to track progression metrics including per-episode rewards, success rates, and path efficiency.

**PPO Training**

**PRNG**

The PRNG-seeded agent trained on 38,993 episodes over 35.88 minutes:

| Metric | Value |
| ----- | ----- |
| Final Success Rate (100-ep avg) | 82.0% |
| Peak Success Rate | 98.0% |
| Overall Success Rate | 64.19% |
| Final Avg Reward | 372.51 |
| Peak Episode Reward | 617.88 |
| Total Successes | 25,030 / 38,993 |
| Training Evaluation Reward | 340.03 ± 95.65 |

Key observations: The PRNG agent demonstrated strong convergence, achieving a peak success rate of 98% on the training distribution. The learning curve shows steady improvement with a final moving-average success rate of 82%, indicating stable performance in later training phases.

**QRNG**

The QRNG-seeded agent trained on 33,435 episodes over 35.71 minutes:

| Metric | Value |
| ----- | ----- |
| Final Success Rate (100-ep avg) | 82.0% |
| Peak Success Rate | 88.0% |
| Overall Success Rate | 49.91% |
| Final Avg Reward | 368.82 |
| Peak Episode Reward | 602.76 |
| Total Successes | 16,687 / 33,435 |
| Training Evaluation Reward | 361.92 ± 94.52 |

Key observations: The QRNG agent converged to the same final success rate (82%) but with lower peak performance (88% vs 98%) and fewer total successes (49.91% vs 64.19%). Notably, the QRNG agent's training evaluation reward was higher (361.92 vs 340.03), suggesting better generalization on held-out training-distribution mazes despite lower overall training success.

Both agents reached the same final 100-episode moving average success rate (82.0%), suggesting convergence to a comparable performance plateau. The PRNG agent showed faster convergence to higher peak performance, while the QRNG agent exhibited a more gradual learning trajectory. The difference in total episodes (38,993 vs 33,435) or reward levels did not prevent convergence to the same moving-average success metric.

**Evaluation**

To assess true generalization capability, both trained agents were evaluated on completely novel mazes using seeds offset by 40,000 positions from the training seed range. This evaluation protocol ensures zero overlap between training and evaluation maze instances. Each condition was tested on 100 independent episodes.

Results

| Agent | Evaluation Set | Episodes | Success Rate | Avg Reward | Std Dev | Avg Steps |
| ----- | ----- | ----- | ----- | ----- | ----- | ----- |
| PRNG | Novel PRNG | 100 | 66.0% | 341.47 | 102.01 | 226.3 |
| PRNG | Novel QRNG | 100 | 66.0% | 341.38 | 82.78 | 222.6 |
| QRNG | Novel QRNG | 100 | 55.0% | 319.21 | 98.84 | 268.1 |
| QRNG | Novel PRNG | 100 | 59.0% | 326.47 | 114.27 | 255.8 |

Key Finding: The PRNG agent demonstrated superior generalization on unseen mazes, achieving 66% success rate on novel instances from both distributions. The QRNG agent achieved only 55% on its matched distribution and 59% on the cross-distribution, representing an 11pp disadvantage compared to the PRNG agent's intra-distribution performance.

**Generalization**

Generalization gaps quantify the performance drop when agents encounter unfamiliar maze distributions:

| Agent | Intra-Distribution SR | Cross-Distribution SR | Gap (pp) | Interpretation |
| ----- | ----- | ----- | ----- | ----- |
| PRNG | 66.0% | 66.0% | 0.0 | Excellent generalization; no distribution-specific overfitting |
| QRNG | 55.0% | 59.0% | \-4.0 | Positive gap; performs *better* on cross-distribution |

Interpretation: The PRNG agent shows zero generalization gap, indicating that the agent's learned policies in this case transferred equally well to novel PRNG and QRNG distributions. This suggests the PRNG sequence distribution captures fundamental maze structural patterns.

The QRNG agent exhibits a negative gap (-4.0pp), meaning it paradoxically performs better on unfamiliar PRNG mazes than on novel QRNG mazes. This counterintuitive result suggests potential overfitting to QRNG-specific patterns during training, leading to slight performance degradation when encountering the trained distribution again under novel seeds.

## **Performance Trade-offs Analysis**

4.1 Presentation of Results

This section focuses on the environmental structural metrics.

You must present data for the five key topological metrics: path length, path tortuosity, dead-end count, junction proportion, and corridor turns

.

This section also includes the Expressive Range Analysis (ERA), specifically visualizing the Linearity vs. Leniency of the mazes and measuring the convex hull area to identify maze diversity.

It is also where you report the initial statistical diagnostics of your seeds, such as Shannon Entropy and Autocorrelation.

4.2 Comparative Analysis / Performance Evaluation

This section evaluates the Deep Reinforcement Learning (DRL) agents (DQN, A2C, and PPO).

Agent Training Metrics: Report the Training Reward over Episodes and Success Rate (SR) over Episodes for both PRNG and QRNG groups.

Agent Evaluation Metrics: Report the Success Rate, Reward, and Amount of Steps Taken during testing on novel mazes.

Generalization Gap: Present the quantitative drop in success (SR intra −SR cross) to measure robustness against overfitting.

Statistical Validation: Include the results of your Shapiro-Wilk normality tests, Independent T-tests (or Mann-Whitney U), and the Multivariate Analysis of Variance (MANOVA) to confirm if differences are statistically significant.

4.3 Performance Trade-offs Analysis

This section analyzes the practical implications of your chosen technology.

It should discuss the constraints of using Quantum Random Number Generators (QRNG) via external APIs (like ANU-QRNG) versus the mathematical efficiency of Pseudo-Random Number Generators (PRNG).

# **CHAPTER 5**

**SUMMARY, CONCLUSIONS AND RECOMMENDATION**

## **Summary**

## **Conclusions**

## **Recommendations**

[image1]: <data:image/png;base64,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V14ZzJw500zHuO6661Q7cODAMIeoFI8yiMq8efOCYcOGmWmnQVTsUO3N3KXabk1UZsyYod4CaiuISvGotrYlXCV21bXFwqdPnx706tVL9c338BGV4lFkUWlLvbsKomKHam/mLtV2mqj069fPTLUJRKV4VFvbEq5i9apDVIpHkUXFZxAVO1R7M3epttNEpS3ID5jy+awoPojK6YFEjtquTKXafmLQ3wT/uGBEIi/hKlavOkSleCAqboKo2KHSzbxSuFTbWUVFmDUr/lBySVT++uyfB0+9+R+xeHj4OUpUbpn8t4kxWR+SSK1+ctvNsei6pKt6HSX+ccGwxLirWL3qEJXigai4CaJihzKKyogRI8yUU6Ji3rsf/G6LpESD2j4zZm0/9u3/mngdb17wvdg6rmL1qkNUigei4iaIih3Mm/mZwqXazioqabgsKgtGfTXxgKW2z4xZ20uG/rfE6/jz+SNj67iK1asOUSkeiIqbICp2MG/mZwqXarssoiKhZeXG6/9HYozaTiettqNv/dw2//uJcVexetUhKsUDUXETRMUOaTfz1sKl2i6TqEiYMynUdutUqm2ZWZmVIikSrmL1qkNUigei4iaIih0q3cxXz/1hIudabZdNVCoFtZ1OpdpuLVzF6lXng6hs/Z9nq+kvMy+BqCSpJCryGm75xtmJvIRLN/OikiYqfX/dmZ86qyTtZq6nx6+8/6LEmEu1jahQ262RVttnClexetW5LirR9+e6LumWGEdUkqSJSvx17JoYd+lmXlRMUYmekwe+e06itrmZp2PezJ+Z+3/C11HC5dpGVKjt1jBruy3hKlavOpdF5d//19mxG5B+yEbXQVSSmKISfSDqeOt//5fYOi7dzItKVFTSzsl9l/13buZtIHozf3retYnXUcLV2kZUqO3WQFQq4LKopN3M57y6PLYOopLEFJV/nTc58Tqasyou3cyLijmjknZOuJmfGfNmPvPqryVeR1dru6iiUomzHHrtfeaVV14xU85j9cy7LCqmrNzx6h8T44hKElNUJHjrJ39MUbni6RsrSgqiUhlTVCT06yizsOaYS7WNqEAWEBXHRUXLijmTogNRSZImKhJPzZucKimu3cyLiikqEmNXXp8qKRKISjppoiJx6zV/m8i5VtuICmQBUfFAVFoLRCVJJVFpLVy6mReVNFFpLRCVdCqJSqVwqbYR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>

[image2]: <data:image/png;base64,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>