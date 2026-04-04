"""
Script to create time-series graphs comparing all trials for PRNG and QRNG models.
Creates 4 subplots: PRNG Success Rate, QRNG Success Rate, PRNG Rewards, QRNG Rewards.
Each subplot shows individual trials + average line.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# ============================================================================
# CONFIGURATION - Modify these to change directories or model type
# ============================================================================

# Base output directory for the model
MODEL_OUTPUT_DIR = Path(__file__).parent.parent / "outputs"

# Training log directories (relative to MODEL_OUTPUT_DIR)
TRAINING_LOG_DIR = MODEL_OUTPUT_DIR / "training_logs"
TRIAL_DIRS = ["log_1", "log_2", "log_3"]

# Output filename for the plots
OUTPUT_FILENAME = "training_comparison.png"

# Colors for each trial (distinct colors)
TRIAL_COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c"]  # blue, orange, green
AVERAGE_COLOR = "#d62728"  # red
LINE_WIDTH_TRIALS = 2.0
LINE_WIDTH_AVERAGE = 4.0

# ============================================================================
# MAIN SCRIPT
# ============================================================================

def load_training_data(trial_dir, seed_type, trial_index):
    """
    Load training log CSV for a given trial and seed type.
    
    Args:
        trial_dir (Path): Path to the trial directory
        seed_type (str): "prng" or "qrng"
        trial_index (int): Trial number (1, 2, 3)
    
    Returns:
        pd.DataFrame: Training data or None if file not found
    """
    csv_path = trial_dir / f"ppo_training_log_{seed_type.upper()}_{trial_index}.csv"
    
    if not csv_path.exists():
        print(f"Warning: File not found: {csv_path}")
        return None
    
    df = pd.read_csv(csv_path, comment="#")
    return df


def create_comparison_plot():
    """Create 4-subplot comparison plot for PRNG and QRNG across all trials."""
    
    # Define subplot structure: (2 rows, 2 cols)
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Flatten axes for easier indexing
    ax_prng_success = axes[0, 0]
    ax_qrng_success = axes[0, 1]
    ax_prng_reward = axes[1, 0]
    ax_qrng_reward = axes[1, 1]
    
    # Data storage for averaging
    prng_success_data = []
    qrng_success_data = []
    prng_reward_data = []
    qrng_reward_data = []
    
    # Load and plot data for each trial
    for idx, trial_name in enumerate(TRIAL_DIRS):
        trial_path = TRAINING_LOG_DIR / trial_name
        trial_num = idx + 1  # Trial numbers are 1-indexed
        
        if not trial_path.exists():
            print(f"Warning: Trial directory not found: {trial_path}")
            continue
        
        color = TRIAL_COLORS[idx]
        
        # Load PRNG data
        prng_df = load_training_data(trial_path, "prng", trial_num)
        if prng_df is not None:
            episodes = prng_df["episode"].values
            success_rate = prng_df["success_rate_100"].values
            avg_reward = prng_df["avg_reward_100"].values
            
            ax_prng_success.plot(
                episodes, success_rate,
                color=color, linewidth=LINE_WIDTH_TRIALS,
                alpha=0.7, label=f"{trial_name}"
            )
            ax_prng_reward.plot(
                episodes, avg_reward,
                color=color, linewidth=LINE_WIDTH_TRIALS,
                alpha=0.7, label=f"{trial_name}"
            )
            
            prng_success_data.append(success_rate)
            prng_reward_data.append(avg_reward)
        
        # Load QRNG data
        qrng_df = load_training_data(trial_path, "qrng", trial_num)
        if qrng_df is not None:
            episodes = qrng_df["episode"].values
            success_rate = qrng_df["success_rate_100"].values
            avg_reward = qrng_df["avg_reward_100"].values
            
            ax_qrng_success.plot(
                episodes, success_rate,
                color=color, linewidth=LINE_WIDTH_TRIALS,
                alpha=0.7, label=f"{trial_name}"
            )
            ax_qrng_reward.plot(
                episodes, avg_reward,
                color=color, linewidth=LINE_WIDTH_TRIALS,
                alpha=0.7, label=f"{trial_name}"
            )
            
            qrng_success_data.append(success_rate)
            qrng_reward_data.append(avg_reward)
    
    # Calculate and plot averages (handle different array lengths by truncating to min length)
    if prng_success_data:
        min_len = min(len(arr) for arr in prng_success_data)
        prng_success_truncated = [arr[:min_len] for arr in prng_success_data]
        avg_prng_success = np.mean(prng_success_truncated, axis=0)
        ax_prng_success.plot(
            episodes[:min_len], avg_prng_success,
            color=AVERAGE_COLOR, linewidth=LINE_WIDTH_AVERAGE,
            label="Average", linestyle="-"
        )
    
    if qrng_success_data:
        min_len = min(len(arr) for arr in qrng_success_data)
        qrng_success_truncated = [arr[:min_len] for arr in qrng_success_data]
        avg_qrng_success = np.mean(qrng_success_truncated, axis=0)
        ax_qrng_success.plot(
            episodes[:min_len], avg_qrng_success,
            color=AVERAGE_COLOR, linewidth=LINE_WIDTH_AVERAGE,
            label="Average", linestyle="-"
        )
    
    if prng_reward_data:
        min_len = min(len(arr) for arr in prng_reward_data)
        prng_reward_truncated = [arr[:min_len] for arr in prng_reward_data]
        avg_prng_reward = np.mean(prng_reward_truncated, axis=0)
        ax_prng_reward.plot(
            episodes[:min_len], avg_prng_reward,
            color=AVERAGE_COLOR, linewidth=LINE_WIDTH_AVERAGE,
            label="Average", linestyle="-"
        )
    
    if qrng_reward_data:
        min_len = min(len(arr) for arr in qrng_reward_data)
        qrng_reward_truncated = [arr[:min_len] for arr in qrng_reward_data]
        avg_qrng_reward = np.mean(qrng_reward_truncated, axis=0)
        ax_qrng_reward.plot(
            episodes[:min_len], avg_qrng_reward,
            color=AVERAGE_COLOR, linewidth=LINE_WIDTH_AVERAGE,
            label="Average", linestyle="-"
        )
    
    # Configure PRNG Success Rate plot
    ax_prng_success.set_xlabel("Episode", fontsize=12, fontweight="bold")
    ax_prng_success.set_ylabel("Success Rate (%)", fontsize=12, fontweight="bold")
    ax_prng_success.set_title("PRNG - Success Rate % over Episodes", fontsize=14, fontweight="bold")
    ax_prng_success.grid(True, alpha=0.3)
    ax_prng_success.legend(loc="best", fontsize=10)
    
    # Configure QRNG Success Rate plot
    ax_qrng_success.set_xlabel("Episode", fontsize=12, fontweight="bold")
    ax_qrng_success.set_ylabel("Success Rate (%)", fontsize=12, fontweight="bold")
    ax_qrng_success.set_title("QRNG - Success Rate % over Episodes", fontsize=14, fontweight="bold")
    ax_qrng_success.grid(True, alpha=0.3)
    ax_qrng_success.legend(loc="best", fontsize=10)
    
    # Configure PRNG Reward plot
    ax_prng_reward.set_xlabel("Episode", fontsize=12, fontweight="bold")
    ax_prng_reward.set_ylabel("Avg Reward (100-ep rolling)", fontsize=12, fontweight="bold")
    ax_prng_reward.set_title("PRNG - Rewards over Episodes", fontsize=14, fontweight="bold")
    ax_prng_reward.grid(True, alpha=0.3)
    ax_prng_reward.legend(loc="best", fontsize=10)
    
    # Configure QRNG Reward plot
    ax_qrng_reward.set_xlabel("Episode", fontsize=12, fontweight="bold")
    ax_qrng_reward.set_ylabel("Avg Reward (100-ep rolling)", fontsize=12, fontweight="bold")
    ax_qrng_reward.set_title("QRNG - Rewards over Episodes", fontsize=14, fontweight="bold")
    ax_qrng_reward.grid(True, alpha=0.3)
    ax_qrng_reward.legend(loc="best", fontsize=10)
    
    # Adjust layout to prevent overlap
    plt.tight_layout()
    
    # Save figure
    output_path = MODEL_OUTPUT_DIR / OUTPUT_FILENAME
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"✓ Plot saved to: {output_path}")
    
    # Close to free memory
    plt.close()


if __name__ == "__main__":
    print(f"Creating training comparison plots from: {TRAINING_LOG_DIR}")
    print(f"Trials: {', '.join(TRIAL_DIRS)}")
    
    if not TRAINING_LOG_DIR.exists():
        print(f"Error: Training logs directory not found: {TRAINING_LOG_DIR}")
        exit(1)
    
    create_comparison_plot()
    print("Done!")
