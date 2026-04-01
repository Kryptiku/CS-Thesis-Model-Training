import numpy as np
import gymnasium as gym
from gymnasium import spaces
import random
import torch
from stable_baselines3 import A2C
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.vec_env import SubprocVecEnv, VecFrameStack, DummyVecEnv
from stable_baselines3.common.callbacks import BaseCallback
from tqdm import tqdm
import os
import sys
import time
import csv
from collections import deque
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

# --- PART 1: MAZE GENERATOR ---
class MazeGenerator:
    def __init__(self, size=20, seed_type="PRNG"):
        self.size = size
        self.seed_type = seed_type

    def generate(self, seed=None):
        maze = np.ones((self.size, self.size), dtype=int)
        if seed is not None:
            random.seed(seed)
        elif self.seed_type == "PRNG":
            random.seed(None)

        def carve(x, y):
            maze[y, x] = 0
            # GENERATION: STRICT 4 DIRECTIONS (Manhattan Geometry)
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            random.shuffle(directions)
            for dx, dy in directions:
                nx, ny = x + dx*2, y + dy*2
                if 0 <= nx < self.size and 0 <= ny < self.size and maze[ny, nx] == 1:
                    maze[y + dy, x + dx] = 0
                    carve(nx, ny)

        carve(1, 1)
        maze[1, 1] = 0
        maze[self.size-2, self.size-2] = 0
        return maze

# --- PART 2: HYBRID ENVIRONMENT ---
class LidarMazeEnv(gym.Env):
    maze_counter = 0  # Class variable to track total mazes

    def __init__(self, size=20, seed_type="PRNG", max_steps=500, seed_csv_path=None, env_id=0):
        super(LidarMazeEnv, self).__init__()
        self.size = size
        self.generator = MazeGenerator(size, seed_type)
        self.maze = None
        self.agent_pos = None
        self.target_pos = None
        self.max_steps = max_steps
        self.current_step = 0
        self.current_dist = 0
        self.visited_cells = set()  # Track explored cells for bonus
        self.current_maze_seed = None  # Track current maze seed
        self.env_id = env_id  # Unique ID for this environment

        # Load seeds from CSV if provided
        self.seeds = []
        self.seed_index = env_id  # OFFSET: Each env starts at different seed index
        self.seed_csv_path = seed_csv_path  # Store for tracking
        if seed_csv_path and os.path.exists(seed_csv_path):
            df = pd.read_csv(seed_csv_path)
            self.seeds = df['number'].tolist()
            if env_id == 0:  # Only print once
                print(f"✅ Loaded {len(self.seeds)} seeds from {seed_csv_path}")
                # Verify first few seeds
                if len(self.seeds) > 0:
                    print(f"   Sample seeds [0-4]: {self.seeds[:5]}")
        else:
            if env_id == 0:  # Only print once
                print(f"⚠️  No CSV provided or file not found - using random seeds")
            self.seed_csv_path = None

        # --- ACTION SPACE: STRICT 4 DIRECTIONS (Thesis Compliance) ---
        # 0=Up, 1=Right, 2=Down, 3=Left
        self.action_space = spaces.Discrete(4)

        # --- OBS SPACE: HIGH DEF 8-RAY LIDAR (Better Intelligence) ---
        # 8 Lidar rays + 2 Target Vector = 10 Inputs
        self.observation_space = spaces.Box(low=-1, high=1, shape=(10,), dtype=np.float32)

    def _get_manhattan_distance(self, y, x):
        """Fast Manhattan distance - no pathfinding needed"""
        return abs(self.target_pos[0] - y) + abs(self.target_pos[1] - x)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        # Get seed from CSV if available, otherwise generate random
        if self.seeds:
            self.current_maze_seed = self.seeds[self.seed_index % len(self.seeds)]
            self.seed_index += len(self.seeds) // 12  # STEP: Skip ahead to ensure parallelism
        else:
            self.current_maze_seed = random.randint(0, 2**31 - 1)

        self.maze = self.generator.generate(seed=self.current_maze_seed)
        self.agent_pos = [1, 1]
        self.target_pos = [self.size-2, self.size-2]
        self.current_step = 0
        self.visited_cells = set()  # Reset visited cells for new maze
        self.visited_cells.add((1, 1))  # Mark starting position as visited
        self.current_dist = self._get_manhattan_distance(self.agent_pos[0], self.agent_pos[1])
        LidarMazeEnv.maze_counter += 1
        return self._get_obs(), {}

    def _get_lidar(self):
        # --- VISION: 8 DIRECTIONS (Allows seeing corners) ---
        directions = [
            (-1, 0), (-1, 1), (0, 1), (1, 1),
            (1, 0), (1, -1), (0, -1), (-1, -1)
        ]
        readings = []
        for dy, dx in directions:
            dist = 0
            cy, cx = self.agent_pos[0], self.agent_pos[1]
            while True:
                cx += dx
                cy += dy
                if not (0 <= cx < self.size and 0 <= cy < self.size) or self.maze[cy, cx] == 1:
                    break
                dist += 1
            readings.append(dist / self.size)
        return readings

    def _get_obs(self):
        lidar = self._get_lidar()
        target_vec = [
            np.clip((self.target_pos[0] - self.agent_pos[0]) / self.size, -1, 1),
            np.clip((self.target_pos[1] - self.agent_pos[1]) / self.size, -1, 1)
        ]
        return np.array(lidar + target_vec, dtype=np.float32)

    def step(self, action):
        self.current_step += 1
        # --- MOVEMENT: STRICT 4 DIRECTIONS ---
        moves = {0: (-1, 0), 1: (0, 1), 2: (1, 0), 3: (0, -1)}
        dy, dx = moves[action]

        old_dist = self.current_dist
        new_y = self.agent_pos[0] + dy
        new_x = self.agent_pos[1] + dx

        reward = -0.005  # Step penalty (REDUCED for faster learning)

        if not (0 <= new_x < self.size and 0 <= new_y < self.size) or self.maze[new_y, new_x] == 1:
            reward = -0.75  # Wall penalty (REDUCED to encourage exploration)
            terminated = False
        else:
            self.agent_pos = [new_y, new_x]
            new_dist = self._get_manhattan_distance(new_y, new_x)
            self.current_dist = new_dist

            # Check if this is a new cell
            cell = (new_y, new_x)
            is_new_cell = cell not in self.visited_cells
            if is_new_cell:
                self.visited_cells.add(cell)

            # Calculate progress (Manhattan distance improvement)
            progress = old_dist - new_dist

            # OPTIMIZED REWARD STRUCTURE: Direct progress incentive + exploration bonuses
            if progress > 0:
                reward += 0.5 * progress  # Direct reward for moving closer to goal
                if is_new_cell:
                    reward += 2.0  # Big reward for productive exploration
                else:
                    reward += 0.2  # Bonus for progress even without new exploration
            elif is_new_cell:
                reward += 0.3  # Increased exploration bonus for better discovery

            if self.agent_pos == self.target_pos:
                reward += 250  # Goal reward (INCREASED to 250)
                terminated = True
            else:
                terminated = False

        if self.current_step >= self.max_steps:
            truncated = True
            if not terminated:
                reward += -7  # Timeout penalty (REDUCED from -10)
        else:
            truncated = False

        # Add goal_reached flag and maze_seed to info for tracking
        info = {
            'goal_reached': self.agent_pos == self.target_pos,
            'maze_seed': self.current_maze_seed
        }

        return self._get_obs(), reward, terminated, truncated, info

# --- PROGRESS BAR WITH CSV LOGGING ---
class ProgressBarCallback(BaseCallback):
    def __init__(self, total_timesteps, log_file="training_log_prng.csv", seed_csv_path=None):
        super().__init__()
        self.pbar = None
        self.total_timesteps = total_timesteps
        self.episode_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.log_file = log_file
        self.seed_csv_path = seed_csv_path

        # Rolling window tracking (last 100 episodes)
        self.episode_rewards = deque(maxlen=100)
        self.episode_lengths = deque(maxlen=100)
        self.episode_successes = deque(maxlen=100)

        # Per-environment tracking
        self.env_episode_rewards = {}
        self.env_episode_lengths = {}

        # Unique maze tracking
        self.unique_mazes = set()
        self.logged_seeds = []  # Track seeds for verification

    def _on_training_start(self):
        self.pbar = tqdm(total=self.total_timesteps, desc="Training Progress")

        # Create CSV file with headers and metadata
        with open(self.log_file, 'w', newline='') as f:
            writer = csv.writer(f)
            # Write metadata
            if self.seed_csv_path:
                writer.writerow([f'# Seed CSV: {self.seed_csv_path}'])
            else:
                writer.writerow(['# Seed CSV: None (using random seeds)'])
            writer.writerow(['# NOTE: A2C Training - Each environment uses unique/offset mazes in parallel'])
            writer.writerow([])
            # Write column headers
            writer.writerow([
                'episode', 'timestep', 'maze_seed', 'reward', 'length',
                'success', 'avg_reward_100', 'avg_length_100',
                'success_rate_100', 'unique_mazes_seen'
            ])

    def _on_step(self):
        # Track per-environment episode stats
        if self.locals.get('dones') is not None:
            dones = self.locals['dones']
            rewards = self.locals.get('rewards', [])
            infos = self.locals.get('infos', [])

            for i, done in enumerate(dones):
                # Initialize tracking for this environment
                if i not in self.env_episode_rewards:
                    self.env_episode_rewards[i] = 0
                    self.env_episode_lengths[i] = 0

                # Accumulate rewards and steps
                if i < len(rewards):
                    self.env_episode_rewards[i] += rewards[i]
                self.env_episode_lengths[i] += 1

                if done:
                    # Episode completed
                    episode_reward = self.env_episode_rewards[i]
                    episode_length = self.env_episode_lengths[i]

                    # Extract info
                    success = False
                    maze_seed = 0
                    if i < len(infos):
                        success = infos[i].get('goal_reached', False)
                        maze_seed = infos[i].get('maze_seed', 0)
                        if maze_seed:
                            self.unique_mazes.add(maze_seed)
                            # Track for verification
                            if len(self.logged_seeds) < 20:
                                self.logged_seeds.append((self.episode_count, maze_seed))

                    # Update counters
                    self.episode_count += 1
                    if success:
                        self.success_count += 1
                    else:
                        self.failure_count += 1

                    # Add to rolling windows
                    self.episode_rewards.append(episode_reward)
                    self.episode_lengths.append(episode_length)
                    self.episode_successes.append(1 if success else 0)

                    # Calculate rolling averages
                    avg_reward_100 = np.mean(self.episode_rewards) if self.episode_rewards else 0
                    avg_length_100 = np.mean(self.episode_lengths) if self.episode_lengths else 0
                    success_rate_100 = np.mean(self.episode_successes) * 100 if self.episode_successes else 0

                    # Write to CSV
                    with open(self.log_file, 'a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            self.episode_count,
                            self.num_timesteps,
                            maze_seed,
                            f"{episode_reward:.2f}",
                            episode_length,
                            1 if success else 0,
                            f"{avg_reward_100:.2f}",
                            f"{avg_length_100:.1f}",
                            f"{success_rate_100:.1f}",
                            len(self.unique_mazes)
                        ])

                    # Reset environment tracking
                    self.env_episode_rewards[i] = 0
                    self.env_episode_lengths[i] = 0

        # Update progress bar
        if self.pbar:
            self.pbar.update(self.num_timesteps - self.pbar.n)
            remaining = self.total_timesteps - self.num_timesteps
            success_rate = (self.success_count / self.episode_count * 100) if self.episode_count > 0 else 0
            self.pbar.set_postfix({
                "Steps Left": f"{remaining:,}",
                "Mazes": self.episode_count,
                "Success": f"{success_rate:.1f}%",
                "Unique": len(self.unique_mazes)
            })
        return True

    def _on_training_end(self):
        if self.pbar:
            self.pbar.close()
        print(f"\n📊 Training log saved to: {self.log_file}")

        # Print verification summary
        if self.logged_seeds:
            print(f"\n✓ Seed Verification (first 10 logged seeds):")
            for ep_num, seed in self.logged_seeds[:10]:
                print(f"   Episode {ep_num}: seed={seed}")

# --- TRAINING METRICS REPORT GENERATOR ---
class TrainingMetricsReport:
    """Generate comprehensive training metrics report with visualizations"""

    def __init__(self, log_file, model_name="Model", seed_type="PRNG", report_dir="training_reports"):
        self.log_file = log_file
        self.model_name = model_name
        self.seed_type = seed_type
        self.df = None
        self.report_dir = report_dir

        # Create reports directory if it doesn't exist
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir)

    def load_data(self):
        """Load training log CSV file"""
        try:
            self.df = pd.read_csv(self.log_file, comment='#')
            print(f"✅ Loaded training data: {len(self.df)} episodes")
            return True
        except Exception as e:
            print(f"❌ Error loading log file: {e}")
            return False

    def plot_training_reward(self):
        """Plot Training Reward over Episodes"""
        if self.df is None:
            return

        plt.figure(figsize=(14, 6))

        # Raw reward per episode
        plt.subplot(1, 2, 1)
        plt.plot(self.df['episode'], self.df['reward'], 'b-', alpha=0.6, linewidth=0.8, label='Episode Reward')
        plt.plot(self.df['episode'], self.df['avg_reward_100'], 'r-', linewidth=2, label='100-Episode Moving Average')
        plt.xlabel('Episode', fontsize=11, fontweight='bold')
        plt.ylabel('Cumulative Reward', fontsize=11, fontweight='bold')
        plt.title(f'Training Reward over Episodes ({self.seed_type})', fontsize=12, fontweight='bold')
        plt.legend(loc='best', fontsize=10)
        plt.grid(True, alpha=0.3)

        # Zoomed view of moving average
        plt.subplot(1, 2, 2)
        plt.plot(self.df['episode'], self.df['avg_reward_100'], 'r-', linewidth=2)
        plt.fill_between(self.df['episode'], self.df['avg_reward_100'], alpha=0.3, color='red')
        plt.xlabel('Episode', fontsize=11, fontweight='bold')
        plt.ylabel('100-Episode Avg Reward', fontsize=11, fontweight='bold')
        plt.title(f'Smoothed Training Reward ({self.seed_type})', fontsize=12, fontweight='bold')
        plt.grid(True, alpha=0.3)

        plt.tight_layout()
        filename = os.path.join(self.report_dir, f'training_reward_{self.seed_type.lower()}.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"✅ Saved: {filename}")
        plt.close()

    def plot_success_rate(self):
        """Plot Success Rate % over Episodes"""
        if self.df is None:
            return

        plt.figure(figsize=(14, 6))

        # Raw success rate per episode
        plt.subplot(1, 2, 1)
        success_pct = self.df['success'] * 100  # Convert to percentage (0 or 100)
        plt.scatter(self.df['episode'], success_pct, c=success_pct, cmap='RdYlGn', s=20, alpha=0.6, label='Episode Result')
        plt.plot(self.df['episode'], self.df['success_rate_100'], 'g-', linewidth=2.5, label='100-Episode Success Rate %')
        plt.xlabel('Episode', fontsize=11, fontweight='bold')
        plt.ylabel('Success Rate (%)', fontsize=11, fontweight='bold')
        plt.title(f'Success Rate % over Episodes ({self.seed_type})', fontsize=12, fontweight='bold')
        plt.ylim(-5, 105)
        plt.legend(loc='best', fontsize=10)
        plt.grid(True, alpha=0.3)

        # Zoomed view of moving average
        plt.subplot(1, 2, 2)
        plt.plot(self.df['episode'], self.df['success_rate_100'], 'g-', linewidth=2.5)
        plt.fill_between(self.df['episode'], self.df['success_rate_100'], alpha=0.3, color='green')
        plt.xlabel('Episode', fontsize=11, fontweight='bold')
        plt.ylabel('Success Rate (%)', fontsize=11, fontweight='bold')
        plt.title(f'Smoothed Success Rate ({self.seed_type})', fontsize=12, fontweight='bold')
        plt.ylim(-5, 105)
        plt.grid(True, alpha=0.3)

        plt.tight_layout()
        filename = os.path.join(self.report_dir, f'success_rate_{self.seed_type.lower()}.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"✅ Saved: {filename}")
        plt.close()

    def plot_combined_metrics(self):
        """Plot both metrics side by side for comparison"""
        if self.df is None:
            return

        fig, axes = plt.subplots(2, 1, figsize=(14, 10))

        # Training Reward
        axes[0].plot(self.df['episode'], self.df['reward'], 'b-', alpha=0.4, linewidth=0.8, label='Per-Episode Reward')
        axes[0].plot(self.df['episode'], self.df['avg_reward_100'], 'r-', linewidth=2.5, label='100-Episode Moving Average')
        axes[0].set_ylabel('Cumulative Reward', fontsize=11, fontweight='bold')
        axes[0].set_title(f'Agent Training Metrics - {self.seed_type}', fontsize=13, fontweight='bold')
        axes[0].legend(loc='best', fontsize=10)
        axes[0].grid(True, alpha=0.3)

        # Success Rate
        success_pct = self.df['success'] * 100
        axes[1].scatter(self.df['episode'], success_pct, c=success_pct, cmap='RdYlGn', s=15, alpha=0.5, label='Episode Result')
        axes[1].plot(self.df['episode'], self.df['success_rate_100'], 'g-', linewidth=2.5, label='Success Rate %')
        axes[1].set_xlabel('Episode', fontsize=11, fontweight='bold')
        axes[1].set_ylabel('Success Rate (%)', fontsize=11, fontweight='bold')
        axes[1].set_ylim(-5, 105)
        axes[1].legend(loc='best', fontsize=10)
        axes[1].grid(True, alpha=0.3)

        plt.tight_layout()
        filename = os.path.join(self.report_dir, f'combined_metrics_{self.seed_type.lower()}.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"✅ Saved: {filename}")
        plt.close()

    def generate_summary_report(self, eval_mean=None, eval_std=None, training_duration=None):
        """Generate HTML summary report"""
        if self.df is None:
            return

        # Calculate statistics
        final_sr = self.df['success_rate_100'].iloc[-1] if len(self.df) > 0 else 0
        max_sr = self.df['success_rate_100'].max()
        avg_reward = self.df['avg_reward_100'].mean()
        final_reward = self.df['avg_reward_100'].iloc[-1] if len(self.df) > 0 else 0
        max_reward = self.df['reward'].max()

        total_episodes = len(self.df)
        successes = int(self.df['success'].sum())
        failures = total_episodes - successes

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>A2C Agent Training Metrics Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #e67e22; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; border-left: 5px solid #e67e22; padding-left: 10px; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }}
        .metric-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }}
        .metric-card.success {{ background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }}
        .metric-card.reward {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }}
        .metric-card.episodes {{ background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }}
        .metric-value {{ font-size: 28px; font-weight: bold; margin: 10px 0; }}
        .metric-label {{ font-size: 12px; text-transform: uppercase; opacity: 0.9; }}
        .chart-container {{ margin: 30px 0; text-align: center; }}
        .chart-container img {{ max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .summary-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        .summary-table th, .summary-table td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        .summary-table th {{ background-color: #e67e22; color: white; font-weight: bold; }}
        .summary-table tr:hover {{ background-color: #f9f9f9; }}
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #7f8c8d; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 A2C Agent Training Metrics Report</h1>

        <h2>Model Configuration</h2>
        <table class="summary-table">
            <tr><th>Parameter</th><th>Value</th></tr>
            <tr><td>Algorithm</td><td>A2C (Advantage Actor-Critic)</td></tr>
            <tr><td>Model Name</td><td>{self.model_name}</td></tr>
            <tr><td>Seed Type</td><td>{self.seed_type}</td></tr>
            <tr><td>Total Episodes</td><td>{total_episodes:,}</td></tr>
            <tr><td>Training Log</td><td>{self.log_file}</td></tr>
        </table>

        <h2>Performance Metrics</h2>
        <div class="metrics-grid">
            <div class="metric-card success">
                <div class="metric-label">Final Success Rate</div>
                <div class="metric-value">{final_sr:.1f}%</div>
            </div>
            <div class="metric-card success">
                <div class="metric-label">Peak Success Rate</div>
                <div class="metric-value">{max_sr:.1f}%</div>
            </div>
            <div class="metric-card reward">
                <div class="metric-label">Final Avg Reward</div>
                <div class="metric-value">{final_reward:.2f}</div>
            </div>
            <div class="metric-card reward">
                <div class="metric-label">Peak Single Reward</div>
                <div class="metric-value">{max_reward:.2f}</div>
            </div>
            <div class="metric-card episodes">
                <div class="metric-label">Total Successes</div>
                <div class="metric-value">{successes}/{total_episodes}</div>
            </div>
            <div class="metric-card episodes">
                <div class="metric-label">Success Rate</div>
                <div class="metric-value">{successes/total_episodes*100:.1f}%</div>
            </div>
        </div>

        <h2>Training Reward over Episodes</h2>
        <div class="chart-container">
            <img src="training_reward_{self.seed_type.lower()}.png" alt="Training Reward Chart">
            <p><em>Showing per-episode cumulative rewards and 100-episode moving average</em></p>
        </div>

        <h2>Success Rate % over Episodes</h2>
        <div class="chart-container">
            <img src="success_rate_{self.seed_type.lower()}.png" alt="Success Rate Chart">
            <p><em>Showing per-episode results (green=success, red=failure) and 100-episode rolling success rate</em></p>
        </div>

        <h2>Combined Metrics Dashboard</h2>
        <div class="chart-container">
            <img src="combined_metrics_{self.seed_type.lower()}.png" alt="Combined Metrics">
            <p><em>Overview of both training reward and success rate progression</em></p>
        </div>

        <h2>Learning Summary</h2>
        <table class="summary-table">
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Episodes with Success</td><td>{successes}</td></tr>
            <tr><td>Episodes with Failure</td><td>{failures}</td></tr>
            <tr><td>Overall Success Rate</td><td>{successes/total_episodes*100:.2f}%</td></tr>
            <tr><td>Average Reward (100-ep avg)</td><td>{avg_reward:.2f}</td></tr>
            <tr><td>Final Average Reward</td><td>{final_reward:.2f}</td></tr>
            <tr><td>Peak Success Rate</td><td>{max_sr:.1f}%</td></tr>
        </table>

        {'<h2>Evaluation Results</h2>' if eval_mean is not None else ''}
        {'<table class="summary-table"><tr><th>Metric</th><th>Value</th></tr>' if eval_mean is not None else ''}
        {'<tr><td>Evaluation Mean Reward</td><td>' + f'{eval_mean:.2f}' + '</td></tr>' if eval_mean is not None else ''}
        {'<tr><td>Evaluation Std Dev</td><td>' + f'{eval_std:.2f}' + '</td></tr></table>' if eval_mean is not None else ''}

        {'<h2>Training Duration</h2>' if training_duration is not None else ''}
        {'<p>Total Training Time: ' + f'{training_duration:.2f} minutes' + '</p>' if training_duration is not None else ''}

        <div class="footer">
            <p>Report generated on {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>This report summarizes the training performance of the A2C agent on {'PRNG' if 'PRNG' in self.seed_type else 'QRNG'}-generated mazes.</p>
        </div>
    </div>
</body>
</html>
"""

        filename = os.path.join(self.report_dir, f'training_report_{self.seed_type.lower()}.html')
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ Saved: {filename}")

    def generate_all_reports(self, eval_mean=None, eval_std=None, training_duration=None):
        """Generate all reports and visualizations"""
        if not self.load_data():
            return False

        print(f"\n📊 Generating training metrics report for {self.seed_type}...")
        self.plot_training_reward()
        self.plot_success_rate()
        self.plot_combined_metrics()
        self.generate_summary_report(eval_mean, eval_std, training_duration)

        print(f"✅ All reports generated in '{self.report_dir}' directory")
        return True

# --- MAIN ---
if __name__ == "__main__":
    # ===== RUN NUMBER =====
    if len(sys.argv) > 1:
        RUN_NUMBER = int(sys.argv[1])
    else:
        print("Usage: python3 train_qrng.py <run_number>")
        print("Example: python3 train_qrng.py 1")
        sys.exit(1)

    # ===== PATH SETUP =====
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    A2C_DIR = os.path.dirname(SCRIPT_DIR)              # a2c/
    PROJECT_ROOT = os.path.dirname(A2C_DIR)             # CS-Thesis-Model-Training/

    SEED_CSV_PATH = os.path.join(PROJECT_ROOT, "seeds", "qrng_seeds.csv")
    MODEL_SAVE_PATH = os.path.join(A2C_DIR, "models", f"run_{RUN_NUMBER}", "A2C_QRNG")
    LOG_FILE = os.path.join(A2C_DIR, "outputs", "training_logs", f"log_{RUN_NUMBER}", "training_log_qrng.csv")
    REPORT_DIR = os.path.join(A2C_DIR, "outputs", "training_reports", f"report_{RUN_NUMBER}")

    # Create output directories
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    os.makedirs(REPORT_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)

    # CHECK GPU
    if torch.cuda.is_available():
        print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
        device_target = "cuda"
    else:
        print("⚠️ GPU NOT DETECTED")
        device_target = "cpu"

    # MAXIMIZE HARDWARE
    NUM_PARALLEL_ENVS = 12
    TOTAL_TIMESTEPS = 10_000_000
    MODEL_NAME = f"A2C_QRNG_run_{RUN_NUMBER}"

    print(f"--- Starting A2C Training ---")
    print(f"Algorithm: A2C (Advantage Actor-Critic)")
    print(f"Vision: 8 Rays (High Def)")
    print(f"Movement: 4 Directions (Valid)")
    print(f"Cores: {NUM_PARALLEL_ENVS} | GPU: {device_target}")
    print(f"Seed Source: {SEED_CSV_PATH}")
    print(f"✨ UNIQUE MAZES: Each environment gets unique/offset maze in parallel")

    def make_env(env_id=0):
        """Factory function: Each parallel env gets unique offset seed"""
        env = LidarMazeEnv(size=20, seed_type="PRNG", max_steps=500, seed_csv_path=SEED_CSV_PATH, env_id=env_id)
        return Monitor(env)

    env = SubprocVecEnv([lambda env_id=i: make_env(env_id) for i in range(NUM_PARALLEL_ENVS)])
    env = VecFrameStack(env, n_stack=4)

    model = A2C("MlpPolicy", env, verbose=0, device=device_target,
                learning_rate=3e-4,
                n_steps=5,
                gamma=0.99,
                gae_lambda=1.0,
                ent_coef=0.01,
                vf_coef=0.5,
                max_grad_norm=0.5,
                use_rms_prop=False,
                normalize_advantage=False,
                policy_kwargs=dict(net_arch=dict(pi=[256, 256], vf=[256, 256])))

    start_time = time.time()
    progress_callback = ProgressBarCallback(TOTAL_TIMESTEPS, log_file=LOG_FILE, seed_csv_path=SEED_CSV_PATH)
    model.learn(total_timesteps=TOTAL_TIMESTEPS, callback=progress_callback)
    duration = time.time() - start_time

    model.save(MODEL_SAVE_PATH)
    print(f"\n✅ Training Complete in {duration/60:.2f} minutes.")
    print(f"📊 Total Mazes Encountered: {progress_callback.episode_count}")
    print(f"🏆 Successes: {progress_callback.success_count} | ❌ Failures: {progress_callback.failure_count}")
    success_rate = (progress_callback.success_count / progress_callback.episode_count * 100) if progress_callback.episode_count > 0 else 0
    print(f"📈 Success Rate: {success_rate:.1f}%")
    print(f"📈 Average Steps per Maze: {TOTAL_TIMESTEPS / progress_callback.episode_count:.1f}")

    # EVALUATION
    print("\n--- RUNNING EVALUATION ---")
    eval_env = DummyVecEnv([lambda env_id=0: Monitor(LidarMazeEnv(size=20, seed_type="PRNG", max_steps=500, seed_csv_path=SEED_CSV_PATH, env_id=env_id))])
    eval_env = VecFrameStack(eval_env, n_stack=4)
    mean_reward, std_reward = evaluate_policy(model, eval_env, n_eval_episodes=200, deterministic=True)

    print(f"Final Score: {mean_reward:.2f} (+/- {std_reward:.2f})")

    # Calculate consistency metrics
    if std_reward < 30 and mean_reward > 70:
        print("🏆 EXCELLENT: High score with low variance - proper generalization achieved!")
    elif mean_reward > 50:
        print("✅ GOOD: Decent performance but high variance - partial generalization")
    else:
        print("❌ POOR: Low score - needs more training or hyperparameter tuning")

    # --- GENERATE TRAINING METRICS REPORT ---
    print("\n--- GENERATING TRAINING METRICS REPORT ---")

    seed_type = "QRNG"

    report_generator = TrainingMetricsReport(
        log_file=progress_callback.log_file,
        model_name=MODEL_NAME,
        seed_type=seed_type,
        report_dir=REPORT_DIR
    )

    report_generator.generate_all_reports(
        eval_mean=mean_reward,
        eval_std=std_reward,
        training_duration=duration/60
    )

    print(f"\n✅ Training complete and report generated!")
    print(f"📁 Open '{REPORT_DIR}/training_report_{seed_type.lower()}.html' to view the full report")
