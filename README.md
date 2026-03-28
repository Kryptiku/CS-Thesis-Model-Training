# CS Thesis: PRNG vs QRNG Randomness in Reinforcement Learning Maze Navigation

This project investigates whether the source of randomness (Pseudo-Random vs Quantum Random Number Generators) used during maze generation affects the generalization capability of reinforcement learning agents trained to navigate 20x20 mazes.

## Project Structure

```
CS-Thesis-Model-Training/
├── seeds/                          # Shared seed CSVs (PRNG & QRNG)
├── ppo/                            # Proximal Policy Optimization
│   ├── scripts/                    # All PPO-related scripts
│   ├── models/                     # Trained model .zip files
│   └── outputs/
│       ���── training_logs/          # Per-episode training CSVs
│       ├── training_reports/       # HTML reports & PNG charts
│       ├── evaluation_results/     # Cross-distribution eval results
│       ├── maze_metrics/           # Structural maze analysis CSVs
│       └── statistical_analysis/   # PRNG vs QRNG stat reports
├── a2c/                            # Advantage Actor-Critic
│   ├── scripts/                    # All A2C-related scripts
│   ├── models/                     # Trained model .zip files
│   └── outputs/
│       ├── training_logs/          # Per-episode training CSVs
│       ├── training_reports/       # HTML reports & PNG charts
│       ├── evaluation_results/     # Cross-distribution eval results
│       ├── maze_metrics/           # Structural maze analysis CSVs
│       └── statistical_analysis/   # PRNG vs QRNG stat reports
```

## Prerequisites

- Python 3.10+
- GPU recommended (CUDA) but CPU works

### Install Dependencies

```bash
pip install numpy gymnasium stable-baselines3 torch pandas matplotlib tqdm scipy
```

For PERMANOVA (optional, used in statistical analysis):
```bash
pip install scikit-bio
```

## Setup

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd CS-Thesis-Model-Training
   ```

2. Place your seed CSV files in `seeds/`:
   - `seeds/prng_seeds.csv` -- seeds generated from a pseudo-random source
   - `seeds/qrng_seeds.csv` -- seeds generated from a quantum random source

   Each CSV must have a `number` column containing integer seeds.

## PPO Pipeline

### Step 1: Train Agents

Train two separate PPO agents -- one on PRNG-seeded mazes, one on QRNG-seeded mazes.

```bash
# Train PRNG agent (~10M timesteps)
python3 ppo/scripts/train_prng.py

# Train QRNG agent (~10M timesteps)
python3 ppo/scripts/train_qrng.py
```

**Outputs:**
- `ppo/models/*.zip` -- trained model weights
- `ppo/outputs/training_logs/` -- per-episode reward, success, steps
- `ppo/outputs/training_reports/` -- HTML report with reward curves and success rate charts

### Step 2: Evaluate Agents on Unseen Mazes

Runs 4 evaluation conditions (100 episodes each) using mazes from seed offset 40,000+ (never seen during training):

| Condition | Agent | Maze Source | Type |
|-----------|-------|-------------|------|
| 1 | PRNG model | Novel PRNG mazes | Intra-distribution |
| 2 | PRNG model | Novel QRNG mazes | Cross-distribution |
| 3 | QRNG model | Novel QRNG mazes | Intra-distribution |
| 4 | QRNG model | Novel PRNG mazes | Cross-distribution |

```bash
python3 ppo/scripts/evaluate_agents.py
```

**Outputs:**
- `ppo/outputs/evaluation_results/evaluation_results.csv` -- per-episode results
- `ppo/outputs/evaluation_results/evaluation_report.html` -- visual report with generalization gap analysis

### Step 3: Extract Maze Structural Metrics

Analyzes maze topology for each seed: shortest path length, tortuosity, dead ends, junction counts, corridor structure.

```bash
python3 ppo/scripts/maze_metrics_extractor.py \
  --seeds seeds/prng_seeds.csv \
  --output ppo/outputs/maze_metrics/prng_metrics.csv

python3 ppo/scripts/maze_metrics_extractor.py \
  --seeds seeds/qrng_seeds.csv \
  --output ppo/outputs/maze_metrics/qrng_metrics.csv
```

**Outputs:**
- Per-maze metrics CSV + summary statistics CSV for each seed type

### Step 4: Statistical Comparison (PRNG vs QRNG)

Tests whether PRNG and QRNG mazes are structurally different using:
- Shapiro-Wilk normality test
- Welch t-test (normal data) or Mann-Whitney U (non-normal data)
- PERMANOVA multivariate test

```bash
# Basic analysis (3 metrics: shortest_path_len, dead_end_count, tortuosity)
python3 ppo/scripts/statistical_analysis.py \
  --prng ppo/outputs/maze_metrics/prng_metrics.csv \
  --qrng ppo/outputs/maze_metrics/qrng_metrics.csv \
  --output ppo/outputs/statistical_analysis/report.txt

# Extended analysis (9 metrics including corridor structure)
python3 ppo/scripts/statistical_analysis_extended.py \
  --prng ppo/outputs/maze_metrics/prng_metrics.csv \
  --qrng ppo/outputs/maze_metrics/qrng_metrics.csv \
  --output ppo/outputs/statistical_analysis/report_extended.txt
```

## A2C Pipeline

### Step 1: Train Agents

Train two separate A2C agents -- one on PRNG-seeded mazes, one on QRNG-seeded mazes.

```bash
# Train PRNG agent (~10M timesteps)
python3 a2c/scripts/train_prng.py

# Train QRNG agent (~10M timesteps)
python3 a2c/scripts/train_qrng.py
```

**Outputs:**
- `a2c/models/*.zip` -- trained model weights
- `a2c/outputs/training_logs/` -- per-episode reward, success, steps
- `a2c/outputs/training_reports/` -- HTML report with reward curves and success rate charts

### Step 2: Evaluate Agents on Unseen Mazes

Runs 4 evaluation conditions (100 episodes each) using mazes from seed offset 40,000+ (never seen during training):

| Condition | Agent | Maze Source | Type |
|-----------|-------|-------------|------|
| 1 | PRNG model | Novel PRNG mazes | Intra-distribution |
| 2 | PRNG model | Novel QRNG mazes | Cross-distribution |
| 3 | QRNG model | Novel QRNG mazes | Intra-distribution |
| 4 | QRNG model | Novel PRNG mazes | Cross-distribution |

```bash
python3 a2c/scripts/evaluate_agents.py
```

**Outputs:**
- `a2c/outputs/evaluation_results/evaluation_results.csv` -- per-episode results
- `a2c/outputs/evaluation_results/evaluation_report.html` -- visual report with generalization gap analysis

### Step 3: Extract Maze Structural Metrics

Uses the same shared maze metrics extractor:

```bash
python3 ppo/scripts/maze_metrics_extractor.py \
  --seeds seeds/prng_seeds.csv \
  --output a2c/outputs/maze_metrics/prng_metrics.csv

python3 ppo/scripts/maze_metrics_extractor.py \
  --seeds seeds/qrng_seeds.csv \
  --output a2c/outputs/maze_metrics/qrng_metrics.csv
```

### Step 4: Statistical Comparison (PRNG vs QRNG)

Uses the same shared statistical analysis scripts:

```bash
python3 ppo/scripts/statistical_analysis.py \
  --prng a2c/outputs/maze_metrics/prng_metrics.csv \
  --qrng a2c/outputs/maze_metrics/qrng_metrics.csv \
  --output a2c/outputs/statistical_analysis/report.txt

python3 ppo/scripts/statistical_analysis_extended.py \
  --prng a2c/outputs/maze_metrics/prng_metrics.csv \
  --qrng a2c/outputs/maze_metrics/qrng_metrics.csv \
  --output a2c/outputs/statistical_analysis/report_extended.txt
```

### A2C Hyperparameters

| Parameter | Value |
|-----------|-------|
| **learning_rate** | 3e-4 |
| **n_steps** | 5 |
| **gamma** | 0.99 |
| **gae_lambda** | 1.0 |
| **ent_coef** | 0.01 |
| **vf_coef** | 0.5 |
| **max_grad_norm** | 0.5 |
| **use_rms_prop** | False (Adam) |
| **normalize_advantage** | False |
| **Network** | pi=[256,256], vf=[256,256] |

## Key Metrics

| Metric | Description |
|--------|-------------|
| **Success Rate (SR)** | % of episodes where the agent reaches the goal |
| **Generalization Gap** | SR_intra - SR_cross (lower = better generalization) |
| **Avg Reward** | Cumulative episode reward (higher = better navigation) |
| **Avg Steps** | Steps to reach goal or timeout at 500 (lower = more efficient) |
| **Tortuosity** | Shortest path / Manhattan distance (higher = more complex maze) |

## Environment Details

- **Maze size:** 20x20 grid
- **Generation:** Recursive backtracking (DFS) with 4-directional carving
- **Observation:** 8-ray LIDAR (normalized) + 2D target vector = 10 inputs
- **Actions:** 4 discrete (Up, Right, Down, Left)
- **Max steps:** 500 per episode
- **Frame stacking:** 4 frames (temporal context)
- **Training:** PPO / A2C with 12 parallel environments, 10M timesteps

## Reward Structure

| Event | Reward |
|-------|--------|
| Reach goal | +250 |
| Move closer + new cell | +2.0 + 0.5 * progress |
| Move closer + visited cell | +0.2 + 0.5 * progress |
| Explore new cell (no progress) | +0.3 |
| Step penalty | -0.005 |
| Wall collision | -0.75 |
| Timeout (500 steps) | -7 |
