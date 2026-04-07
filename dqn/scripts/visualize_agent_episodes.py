import numpy as np
import gymnasium as gym
from gymnasium import spaces
import random
import pandas as pd
import os
import argparse
from stable_baselines3 import DQN
from stable_baselines3.common.vec_env import DummyVecEnv, VecFrameStack
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import traceback


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
        self.seed_index = seed_offset
        
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


# --- MAZE VISUALIZATION ---
class MazeVisualizer:
    def __init__(self, maze, cell_size=15, padding=40):
        """
        Initialize visualizer for a maze.
        
        Args:
            maze: 2D numpy array (0=path, 1=wall)
            cell_size: pixels per maze cell
            padding: pixels around maze for info/labels
        """
        self.maze = maze
        self.size = maze.shape[0]
        self.cell_size = cell_size
        self.padding = padding
        
        # Colors
        self.COLOR_WALL = (50, 50, 50)
        self.COLOR_PATH = (240, 240, 245)
        self.COLOR_VISITED = (200, 220, 255)
        self.COLOR_TARGET = (50, 200, 50)
        self.COLOR_AGENT = (255, 50, 50)
        self.COLOR_START = (100, 100, 255)
        
        self.canvas_width = self.size * self.cell_size + 2 * self.padding
        self.canvas_height = self.size * self.cell_size + 2 * self.padding + 50

    def render_frame(self, agent_pos, target_pos, visited_cells, step, goal_reached=False, episode_reward=0):
        """
        Render a single frame of the maze with agent, target, and visited cells.
        
        Returns:
            PIL Image
        """
        # Create image
        img = Image.new('RGB', (self.canvas_width, self.canvas_height), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        # Draw maze
        for y in range(self.size):
            for x in range(self.size):
                cell_x = x * self.cell_size + self.padding
                cell_y = y * self.cell_size + self.padding
                
                if self.maze[y, x] == 1:  # Wall
                    color = self.COLOR_WALL
                elif (y, x) in visited_cells and (y, x) != tuple(agent_pos) and (y, x) != tuple(target_pos):
                    color = self.COLOR_VISITED
                else:
                    color = self.COLOR_PATH
                
                draw.rectangle(
                    [cell_x, cell_y, cell_x + self.cell_size - 1, cell_y + self.cell_size - 1],
                    fill=color
                )
        
        # Draw target (goal)
        target_x = target_pos[1] * self.cell_size + self.padding + self.cell_size // 2
        target_y = target_pos[0] * self.cell_size + self.padding + self.cell_size // 2
        target_radius = self.cell_size // 3
        draw.ellipse(
            [target_x - target_radius, target_y - target_radius,
             target_x + target_radius, target_y + target_radius],
            fill=self.COLOR_TARGET
        )
        
        # Draw agent
        agent_x = agent_pos[1] * self.cell_size + self.padding + self.cell_size // 2
        agent_y = agent_pos[0] * self.cell_size + self.padding + self.cell_size // 2
        agent_radius = self.cell_size // 3
        draw.ellipse(
            [agent_x - agent_radius, agent_y - agent_radius,
             agent_x + agent_radius, agent_y + agent_radius],
            fill=self.COLOR_AGENT
        )
        
        # Draw info text
        info_y = self.size * self.cell_size + self.padding + 5
        status = "✓ GOAL REACHED!" if goal_reached else "In Progress"
        status_color = (0, 200, 0) if goal_reached else (200, 100, 0)
        
        draw.text((self.padding, info_y), f"Step: {step:3d} | Reward: {episode_reward:+.1f} | {status}", 
                 fill=status_color, font=None)
        
        return img

    def create_episode_gif(self, frames_data, output_path, duration=100):
        """
        Create a GIF from frames data.
        
        Args:
            frames_data: List of tuples (agent_pos, target_pos, visited_cells, step, goal_reached, reward)
            output_path: Path to save GIF
            duration: Milliseconds per frame
        """
        frames = []
        for agent_pos, target_pos, visited_cells, step, goal_reached, reward in frames_data:
            frame = self.render_frame(agent_pos, target_pos, visited_cells, step, goal_reached, reward)
            frames.append(frame)
        
        if frames:
            frames[0].save(
                output_path,
                save_all=True,
                append_images=frames[1:],
                duration=duration,
                loop=0,
                optimize=False
            )
            return True
        return False


# --- EPISODE RECORDER ---
class EpisodeRecorder:
    def __init__(self, model, seed_list, seed_type, seed_offset=50000):
        """
        Record episodes matching evaluate_agents.py structure.
        
        Args:
            model: Trained DQN model
            seed_list: List of seeds to use
            seed_type: "PRNG" or "QRNG"
            seed_offset: Starting offset for seeds
        """
        self.model = model
        self.seed_list = seed_list
        self.seed_type = seed_type
        self.seed_offset = seed_offset

    def record_episode(self, episode_num):
        """
        Record a single episode with unique seed based on episode number.
        
        Args:
            episode_num: Episode number (0-indexed)
        
        Returns:
            Dict with episode data including frames, success, reward, steps
        """
        # Create environment with offset seed
        env = LidarMazeEnvEval(
            seed_type=self.seed_type,
            seed_list=self.seed_list,
            seed_offset=self.seed_offset + episode_num
        )
        env = DummyVecEnv([lambda e=env: e])
        env = VecFrameStack(env, n_stack=4)
        
        obs = env.reset()
        
        frames_data = []
        episode_reward = 0
        episode_steps = 0
        done = False
        episode_success = False
        maze_seed = None
        
        # Get initial state for visualization
        inner_env = env.envs[0]
        if hasattr(inner_env, 'env'):
            inner_env = inner_env.env
        
        maze = inner_env.maze.copy()
        maze_seed = inner_env.current_maze_seed
        
        # Capture initial frame
        initial_frame_data = (
            inner_env.agent_pos.copy(),
            inner_env.target_pos.copy(),
            set(inner_env.visited_cells),
            0,
            False,
            0
        )
        frames_data.append(initial_frame_data)
        
        # Run episode
        while not done:
            action, _ = self.model.predict(obs, deterministic=True)
            obs, reward, dones, info = env.step(action)
            
            episode_reward += float(reward[0])
            episode_steps += 1
            done = bool(dones[0])
            
            if done:
                try:
                    if isinstance(info, (list, tuple)) and len(info) > 0:
                        if isinstance(info[0], dict) and info[0].get('goal_reached'):
                            episode_success = True
                except:
                    pass
            
            # Always capture frame to include entire trajectory
            frame_data = (
                inner_env.agent_pos.copy(),
                inner_env.target_pos.copy(),
                set(inner_env.visited_cells),
                episode_steps,
                episode_success,
                episode_reward
            )
            frames_data.append(frame_data)
        
        env.close()
        
        return {
            'frames': frames_data,
            'success': episode_success,
            'reward': episode_reward,
            'steps': episode_steps,
            'maze': maze,
            'maze_seed': maze_seed
        }


# --- MAIN VISUALIZER ---
class GifGenerator:
    def __init__(self, prng_model_path, qrng_model_path, prng_seeds_csv, qrng_seeds_csv):
        """Load models and seed lists"""
        print("\n" + "="*70)
        print("LOADING MODELS FOR VISUALIZATION")
        print("="*70)
        
        try:
            self.prng_model = DQN.load(prng_model_path)
            print(f"✅ Loaded PRNG model")
        except Exception as e:
            print(f"❌ Error loading PRNG model: {e}")
            raise
        
        try:
            self.qrng_model = DQN.load(qrng_model_path)
            print(f"✅ Loaded QRNG model")
        except Exception as e:
            print(f"❌ Error loading QRNG model: {e}")
            raise
        
        self.prng_seeds = self._load_seeds(prng_seeds_csv)
        self.qrng_seeds = self._load_seeds(qrng_seeds_csv)
        
        print(f"✅ Loaded {len(self.prng_seeds)} PRNG seeds")
        print(f"✅ Loaded {len(self.qrng_seeds)} QRNG seeds")
    
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
    
    def generate_gifs(self, output_dir, model_name, model, seed_list, seed_type_name, 
                     condition_name, num_episodes=1000, seed_offset=50000):
        """
        Generate GIFs for all episodes in a condition (matching evaluate_agents.py).
        
        Args:
            output_dir: Base output directory
            model_name: Name of model (e.g., "PRNG_Model")
            model: Trained model
            seed_list: Seed list to use
            seed_type_name: Name of seed type
            condition_name: Name of condition (e.g., "IntraDistribution", "CrossDistribution")
            num_episodes: Number of episodes to visualize (default: 1000)
            seed_offset: Seed offset for unseen mazes
        """
        condition_dir = os.path.join(output_dir, f"{model_name}_{condition_name}")
        os.makedirs(condition_dir, exist_ok=True)
        
        seed_type = "PRNG" if "PRNG" in seed_type_name else "QRNG"
        
        print(f"\n[{condition_name}] Generating {num_episodes} GIFs for {model_name}...")
        print(f"   Seed Type: {seed_type_name}")
        print(f"   Offset: {seed_offset:,}")
        
        recorder = EpisodeRecorder(model, seed_list, seed_type, seed_offset)
        
        successes = []
        steps_list = []
        rewards_list = []
        
        for episode_num in range(num_episodes):
            try:
                episode_data = recorder.record_episode(episode_num)
                
                successes.append(episode_data['success'])
                steps_list.append(episode_data['steps'])
                rewards_list.append(episode_data['reward'])
                
                # Create GIF
                visualizer = MazeVisualizer(episode_data['maze'])
                status = "✓SUCCESS" if episode_data['success'] else "FAILED"
                gif_name = f"ep{episode_num+1:04d}_{status}_steps{episode_data['steps']}.gif"
                gif_path = os.path.join(condition_dir, gif_name)
                
                visualizer.create_episode_gif(episode_data['frames'], gif_path, duration=100)
                
                if (episode_num + 1) % 50 == 0:
                    success_rate = (sum(successes) / len(successes) * 100)
                    print(f"   Progress: {episode_num+1}/{num_episodes} | SR: {success_rate:.1f}%")
                
            except Exception as e:
                print(f"   ⚠️  Error in episode {episode_num+1}: {e}")
                traceback.print_exc()
        
        success_rate = (sum(successes) / len(successes) * 100) if successes else 0
        avg_steps = np.mean(steps_list) if steps_list else 0
        avg_reward = np.mean(rewards_list) if rewards_list else 0
        
        print(f"\n   ✅ Generated {len(successes)} GIFs")
        print(f"   📊 Success Rate: {success_rate:.2f}%")
        print(f"   📊 Avg Steps: {avg_steps:.1f}")
        print(f"   📊 Avg Reward: {avg_reward:.2f}")
        
        return condition_dir, len(successes), success_rate, avg_steps, avg_reward

    def generate_all_conditions(self, base_output_dir, num_episodes_per_condition=1000, 
                               seed_offset=50000):
        """
        Generate GIFs for all 4 conditions (matching evaluate_agents.py exactly).
        
        Args:
            base_output_dir: Base output directory
            num_episodes_per_condition: Episodes to generate per condition (default: 1000)
            seed_offset: Seed offset for unseen mazes (default: 50000)
        """
        print("\n" + "="*70)
        print("GENERATING AGENT EPISODE VISUALIZATIONS (GIFs)")
        print("="*70)
        print(f"\n📌 Configuration:")
        print(f"   Episodes per condition: {num_episodes_per_condition:,}")
        print(f"   Total episodes: {num_episodes_per_condition * 4:,}")
        print(f"   Seed offset: {seed_offset:,} (all novel/unseen mazes)")
        
        results = {}
        
        # [1/4] PRNG Model on PRNG Mazes (Intra-Distribution)
        print("\n" + "="*70)
        print("[1/4] PRNG Model on Novel PRNG Mazes (Intra-Distribution)")
        print("="*70)
        dir1, count1, sr1, steps1, reward1 = self.generate_gifs(
            base_output_dir,
            "PRNG_Model",
            self.prng_model,
            self.prng_seeds,
            "PRNG",
            "IntraDistribution",
            num_episodes_per_condition,
            seed_offset
        )
        results['prng_on_prng'] = {'dir': dir1, 'count': count1, 'sr': sr1, 'steps': steps1, 'reward': reward1}
        
        # [2/4] PRNG Model on QRNG Mazes (Cross-Distribution)
        print("\n" + "="*70)
        print("[2/4] PRNG Model on Novel QRNG Mazes (Cross-Distribution)")
        print("="*70)
        dir2, count2, sr2, steps2, reward2 = self.generate_gifs(
            base_output_dir,
            "PRNG_Model",
            self.prng_model,
            self.qrng_seeds,
            "QRNG",
            "CrossDistribution",
            num_episodes_per_condition,
            seed_offset
        )
        results['prng_on_qrng'] = {'dir': dir2, 'count': count2, 'sr': sr2, 'steps': steps2, 'reward': reward2}
        
        # [3/4] QRNG Model on QRNG Mazes (Intra-Distribution)
        print("\n" + "="*70)
        print("[3/4] QRNG Model on Novel QRNG Mazes (Intra-Distribution)")
        print("="*70)
        dir3, count3, sr3, steps3, reward3 = self.generate_gifs(
            base_output_dir,
            "QRNG_Model",
            self.qrng_model,
            self.qrng_seeds,
            "QRNG",
            "IntraDistribution",
            num_episodes_per_condition,
            seed_offset
        )
        results['qrng_on_qrng'] = {'dir': dir3, 'count': count3, 'sr': sr3, 'steps': steps3, 'reward': reward3}
        
        # [4/4] QRNG Model on PRNG Mazes (Cross-Distribution)
        print("\n" + "="*70)
        print("[4/4] QRNG Model on Novel PRNG Mazes (Cross-Distribution)")
        print("="*70)
        dir4, count4, sr4, steps4, reward4 = self.generate_gifs(
            base_output_dir,
            "QRNG_Model",
            self.qrng_model,
            self.prng_seeds,
            "PRNG",
            "CrossDistribution",
            num_episodes_per_condition,
            seed_offset
        )
        results['qrng_on_prng'] = {'dir': dir4, 'count': count4, 'sr': sr4, 'steps': steps4, 'reward': reward4}
        
        print("\n" + "="*70)
        print("GIF GENERATION COMPLETE")
        print("="*70)
        print(f"\n📁 Output Directory: {base_output_dir}")
        print(f"\n📊 Summary:")
        print(f"   PRNG Model → PRNG Mazes (Intra):  {count1:,} GIFs | SR: {sr1:.2f}%")
        print(f"   PRNG Model → QRNG Mazes (Cross):  {count2:,} GIFs | SR: {sr2:.2f}%")
        print(f"   QRNG Model → QRNG Mazes (Intra):  {count3:,} GIFs | SR: {sr3:.2f}%")
        print(f"   QRNG Model → PRNG Mazes (Cross):  {count4:,} GIFs | SR: {sr4:.2f}%")
        print(f"   {'─'*50}")
        print(f"   Total GIFs Generated: {count1 + count2 + count3 + count4:,}")


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    BASE_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))
    MODELS_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "models")
    SEEDS_DIR = os.path.join(BASE_DIR, "seeds")
    
    PRNG_MODEL = os.path.join(MODELS_DIR, "DQN_20x20_Manhattan-PRNG-trial-3")
    QRNG_MODEL = os.path.join(MODELS_DIR, "DQN_20x20_Manhattan-QRNG-trial-3")
    
    PRNG_SEEDS = os.path.join(SEEDS_DIR, "prng_seeds.csv")
    QRNG_SEEDS = os.path.join(SEEDS_DIR, "qrng_seeds.csv")
    
    print("="*70)
    print("GIF VISUALIZATION GENERATOR - Configuration Check")
    print("="*70)
    for path, name in [(PRNG_MODEL + ".zip", "PRNG model"), 
                       (QRNG_MODEL + ".zip", "QRNG model"),
                       (PRNG_SEEDS, "PRNG seeds"),
                       (QRNG_SEEDS, "QRNG seeds")]:
        status = "✅" if os.path.exists(path) else "❌"
        print(f"{status} {name}")
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Generate GIFs of agents traversing ENTIRE evaluation set (all 1000 episodes per condition)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python visualize_agent_episodes.py
  python visualize_agent_episodes.py --episodes 100 --offset 50000
  python visualize_agent_episodes.py --output "C:/my/folder"
        """
    )
    parser.add_argument(
        '--episodes',
        type=int,
        default=1000,
        help='Number of episodes per condition (default: 1000)'
    )
    parser.add_argument(
        '--offset',
        type=int,
        default=50000,
        help='Seed offset for unseen mazes (default: 50000)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output directory (default: dqn/outputs/episode_gifs)'
    )
    
    args = parser.parse_args()
    
    # Set output directory
    if args.output:
        output_dir = args.output
    else:
        output_dir = os.path.join(BASE_DIR, "dqn", "outputs", "episode_gifs")
    
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n📋 Configuration:")
    print(f"   Episodes per condition: {args.episodes:,}")
    print(f"   Total episodes: {args.episodes * 4:,}")
    print(f"   Seed offset: {args.offset:,}")
    print(f"   Output: {output_dir}")
    
    try:
        generator = GifGenerator(PRNG_MODEL, QRNG_MODEL, PRNG_SEEDS, QRNG_SEEDS)
        generator.generate_all_conditions(
            output_dir,
            num_episodes_per_condition=args.episodes,
            seed_offset=args.offset
        )
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        traceback.print_exc()
