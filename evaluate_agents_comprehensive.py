"""
Comprehensive Agent Evaluation Script - Train 19 (Frame Stacking)
Evaluates both PRNG and QRNG trained agents on novel mazes with:
- Success Rate % (SR)
- Reward (navigation quality)
- Steps Taken (path efficiency)
- Generalization Gap (SR_intra - SR_cross)
"""

import numpy as np
import gymnasium as gym
from gymnasium import spaces
import random
import pandas as pd
import os
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecFrameStack
from datetime import datetime


# --- MAZE GENERATOR (IDENTICAL TO TRAINING) ---
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


# --- EVALUATION ENVIRONMENT (DETERMINISTIC) ---
class LidarMazeEnvEval(gym.Env):
    def __init__(self, size=20, seed_type="PRNG", max_steps=500, seed_list=None, seed_offset=0):
        super(LidarMazeEnvEval, self).__init__()
        self.size = size
        self.generator = MazeGenerator(size, seed_type)
        self.maze = None
        self.agent_pos = None
        self.target_pos = None
        self.max_steps = max_steps
        self.current_step = 0
        self.current_dist = 0
        self.visited_cells = set()
        self.current_maze_seed = None
        
        self.seeds = seed_list if seed_list else []
        self.seed_index = seed_offset  # Start from offset (e.g., 40,000 for unseen mazes)
        
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(low=-1, high=1, shape=(10,), dtype=np.float32)

    def _get_manhattan_distance(self, y, x):
        return abs(self.target_pos[0] - y) + abs(self.target_pos[1] - x)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        if self.seeds:
            self.current_maze_seed = self.seeds[self.seed_index % len(self.seeds)]
            self.seed_index += 1
        else:
            self.current_maze_seed = random.randint(0, 2**31 - 1)
        
        self.maze = self.generator.generate(seed=self.current_maze_seed)
        self.agent_pos = [1, 1]
        self.target_pos = [self.size-2, self.size-2]
        self.current_step = 0
        self.visited_cells = set()
        self.visited_cells.add((1, 1))
        self.current_dist = self._get_manhattan_distance(self.agent_pos[0], self.agent_pos[1])
        return self._get_obs(), {}

    def _get_lidar(self):
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
        moves = {0: (-1, 0), 1: (0, 1), 2: (1, 0), 3: (0, -1)}
        dy, dx = moves[action]
        
        old_dist = self.current_dist
        new_y = self.agent_pos[0] + dy
        new_x = self.agent_pos[1] + dx
        
        reward = -0.005

        if not (0 <= new_x < self.size and 0 <= new_y < self.size) or self.maze[new_y, new_x] == 1:
            reward = -0.75
            terminated = False
        else:
            self.agent_pos = [new_y, new_x]
            new_dist = self._get_manhattan_distance(new_y, new_x)
            self.current_dist = new_dist
            
            cell = (new_y, new_x)
            is_new_cell = cell not in self.visited_cells
            if is_new_cell:
                self.visited_cells.add(cell)
            
            progress = old_dist - new_dist
            
            if progress > 0:
                reward += 0.5 * progress
                if is_new_cell:
                    reward += 2.0
                else:
                    reward += 0.2
            elif is_new_cell:
                reward += 0.3
            
            if self.agent_pos == self.target_pos:
                reward += 250
                terminated = True
            else:
                terminated = False

        if self.current_step >= self.max_steps:
            truncated = True
            if not terminated: 
                reward += -7
        else:
            truncated = False
        
        info = {
            'goal_reached': self.agent_pos == self.target_pos,
            'maze_seed': self.current_maze_seed,
            'steps': self.current_step
        }
        
        return self._get_obs(), reward, terminated, truncated, info


# --- EVALUATION RUNNER ---
class EvaluationRunner:
    def __init__(self, prng_model_path, qrng_model_path, prng_seeds_csv, qrng_seeds_csv):
        """Load models and seed lists"""
        print("\n" + "="*70)
        print("LOADING MODELS AND SEEDS")
        print("="*70)
        
        try:
            self.prng_model = PPO.load(prng_model_path)
            print(f"✅ Loaded PRNG model")
        except Exception as e:
            print(f"❌ Error loading PRNG model: {e}")
            raise
        
        try:
            self.qrng_model = PPO.load(qrng_model_path)
            print(f"✅ Loaded QRNG model")
        except Exception as e:
            print(f"❌ Error loading QRNG model: {e}")
            raise
        
        self.prng_seeds = self._load_seeds(prng_seeds_csv)
        self.qrng_seeds = self._load_seeds(qrng_seeds_csv)
        
        print(f"✅ Loaded {len(self.prng_seeds)} PRNG seeds total")
        print(f"✅ Loaded {len(self.qrng_seeds)} QRNG seeds total")
        print(f"\n📌 EVALUATION ON UNSEEN MAZES:")
        print(f"   Starting from seed index 40,000 (all novel/unseen)")
        
    def _load_seeds(self, csv_path):
        """Load seeds from CSV file"""
        if not os.path.exists(csv_path):
            print(f"❌ File not found: {csv_path}")
            return []
        try:
            df = pd.read_csv(csv_path)
            return df['number'].tolist()
        except Exception as e:
            print(f"❌ Error loading {csv_path}: {e}")
            return []
    
    def evaluate_agent(self, model, seed_list, seed_type_name, num_episodes=100, seed_offset=40000):
        """Evaluate a single agent on given seed list, offset by seed_offset (default: 40,000 for unseen mazes)"""
        seed_type = "PRNG" if "PRNG" in seed_type_name else "QRNG"
        
        successes = []
        rewards = []
        steps_taken = []
        
        print(f"\n  Evaluating on {num_episodes} novel {seed_type_name} mazes (offset {seed_offset:,})...")
        
        for episode in range(num_episodes):
            # Create environment and wrap with frame stacking, offset for unseen mazes
            # Pass seed_offset + episode so each episode gets a unique seed
            env = LidarMazeEnvEval(seed_type=seed_type, seed_list=seed_list, seed_offset=seed_offset + episode)
            env = DummyVecEnv([lambda e=env: e])
            env = VecFrameStack(env, n_stack=4)
            
            obs = env.reset()  # VecEnv.reset() returns only obs, not (obs, info)
            
            episode_reward = 0
            episode_steps = 0
            done = False
            episode_success = False
            
            # Run episode to completion
            while not done:
                action, _ = model.predict(obs, deterministic=True)
                obs, reward, dones, info = env.step(action)
                episode_reward += float(reward[0])
                episode_steps += 1
                done = bool(dones[0])
                
                # Check goal reached
                try:
                    if isinstance(info, (list, tuple)) and len(info) > 0:
                        if isinstance(info[0], dict) and info[0].get('goal_reached'):
                            episode_success = True
                except:
                    pass
            
            env.close()
            
            successes.append(1 if episode_success else 0)
            rewards.append(episode_reward)
            steps_taken.append(episode_steps)
            
            if (episode + 1) % 10 == 0:
                print(f"    Completed {episode+1}/{num_episodes}")
        
        success_rate = np.mean(successes) * 100
        avg_reward = np.mean(rewards)
        std_reward = np.std(rewards)
        avg_steps = np.mean(steps_taken)
        
        return {
            'success_rate': success_rate,
            'avg_reward': avg_reward,
            'std_reward': std_reward,
            'avg_steps': avg_steps,
            'successes': successes,
            'rewards': rewards,
            'steps': steps_taken
        }
    
    def run_full_evaluation(self, num_episodes=100, seed_offset=40000):
        """Run all 4 evaluation conditions on unseen mazes"""
        print("\n" + "="*70)
        print("COMPREHENSIVE AGENT EVALUATION ON UNSEEN MAZES - Train 19")
        print("="*70)
        
        results = {}
        
        print("\n[1/4] PRNG Model on Novel PRNG Mazes (Intra-Distribution)")
        results['prng_on_prng'] = self.evaluate_agent(
            self.prng_model, self.prng_seeds, "PRNG_Intra", num_episodes, seed_offset=seed_offset
        )
        
        print("\n[2/4] PRNG Model on Novel QRNG Mazes (Cross-Distribution)")
        results['prng_on_qrng'] = self.evaluate_agent(
            self.prng_model, self.qrng_seeds, "QRNG_Cross", num_episodes, seed_offset=seed_offset
        )
        
        print("\n[3/4] QRNG Model on Novel QRNG Mazes (Intra-Distribution)")
        results['qrng_on_qrng'] = self.evaluate_agent(
            self.qrng_model, self.qrng_seeds, "QRNG_Intra", num_episodes, seed_offset=seed_offset
        )
        
        print("\n[4/4] QRNG Model on Novel PRNG Mazes (Cross-Distribution)")
        results['qrng_on_prng'] = self.evaluate_agent(
            self.qrng_model, self.prng_seeds, "PRNG_Cross", num_episodes, seed_offset=seed_offset
        )
        
        return results
    
    def compute_generalization_gap(self, results):
        """Compute generalization gap for each agent"""
        prng_intra = results['prng_on_prng']['success_rate']
        prng_cross = results['prng_on_qrng']['success_rate']
        prng_gap = prng_intra - prng_cross
        
        qrng_intra = results['qrng_on_qrng']['success_rate']
        qrng_cross = results['qrng_on_prng']['success_rate']
        qrng_gap = qrng_intra - qrng_cross
        
        return {
            'prng_gap': prng_gap,
            'qrng_gap': qrng_gap
        }
    
    def generate_report(self, results, output_file="evaluation_report.html"):
        """Generate HTML report"""
        gaps = self.compute_generalization_gap(results)
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Agent Evaluation Report - Train 19</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; border-left: 5px solid #3498db; padding-left: 10px; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin: 20px 0; }}
        .metric-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; }}
        .metric-card.prng {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }}
        .metric-card.qrng {{ background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }}
        .metric-card.gap {{ background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }}
        .metric-value {{ font-size: 32px; font-weight: bold; margin: 10px 0; }}
        .metric-label {{ font-size: 11px; text-transform: uppercase; opacity: 0.9; }}
        .metric-sublabel {{ font-size: 10px; margin-top: 5px; opacity: 0.8; }}
        .summary-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        .summary-table th, .summary-table td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        .summary-table th {{ background-color: #3498db; color: white; font-weight: bold; }}
        .summary-table tr:hover {{ background-color: #f9f9f9; }}
        .comparison-section {{ margin: 30px 0; padding: 20px; background-color: #ecf0f1; border-radius: 8px; }}
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #7f8c8d; font-size: 12px; }}
        .highlight {{ background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #ffc107; }}
        .unseen-badge {{ background-color: #28a745; color: white; padding: 8px 12px; border-radius: 4px; display: inline-block; margin: 10px 0; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Comprehensive Agent Evaluation Report - Train 19 (UNSEEN MAZES)</h1>
        
        <div class="unseen-badge">✓ EVALUATED ON NOVEL MAZES (Seed Offset: 40,000+)</div>
        
        <p>Trained on both PRNG and QRNG randomness sources. Evaluated on completely novel mazes from both distributions (seeds 40,000 onwards).</p>
        
        <h2>Key Performance Metrics</h2>
        <div class="metrics-grid">
            <div class="metric-card prng">
                <div class="metric-label">PRNG Model - Intra SR %</div>
                <div class="metric-value">{results['prng_on_prng']['success_rate']:.1f}%</div>
                <div class="metric-sublabel">(Novel PRNG mazes)</div>
            </div>
            <div class="metric-card prng">
                <div class="metric-label">PRNG Model - Cross SR %</div>
                <div class="metric-value">{results['prng_on_qrng']['success_rate']:.1f}%</div>
                <div class="metric-sublabel">(Novel QRNG mazes)</div>
            </div>
            <div class="metric-card gap">
                <div class="metric-label">PRNG Gen. Gap</div>
                <div class="metric-value">{gaps['prng_gap']:.1f}pp</div>
                <div class="metric-sublabel">Intra - Cross</div>
            </div>
            <div class="metric-card qrng">
                <div class="metric-label">QRNG Model - Intra SR %</div>
                <div class="metric-value">{results['qrng_on_qrng']['success_rate']:.1f}%</div>
                <div class="metric-sublabel">(Novel QRNG mazes)</div>
            </div>
            <div class="metric-card qrng">
                <div class="metric-label">QRNG Model - Cross SR %</div>
                <div class="metric-value">{results['qrng_on_prng']['success_rate']:.1f}%</div>
                <div class="metric-sublabel">(Novel PRNG mazes)</div>
            </div>
            <div class="metric-card gap">
                <div class="metric-label">QRNG Gen. Gap</div>
                <div class="metric-value">{gaps['qrng_gap']:.1f}pp</div>
                <div class="metric-sublabel">Intra - Cross</div>
            </div>
        </div>
        
        <h2>Detailed Performance Comparison</h2>
        <table class="summary-table">
            <tr>
                <th>Agent</th>
                <th>Evaluation Set</th>
                <th>Success Rate %</th>
                <th>Avg Reward</th>
                <th>Std Dev</th>
                <th>Avg Steps</th>
                <th>Type</th>
            </tr>
            <tr>
                <td><strong>PRNG Model</strong></td>
                <td>Novel PRNG Mazes</td>
                <td>{results['prng_on_prng']['success_rate']:.2f}%</td>
                <td>{results['prng_on_prng']['avg_reward']:.2f}</td>
                <td>{results['prng_on_prng']['std_reward']:.2f}</td>
                <td>{results['prng_on_prng']['avg_steps']:.1f}</td>
                <td>Intra ✓</td>
            </tr>
            <tr>
                <td><strong>PRNG Model</strong></td>
                <td>Novel QRNG Mazes</td>
                <td>{results['prng_on_qrng']['success_rate']:.2f}%</td>
                <td>{results['prng_on_qrng']['avg_reward']:.2f}</td>
                <td>{results['prng_on_qrng']['std_reward']:.2f}</td>
                <td>{results['prng_on_qrng']['avg_steps']:.1f}</td>
                <td>Cross</td>
            </tr>
            <tr>
                <td><strong>QRNG Model</strong></td>
                <td>Novel QRNG Mazes</td>
                <td>{results['qrng_on_qrng']['success_rate']:.2f}%</td>
                <td>{results['qrng_on_qrng']['avg_reward']:.2f}</td>
                <td>{results['qrng_on_qrng']['std_reward']:.2f}</td>
                <td>{results['qrng_on_qrng']['avg_steps']:.1f}</td>
                <td>Intra ✓</td>
            </tr>
            <tr>
                <td><strong>QRNG Model</strong></td>
                <td>Novel PRNG Mazes</td>
                <td>{results['qrng_on_prng']['success_rate']:.2f}%</td>
                <td>{results['qrng_on_prng']['avg_reward']:.2f}</td>
                <td>{results['qrng_on_prng']['std_reward']:.2f}</td>
                <td>{results['qrng_on_prng']['avg_steps']:.1f}</td>
                <td>Cross</td>
            </tr>
        </table>
        
        <h2>Generalization Gap Analysis</h2>
        <div class="comparison-section">
            <p><strong>Generalization Gap = SR_intra - SR_cross</strong><br>Measures performance drop on unfamiliar maze distributions. Lower = Better generalization.</p>
            
            <table class="summary-table">
                <tr>
                    <th>Agent</th>
                    <th>Intra SR %</th>
                    <th>Cross SR %</th>
                    <th>Gap (pp)</th>
                    <th>Interpretation</th>
                </tr>
                <tr>
                    <td><strong>PRNG Agent</strong></td>
                    <td>{results['prng_on_prng']['success_rate']:.2f}%</td>
                    <td>{results['prng_on_qrng']['success_rate']:.2f}%</td>
                    <td>{gaps['prng_gap']:.2f}pp</td>
                    <td>{"High overfitting" if gaps['prng_gap'] > 20 else "Moderate fit" if gaps['prng_gap'] > 10 else "Good generalization"}</td>
                </tr>
                <tr>
                    <td><strong>QRNG Agent</strong></td>
                    <td>{results['qrng_on_qrng']['success_rate']:.2f}%</td>
                    <td>{results['qrng_on_prng']['success_rate']:.2f}%</td>
                    <td>{gaps['qrng_gap']:.2f}pp</td>
                    <td>{"High overfitting" if gaps['qrng_gap'] > 20 else "Moderate fit" if gaps['qrng_gap'] > 10 else "Good generalization"}</td>
                </tr>
            </table>
        </div>
        
        <h2>Path Efficiency (Steps Taken)</h2>
        <div class="highlight">
            <p>Lower steps = more efficient pathfinding. Optimal paths for 20×20 maze: 40-50 steps.</p>
            <ul>
                <li><strong>PRNG on PRNG:</strong> {results['prng_on_prng']['avg_steps']:.1f} avg steps</li>
                <li><strong>PRNG on QRNG:</strong> {results['prng_on_qrng']['avg_steps']:.1f} avg steps</li>
                <li><strong>QRNG on QRNG:</strong> {results['qrng_on_qrng']['avg_steps']:.1f} avg steps</li>
                <li><strong>QRNG on PRNG:</strong> {results['qrng_on_prng']['avg_steps']:.1f} avg steps</li>
            </ul>
        </div>
        
        <h2>Key Findings</h2>
        <div class="highlight">
            <ul>
                <li><strong>Best Intra-Distribution SR:</strong> {"PRNG" if results['prng_on_prng']['success_rate'] > results['qrng_on_qrng']['success_rate'] else "QRNG"} @ {max(results['prng_on_prng']['success_rate'], results['qrng_on_qrng']['success_rate']):.1f}%</li>
                <li><strong>Cross-Distribution Winner:</strong> {"PRNG" if results['prng_on_qrng']['success_rate'] > results['qrng_on_prng']['success_rate'] else "QRNG"} on unfamiliar mazes</li>
                <li><strong>Robustness (lower gap better):</strong> {"PRNG" if gaps['prng_gap'] < gaps['qrng_gap'] else "QRNG"} shows less overfitting</li>
                <li><strong>Path Efficiency:</strong> {"PRNG" if results['prng_on_prng']['avg_steps'] < results['qrng_on_qrng']['avg_steps'] else "QRNG"} finds quicker solutions</li>
            </ul>
        </div>
        
        <div class="footer">
            <p>Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Evaluation: 100 episodes × 4 conditions | Seed Offset: 40,000+ (all novel/unseen mazes)</p>
            <p>Frame Stacking: n_stack=4 | Deterministic Policy Evaluation</p>
        </div>
    </div>
</body>
</html>
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"\n✅ Report saved to: {output_file}")
    
    def save_csv_results(self, results, output_file="evaluation_results.csv"):
        """Save detailed results to CSV"""
        rows = []
        
        for condition, data in results.items():
            for i, (sr, reward, steps) in enumerate(zip(
                data['successes'], data['rewards'], data['steps']
            )):
                rows.append({
                    'condition': condition,
                    'episode': i+1,
                    'success': sr,
                    'reward': reward,
                    'steps': steps
                })
        
        df = pd.DataFrame(rows)
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"✅ Detailed results saved to: {output_file}")


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    BASE_DIR = r"c:\Users\Ryce\Downloads\Eval\PPO FINAL EVAL\PPO Main Modified Reward Structure\Clean Training\Clean train 19 (Frame Stacking)"
    
    PRNG_MODEL = os.path.join(BASE_DIR, "PPO_20x20_Manhattan (MAIN) PRNG - 19 UNIQUE MAZES")
    QRNG_MODEL = os.path.join(BASE_DIR, "PPO_20x20_Manhattan (MAIN) QRNG - 19 UNIQUE MAZES")
    
    PRNG_SEEDS = os.path.join(BASE_DIR, "prng_seeds.csv")
    QRNG_SEEDS = os.path.join(BASE_DIR, "qrng_seeds.csv")
    
    print("="*70)
    print("CONFIGURATION CHECK")
    print("="*70)
    for path, name in [(PRNG_MODEL + ".zip", "PRNG model"), 
                       (QRNG_MODEL + ".zip", "QRNG model"),
                       (PRNG_SEEDS, "PRNG seeds"),
                       (QRNG_SEEDS, "QRNG seeds")]:
        status = "✅" if os.path.exists(path) else "❌"
        print(f"{status} {name}")
    
    try:
        evaluator = EvaluationRunner(PRNG_MODEL, QRNG_MODEL, PRNG_SEEDS, QRNG_SEEDS)
        results = evaluator.run_full_evaluation(num_episodes=100, seed_offset=40000)
        
        output_dir = os.path.join(BASE_DIR, "evaluation_results")
        os.makedirs(output_dir, exist_ok=True)
        
        report_path = os.path.join(output_dir, "evaluation_report.html")
        csv_path = os.path.join(output_dir, "evaluation_results.csv")
        
        evaluator.generate_report(results, report_path)
        evaluator.save_csv_results(results, csv_path)
        
        gaps = evaluator.compute_generalization_gap(results)
        print("\n" + "="*70)
        print("EVALUATION SUMMARY (UNSEEN MAZES - OFFSET 40,000+)")
        print("="*70)
        print(f"\n📊 PRNG Agent (Novel Mazes):")
        print(f"   Intra-distribution SR:  {results['prng_on_prng']['success_rate']:.2f}%")
        print(f"   Cross-distribution SR:  {results['prng_on_qrng']['success_rate']:.2f}%")
        print(f"   Generalization Gap:     {gaps['prng_gap']:.2f}pp\n")
        
        print(f"🔷 QRNG Agent (Novel Mazes):")
        print(f"   Intra-distribution SR:  {results['qrng_on_qrng']['success_rate']:.2f}%")
        print(f"   Cross-distribution SR:  {results['qrng_on_prng']['success_rate']:.2f}%")
        print(f"   Generalization Gap:     {gaps['qrng_gap']:.2f}pp\n")
        
        print(f"📁 Results: {output_dir}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
