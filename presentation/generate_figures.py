import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import numpy as np
from scipy.spatial import ConvexHull
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figures')

def load_data():
    prng = pd.read_csv(os.path.join(BASE_DIR, 'a2c/outputs/maze_metrics/prng_metrics.csv'))
    qrng = pd.read_csv(os.path.join(BASE_DIR, 'a2c/outputs/maze_metrics/qrng_metrics.csv'))
    return prng, qrng

def generate_histogram(prng, qrng):
    """Generate histogram comparing path length, tortuosity, dead-end count."""
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    axes[0].hist(prng['shortest_path_len'], bins=40, alpha=0.6, label=f'PRNG (μ={prng["shortest_path_len"].mean():.2f})', color='#4472C4')
    axes[0].hist(qrng['shortest_path_len'], bins=40, alpha=0.6, label=f'QRNG (μ={qrng["shortest_path_len"].mean():.2f})', color='#ED7D31')
    axes[0].set_title('Path Length Distribution', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Value')
    axes[0].set_ylabel('Count')
    axes[0].legend(fontsize=9)

    axes[1].hist(prng['tortuosity'], bins=40, alpha=0.6, label=f'PRNG (μ={prng["tortuosity"].mean():.2f})', color='#4472C4')
    axes[1].hist(qrng['tortuosity'], bins=40, alpha=0.6, label=f'QRNG (μ={qrng["tortuosity"].mean():.2f})', color='#ED7D31')
    axes[1].set_title('Path Tortuosity Distribution', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Value')
    axes[1].set_ylabel('Count')
    axes[1].legend(fontsize=9)

    axes[2].hist(prng['dead_end_count'], bins=20, alpha=0.6, label=f'PRNG (μ={prng["dead_end_count"].mean():.2f})', color='#4472C4')
    axes[2].hist(qrng['dead_end_count'], bins=20, alpha=0.6, label=f'QRNG (μ={qrng["dead_end_count"].mean():.2f})', color='#ED7D31')
    axes[2].set_title('Dead-End Count Distribution', fontsize=14, fontweight='bold')
    axes[2].set_xlabel('Value')
    axes[2].set_ylabel('Count')
    axes[2].legend(fontsize=9)

    plt.tight_layout()
    path = os.path.join(FIGURES_DIR, 'histogram_structural.png')
    plt.savefig(path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f'Saved: {path}')

def generate_boxplot(prng, qrng):
    """Generate boxplot comparing path length, tortuosity, dead-end count."""
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    for ax, col, title in zip(axes,
        ['shortest_path_len', 'tortuosity', 'dead_end_count'],
        ['Path Length (Dijkstra)', 'Path Tortuosity', 'Dead-End Count']):
        bp = ax.boxplot([prng[col], qrng[col]], tick_labels=['PRNG', 'QRNG'],
                       patch_artist=True, showmeans=True,
                       meanprops=dict(marker='D', markerfacecolor='red', markersize=8))
        bp['boxes'][0].set_facecolor('#4472C4')
        bp['boxes'][1].set_facecolor('#ED7D31')
        for box in bp['boxes']:
            box.set_alpha(0.5)
        ax.set_title(title, fontsize=14, fontweight='bold')
        prng_mean = prng[col].mean()
        qrng_mean = qrng[col].mean()
        prng_med = prng[col].median()
        qrng_med = qrng[col].median()
        ax.set_xlabel(f'PRNG: μ={prng_mean:.2f}, Md={prng_med:.2f}\nQRNG: μ={qrng_mean:.2f}, Md={qrng_med:.2f}', fontsize=9)

    plt.tight_layout()
    path = os.path.join(FIGURES_DIR, 'boxplot_structural.png')
    plt.savefig(path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f'Saved: {path}')

def generate_era_plot(prng, qrng):
    """Generate Expressive Range Analysis plot (Linearity vs Leniency)."""
    prng_linearity = prng['straight_corridors'] / (prng['straight_corridors'] + prng['turning_corridors'])
    qrng_linearity = qrng['straight_corridors'] / (qrng['straight_corridors'] + qrng['turning_corridors'])

    prng_leniency = -prng['dead_end_count'] / prng['cell_nodes']
    qrng_leniency = -qrng['dead_end_count'] / qrng['cell_nodes']

    fig, ax = plt.subplots(figsize=(10, 8))

    ax.scatter(prng_linearity, prng_leniency, alpha=0.3, s=5, color='#4472C4', label=f'PRNG (n={len(prng)})')
    ax.scatter(qrng_linearity, qrng_leniency, alpha=0.3, s=5, color='#ED7D31', label=f'QRNG (n={len(qrng)})')

    for data_x, data_y, color, label in [
        (prng_linearity, prng_leniency, '#4472C4', 'PRNG'),
        (qrng_linearity, qrng_leniency, '#ED7D31', 'QRNG')
    ]:
        points = np.column_stack([data_x.values, data_y.values])
        points = points[~np.isnan(points).any(axis=1)]
        hull = ConvexHull(points)
        hull_points = np.append(hull.vertices, hull.vertices[0])
        ax.plot(points[hull_points, 0], points[hull_points, 1], '-', color=color, linewidth=2)
        ax.fill(points[hull.vertices, 0], points[hull.vertices, 1], alpha=0.1, color=color,
                label=f'{label} Hull (Area={hull.volume:.6f})')

    ax.set_xlabel('Linearity (Straight Corridors / Total Corridors)', fontsize=12)
    ax.set_ylabel('Leniency (-Dead Ends / Total Nodes)', fontsize=12)
    ax.set_title('Expressive Range Analysis (ERA): PRNG vs QRNG Maze Diversity', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)

    plt.tight_layout()
    path = os.path.join(FIGURES_DIR, 'era_plot.png')
    plt.savefig(path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f'Saved: {path}')

if __name__ == '__main__':
    os.makedirs(FIGURES_DIR, exist_ok=True)
    prng, qrng = load_data()
    print(f'Loaded PRNG: {len(prng)} rows, QRNG: {len(qrng)} rows')
    generate_histogram(prng, qrng)
    generate_boxplot(prng, qrng)
    generate_era_plot(prng, qrng)
    print('All figures generated.')
