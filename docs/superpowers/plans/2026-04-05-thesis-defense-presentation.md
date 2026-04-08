# Thesis Defense Presentation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a complete 15-slide PowerPoint presentation for the CS Thesis Final Defense on April 8, 2026, following the approved spec at `docs/superpowers/specs/2026-04-05-thesis-defense-presentation-design.md`.

**Architecture:** A Python script using `python-pptx` generates the entire presentation programmatically. Maze structural figures (histograms, boxplots, ERA plot) are regenerated from CSV data using matplotlib since they don't exist as standalone images. Training curve images already exist in the repo. The script produces a single `.pptx` file.

**Tech Stack:** Python 3, python-pptx, matplotlib, pandas

---

## File Structure

| File | Purpose |
|------|---------|
| `presentation/generate_slides.py` | Main script that builds the full 15-slide PPTX |
| `presentation/generate_figures.py` | Script to regenerate maze structural figures from CSV data |
| `presentation/figures/` | Directory for generated figure PNGs used in slides |
| `presentation/output/` | Directory for the final PPTX file |

## Available Assets

**Training curve PNGs (already in repo):**
- `a2c/outputs/training_comparison.png` - A2C PRNG vs QRNG comparison
- `dqn/outputs/training_comparison.png` - DQN comparison
- PPO individual reports: `ppo/outputs/training_reports/report_*/training_reports_*/success_rate_*.png`

**Maze metrics CSVs (for figure regeneration):**
- `a2c/outputs/maze_metrics/prng_metrics.csv` - PRNG maze structural data
- `a2c/outputs/maze_metrics/qrng_metrics.csv` - QRNG maze structural data

**Figures NOT available as standalone files (must be regenerated or extracted):**
- Histogram: path length, tortuosity, dead-end count distributions (thesis Figure 6)
- Boxplot: path length, tortuosity, dead-end count (thesis Figure 7)
- ERA plot: linearity vs leniency convex hulls (thesis Figure 9)
- Conceptual Framework Diagram (thesis Figure 5) - this is a diagram, not data-driven; will need to be created manually or extracted from the PDF

---

### Task 1: Set Up Project Structure

**Files:**
- Create: `presentation/generate_figures.py`
- Create: `presentation/generate_slides.py`
- Create: `presentation/figures/` (directory)
- Create: `presentation/output/` (directory)

- [ ] **Step 1: Create directories**

```bash
mkdir -p presentation/figures presentation/output
```

- [ ] **Step 2: Create empty Python files**

```bash
touch presentation/generate_figures.py presentation/generate_slides.py
```

- [ ] **Step 3: Verify python-pptx and dependencies are available**

```bash
python3 -c "import pptx, matplotlib, pandas; print('All dependencies available')"
```

Expected: `All dependencies available`

---

### Task 2: Generate Maze Structural Figures from CSV Data

**Files:**
- Create: `presentation/generate_figures.py`
- Read: `a2c/outputs/maze_metrics/prng_metrics.csv`
- Read: `a2c/outputs/maze_metrics/qrng_metrics.csv`
- Output: `presentation/figures/histogram_structural.png`
- Output: `presentation/figures/boxplot_structural.png`
- Output: `presentation/figures/era_plot.png`

- [ ] **Step 1: Write the figure generation script**

Write `presentation/generate_figures.py` with three functions:

```python
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

    # Path Length
    axes[0].hist(prng['shortest_path_len'], bins=40, alpha=0.6, label=f'PRNG (μ={prng["shortest_path_len"].mean():.2f})', color='#4472C4')
    axes[0].hist(qrng['shortest_path_len'], bins=40, alpha=0.6, label=f'QRNG (μ={qrng["shortest_path_len"].mean():.2f})', color='#ED7D31')
    axes[0].set_title('Path Length Distribution', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Value')
    axes[0].set_ylabel('Count')
    axes[0].legend(fontsize=9)

    # Tortuosity
    axes[1].hist(prng['tortuosity'], bins=40, alpha=0.6, label=f'PRNG (μ={prng["tortuosity"].mean():.2f})', color='#4472C4')
    axes[1].hist(qrng['tortuosity'], bins=40, alpha=0.6, label=f'QRNG (μ={qrng["tortuosity"].mean():.2f})', color='#ED7D31')
    axes[1].set_title('Path Tortuosity Distribution', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Value')
    axes[1].set_ylabel('Count')
    axes[1].legend(fontsize=9)

    # Dead-End Count
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
        bp = ax.boxplot([prng[col], qrng[col]], labels=['PRNG', 'QRNG'],
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
    # Linearity = straight_corridors / (straight_corridors + turning_corridors)
    prng_linearity = prng['straight_corridors'] / (prng['straight_corridors'] + prng['turning_corridors'])
    qrng_linearity = qrng['straight_corridors'] / (qrng['straight_corridors'] + qrng['turning_corridors'])

    # Leniency = -dead_end_count / cell_nodes (negative because more dead ends = less lenient)
    prng_leniency = -prng['dead_end_count'] / prng['cell_nodes']
    qrng_leniency = -qrng['dead_end_count'] / qrng['cell_nodes']

    fig, ax = plt.subplots(figsize=(10, 8))

    ax.scatter(prng_linearity, prng_leniency, alpha=0.3, s=5, color='#4472C4', label=f'PRNG (n={len(prng)})')
    ax.scatter(qrng_linearity, qrng_leniency, alpha=0.3, s=5, color='#ED7D31', label=f'QRNG (n={len(qrng)})')

    # Draw convex hulls
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
```

- [ ] **Step 2: Run the figure generation script**

```bash
cd /Users/angelobaricante/CS-Thesis-Model-Training && python3 presentation/generate_figures.py
```

Expected output:
```
Loaded PRNG: XXXXX rows, QRNG: XXXXX rows
Saved: .../presentation/figures/histogram_structural.png
Saved: .../presentation/figures/boxplot_structural.png
Saved: .../presentation/figures/era_plot.png
All figures generated.
```

- [ ] **Step 3: Verify all three figures were created**

```bash
ls -la presentation/figures/
```

Expected: `histogram_structural.png`, `boxplot_structural.png`, `era_plot.png` all present with non-zero file sizes.

---

### Task 3: Build the PowerPoint Presentation Script

**Files:**
- Create: `presentation/generate_slides.py`
- Read: `presentation/figures/*.png`
- Read: `a2c/outputs/training_comparison.png`
- Read: `ppo/outputs/training_reports/report_1/training_reports_prng/success_rate_prng.png`
- Output: `presentation/output/thesis_defense_presentation.pptx`

- [ ] **Step 1: Write the slide generation script**

Write `presentation/generate_slides.py` — a single Python script that creates all 15 slides.

```python
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figures')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')

# Color scheme - minimalist academic
NAVY = RGBColor(0x1B, 0x2A, 0x4A)
DARK_GRAY = RGBColor(0x33, 0x33, 0x33)
MEDIUM_GRAY = RGBColor(0x66, 0x66, 0x66)
LIGHT_GRAY = RGBColor(0xF2, 0xF2, 0xF2)
ACCENT_BLUE = RGBColor(0x44, 0x72, 0xC4)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

# Slide dimensions (widescreen 16:9)
SLIDE_WIDTH = Inches(13.333)
SLIDE_HEIGHT = Inches(7.5)


def set_slide_bg(slide, color=WHITE):
    """Set slide background color."""
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_textbox(slide, left, top, width, height, text, font_size=18,
                bold=False, color=DARK_GRAY, alignment=PP_ALIGN.LEFT, font_name='Calibri'):
    """Add a text box to a slide."""
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.font.name = font_name
    p.alignment = alignment
    return tf


def add_bullet_list(slide, left, top, width, height, items, font_size=16,
                    color=DARK_GRAY, font_name='Calibri', bold_items=None):
    """Add a bulleted list to a slide."""
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = item
        p.font.size = Pt(font_size)
        p.font.color.rgb = color
        p.font.name = font_name
        p.space_after = Pt(6)
        if bold_items and i in bold_items:
            p.font.bold = True
    return tf


def add_accent_line(slide, left, top, width):
    """Add a thin accent line."""
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, Pt(3))
    shape.fill.solid()
    shape.fill.fore_color.rgb = ACCENT_BLUE
    shape.line.fill.background()
    return shape


def add_image_safe(slide, img_path, left, top, width=None, height=None):
    """Add an image if the file exists, otherwise add a placeholder box."""
    if os.path.exists(img_path):
        if width and height:
            slide.shapes.add_picture(img_path, left, top, width, height)
        elif width:
            slide.shapes.add_picture(img_path, left, top, width=width)
        elif height:
            slide.shapes.add_picture(img_path, left, top, height=height)
        else:
            slide.shapes.add_picture(img_path, left, top)
    else:
        shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top,
                                        width or Inches(4), height or Inches(3))
        shape.fill.solid()
        shape.fill.fore_color.rgb = LIGHT_GRAY
        shape.line.color.rgb = MEDIUM_GRAY
        tf = shape.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = f'[Image: {os.path.basename(img_path)}]'
        p.font.size = Pt(12)
        p.font.color.rgb = MEDIUM_GRAY
        p.alignment = PP_ALIGN.CENTER


def build_slide_1_title(prs):
    """SLIDE 1: TITLE SLIDE"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank layout
    set_slide_bg(slide, WHITE)

    # Top accent bar
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), SLIDE_WIDTH, Inches(0.6))
    shape.fill.solid()
    shape.fill.fore_color.rgb = NAVY
    shape.line.fill.background()

    # Title
    add_textbox(slide, Inches(1), Inches(1.2), Inches(11.3), Inches(1.8),
                'Enhancing Autonomous Navigation Robustness\nin Unstructured Environments using\nQuantum-Seeded Procedural Maze Generation',
                font_size=28, bold=True, color=NAVY, alignment=PP_ALIGN.CENTER)

    # Divider line
    add_accent_line(slide, Inches(4), Inches(3.2), Inches(5.3))

    # Institution
    add_textbox(slide, Inches(1), Inches(3.5), Inches(11.3), Inches(0.6),
                'Batangas State University - College of Informatics and Computing Sciences',
                font_size=14, color=MEDIUM_GRAY, alignment=PP_ALIGN.CENTER)

    # Members
    add_textbox(slide, Inches(1), Inches(4.3), Inches(11.3), Inches(1.0),
                'Antony, Aldrich Ryan V.  |  Baricante, Mark Angelo R.  |  Mirabel, Kevin Hans Aurick S.',
                font_size=16, color=DARK_GRAY, alignment=PP_ALIGN.CENTER)

    # Adviser
    add_textbox(slide, Inches(1), Inches(5.2), Inches(11.3), Inches(0.5),
                'Adviser: John Richard M. Esguerra, MSCS',
                font_size=14, color=MEDIUM_GRAY, alignment=PP_ALIGN.CENTER)

    # Date
    add_textbox(slide, Inches(1), Inches(5.8), Inches(11.3), Inches(0.5),
                'April 8, 2026',
                font_size=14, color=MEDIUM_GRAY, alignment=PP_ALIGN.CENTER)

    # Bottom accent bar
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(6.9), SLIDE_WIDTH, Inches(0.6))
    shape.fill.solid()
    shape.fill.fore_color.rgb = NAVY
    shape.line.fill.background()


def add_slide_header(slide, title, subtitle=None):
    """Standard slide header with navy bar and title."""
    # Top accent bar
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), SLIDE_WIDTH, Inches(0.08))
    shape.fill.solid()
    shape.fill.fore_color.rgb = NAVY
    shape.line.fill.background()

    # Title
    add_textbox(slide, Inches(0.6), Inches(0.3), Inches(12), Inches(0.6),
                title, font_size=28, bold=True, color=NAVY)

    # Underline
    add_accent_line(slide, Inches(0.6), Inches(0.95), Inches(3))

    if subtitle:
        add_textbox(slide, Inches(0.6), Inches(1.0), Inches(12), Inches(0.4),
                    subtitle, font_size=14, color=MEDIUM_GRAY)


def build_slide_2_overview(prs):
    """SLIDE 2: OVERVIEW OF THE STUDY"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, WHITE)
    add_slide_header(slide, 'Overview of the Study')

    # Background
    add_textbox(slide, Inches(0.6), Inches(1.4), Inches(5.5), Inches(0.4),
                'Background', font_size=18, bold=True, color=NAVY)
    add_bullet_list(slide, Inches(0.8), Inches(1.8), Inches(11.5), Inches(1.2), [
        'Procedural Content Generation (PCG) relies on PRNGs to create diverse training environments for Deep Reinforcement Learning agents',
        'Quantum Random Number Generators (QRNGs) provide true randomness from quantum phenomena \u2014 but have never been tested in PCG',
    ], font_size=15)

    # Research Problem
    add_textbox(slide, Inches(0.6), Inches(3.3), Inches(5.5), Inches(0.4),
                'Research Problem', font_size=18, bold=True, color=NAVY)
    add_bullet_list(slide, Inches(0.8), Inches(3.7), Inches(11.5), Inches(0.8), [
        'Does the source of seed-level randomness affect maze structural diversity and DRL agent generalization?',
    ], font_size=15)

    # Motivation
    add_textbox(slide, Inches(0.6), Inches(4.7), Inches(5.5), Inches(0.4),
                'Motivation', font_size=18, bold=True, color=NAVY)
    add_bullet_list(slide, Inches(0.8), Inches(5.1), Inches(11.5), Inches(1.2), [
        'DRL agents overfit to training environments; structural randomization is underexplored compared to visual domain randomization',
    ], font_size=15)


def build_slide_3_research_gap(prs):
    """SLIDE 3: RESEARCH GAP"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, WHITE)
    add_slide_header(slide, 'Research Gap')

    add_bullet_list(slide, Inches(0.8), Inches(1.5), Inches(11.5), Inches(4.0), [
        'Existing PCG studies exclusively use PRNGs \u2014 no empirical evaluation of QRNG in procedural generation',
        'Domain randomization research focuses on visual changes (textures, lighting, colors), not structural randomization of the environment itself',
        'No study has tested whether true quantum entropy improves DRL zero-shot generalization in navigation tasks',
    ], font_size=18)

    # Gap highlight box
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2), Inches(4.5), Inches(9.3), Inches(1.5))
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor(0xE8, 0xEE, 0xF7)
    shape.line.color.rgb = ACCENT_BLUE
    tf = shape.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = 'This study bridges the gap: first empirical benchmark of QRNG-seeded procedural generation for DRL training environments'
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.alignment = PP_ALIGN.CENTER


def build_slide_4_objectives(prs):
    """SLIDE 4: OBJECTIVES OF THE STUDY"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, WHITE)
    add_slide_header(slide, 'Objectives of the Study')

    # General Objective
    add_textbox(slide, Inches(0.6), Inches(1.4), Inches(5.5), Inches(0.4),
                'General Objective', font_size=18, bold=True, color=NAVY)
    add_bullet_list(slide, Inches(0.8), Inches(1.8), Inches(11.5), Inches(0.8), [
        'Evaluate the impact of QRNG vs. PRNG seeds on procedural maze generation and DRL agent navigation robustness',
    ], font_size=15)

    # Specific Objectives
    add_textbox(slide, Inches(0.6), Inches(2.8), Inches(5.5), Inches(0.4),
                'Specific Objectives', font_size=18, bold=True, color=NAVY)
    add_bullet_list(slide, Inches(0.8), Inches(3.2), Inches(11.5), Inches(3.5), [
        '1.  Determine how different sources of randomness (PRNGs and QRNGs) influence the structural metrics \u2014 path length, tortuosity, dead-end count \u2014 and overall diversity of maze training environments',
        '2.  Determine the extent to which QRNG-based sources impact the training of autonomous navigation models in terms of success rate and rewards over episodes',
        '3.  Evaluate the performance of DRL agents trained in QRNG-seeded vs. PRNG-seeded mazes on unseen environments, in terms of success rate, reward, efficiency, and generalization',
    ], font_size=15)


def build_slide_5_conceptual(prs):
    """SLIDE 5: CONCEPTUAL / SYSTEM OVERVIEW"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, WHITE)
    add_slide_header(slide, 'Conceptual Framework')

    # Since the conceptual framework diagram is only in the PDF, create a text-based version
    # Input section
    add_textbox(slide, Inches(0.4), Inches(1.5), Inches(3.8), Inches(0.4),
                'INPUT', font_size=16, bold=True, color=WHITE, alignment=PP_ALIGN.CENTER)
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.4), Inches(1.4), Inches(3.8), Inches(2.0))
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor(0xE8, 0xEE, 0xF7)
    shape.line.color.rgb = ACCENT_BLUE
    tf = shape.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = 'INPUT'
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.alignment = PP_ALIGN.CENTER
    p2 = tf.add_paragraph()
    p2.text = '\u2022 PRNG Seeds (Mersenne Twister, 64-bit)\n\u2022 QRNG Seeds (ANU Quantum API, 64-bit)\n\u2022 Recursive Backtracking Algorithm'
    p2.font.size = Pt(13)
    p2.font.color.rgb = DARK_GRAY

    # Process section
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.7), Inches(1.4), Inches(4.0), Inches(2.0))
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor(0xE8, 0xEE, 0xF7)
    shape.line.color.rgb = ACCENT_BLUE
    tf = shape.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = 'PROCESS'
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.alignment = PP_ALIGN.CENTER
    p2 = tf.add_paragraph()
    p2.text = '\u2022 Maze Generation & Feature Extraction\n\u2022 Maze Structural Evaluation\n\u2022 DRL Model Training (A2C, DQN, PPO)\n\u2022 Generalization Testing'
    p2.font.size = Pt(13)
    p2.font.color.rgb = DARK_GRAY

    # Output section
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.2), Inches(1.4), Inches(3.8), Inches(2.0))
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor(0xE8, 0xEE, 0xF7)
    shape.line.color.rgb = ACCENT_BLUE
    tf = shape.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = 'OUTPUT'
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.alignment = PP_ALIGN.CENTER
    p2 = tf.add_paragraph()
    p2.text = '\u2022 Maze Structure Comparison\n\u2022 RL Performance Evaluation\n\u2022 QRNG Suitability Assessment\n\u2022 Benchmarking Framework'
    p2.font.size = Pt(13)
    p2.font.color.rgb = DARK_GRAY

    # Arrows between sections (simple right arrows using shapes)
    arrow1 = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(4.25), Inches(2.1), Inches(0.4), Inches(0.3))
    arrow1.fill.solid()
    arrow1.fill.fore_color.rgb = NAVY
    arrow1.line.fill.background()

    arrow2 = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(8.75), Inches(2.1), Inches(0.4), Inches(0.3))
    arrow2.fill.solid()
    arrow2.fill.fore_color.rgb = NAVY
    arrow2.line.fill.background()

    # Bottom detail: Two-Group Comparative Design
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.5), Inches(4.0), Inches(4.5), Inches(2.5))
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor(0xFC, 0xF0, 0xE3)
    shape.line.color.rgb = RGBColor(0xED, 0x7D, 0x31)
    tf = shape.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = 'Control Group (Agent_PRNG)'
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = DARK_GRAY
    p.alignment = PP_ALIGN.CENTER
    p2 = tf.add_paragraph()
    p2.text = 'Trained on PRNG-seeded mazes\n10M timesteps \u00d7 3 trials\nBaseline for comparison'
    p2.font.size = Pt(12)
    p2.font.color.rgb = DARK_GRAY

    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.3), Inches(4.0), Inches(4.5), Inches(2.5))
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor(0xE3, 0xEF, 0xFC)
    shape.line.color.rgb = ACCENT_BLUE
    tf = shape.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = 'Experimental Group (Agent_QRNG)'
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = DARK_GRAY
    p.alignment = PP_ALIGN.CENTER
    p2 = tf.add_paragraph()
    p2.text = 'Trained on QRNG-seeded mazes\n10M timesteps \u00d7 3 trials\nTests quantum entropy hypothesis'
    p2.font.size = Pt(12)
    p2.font.color.rgb = DARK_GRAY


def build_slide_6_pipeline(prs):
    """SLIDE 6: OVERALL PIPELINE"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, WHITE)
    add_slide_header(slide, 'Methodology: Overall Pipeline')

    steps = [
        ('1', 'Generate Seeds', 'PRNG: Mersenne Twister (64-bit)\nQRNG: ANU API \u2192 bitwise concat to 64-bit'),
        ('2', 'Validate Seed Quality', 'Shannon Entropy\nAutocorrelation (lag 0\u2013100)'),
        ('3', 'Generate Mazes', 'Recursive Backtracking\n20\u00d720 grid, 71,800 per group'),
        ('4', 'Extract Maze Metrics', 'Path length, tortuosity, dead-ends\nJunction proportions, corridor analysis'),
        ('5', 'Train DRL Agents', 'A2C, DQN, PPO\n10M timesteps, 3 trials each'),
        ('6', 'Evaluate Generalization', '1,000 unseen mazes per condition\nIntra-domain + Cross-domain'),
        ('7', 'Statistical Comparison', 'Shapiro-Wilk \u2192 Mann-Whitney U\nPERMANOVA (p=0.05)'),
    ]

    start_y = 1.4
    box_height = 0.7
    gap = 0.12

    for i, (num, title, desc) in enumerate(steps):
        y = start_y + i * (box_height + gap)

        # Number circle
        circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.6), Inches(y + 0.1), Inches(0.45), Inches(0.45))
        circle.fill.solid()
        circle.fill.fore_color.rgb = NAVY
        circle.line.fill.background()
        tf = circle.text_frame
        p = tf.paragraphs[0]
        p.text = num
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER

        # Step title
        add_textbox(slide, Inches(1.2), Inches(y), Inches(3.5), Inches(box_height),
                    title, font_size=15, bold=True, color=NAVY)

        # Step description
        add_textbox(slide, Inches(4.8), Inches(y), Inches(8.0), Inches(box_height),
                    desc, font_size=13, color=MEDIUM_GRAY)

        # Connector line (except last)
        if i < len(steps) - 1:
            line_y = y + box_height
            shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                           Inches(0.8), Inches(line_y), Inches(0.05), Inches(gap))
            shape.fill.solid()
            shape.fill.fore_color.rgb = ACCENT_BLUE
            shape.line.fill.background()


def build_slide_7_model_design(prs):
    """SLIDE 7: MODEL / ALGORITHM DESIGN"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, WHITE)
    add_slide_header(slide, 'Model / Algorithm Design')

    # LEFT PANEL - Environment Design
    add_textbox(slide, Inches(0.6), Inches(1.3), Inches(5.5), Inches(0.4),
                'Environment Configuration', font_size=16, bold=True, color=NAVY)

    env_items = [
        'Maze: 20\u00d720 grid, recursive backtracking',
        'Observation: 10-dim vector (8 LiDAR rays + 2D target)',
        'Action space: {Up, Down, Left, Right}',
        'Episode limit: 500 steps',
    ]
    add_bullet_list(slide, Inches(0.8), Inches(1.8), Inches(5.8), Inches(1.6), env_items, font_size=14)

    # Reward table
    add_textbox(slide, Inches(0.8), Inches(3.4), Inches(5.0), Inches(0.3),
                'Reward Structure:', font_size=14, bold=True, color=NAVY)

    rewards = [
        'Goal Achieved: +250',
        'Wall Collision: -0.75',
        'Step Penalty: -0.005',
        'New Cell Exploration: +2.0',
        'Progress Reward: +0.5 \u00d7 improvement',
        'Timeout: -7',
    ]
    add_bullet_list(slide, Inches(1.0), Inches(3.7), Inches(5.0), Inches(2.5), rewards, font_size=13, color=MEDIUM_GRAY)

    # Vertical divider
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.5), Inches(1.3), Pt(2), Inches(5.0))
    shape.fill.solid()
    shape.fill.fore_color.rgb = LIGHT_GRAY
    shape.line.fill.background()

    # RIGHT PANEL - DRL Architectures
    add_textbox(slide, Inches(6.8), Inches(1.3), Inches(6.0), Inches(0.4),
                'DRL Architectures', font_size=16, bold=True, color=NAVY)

    add_textbox(slide, Inches(6.8), Inches(1.8), Inches(6.0), Inches(0.5),
                'Input(10) \u2192 MLP Hidden Layers \u2192 Output(4 actions)',
                font_size=14, color=MEDIUM_GRAY)

    # Three model boxes
    models = [
        ('A2C', 'Actor-Critic Hybrid', 'MLP(64, 64)\nLR: 7\u00d710\u207b\u2074\nEntropy Coeff: 0.0'),
        ('DQN', 'Value-Based', 'MLP(256, 256)\nLR: 1\u00d710\u207b\u00b3\n\u03b5-greedy: 1.0\u21920.05'),
        ('PPO', 'Policy Gradient', 'MLP(256, 256)\nLR: 3\u00d710\u207b\u2074\nEntropy Coeff: 0.01'),
    ]

    for i, (name, family, details) in enumerate(models):
        y = 2.5 + i * 1.5
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                        Inches(6.8), Inches(y), Inches(5.8), Inches(1.3))
        shape.fill.solid()
        shape.fill.fore_color.rgb = LIGHT_GRAY
        shape.line.color.rgb = ACCENT_BLUE
        tf = shape.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = f'{name} \u2014 {family}'
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = NAVY
        p2 = tf.add_paragraph()
        p2.text = details
        p2.font.size = Pt(12)
        p2.font.color.rgb = DARK_GRAY

    # Bottom note
    add_textbox(slide, Inches(6.8), Inches(6.3), Inches(5.8), Inches(0.5),
                'Three DRL families to benchmark the randomness source, not the model',
                font_size=12, bold=True, color=ACCENT_BLUE, alignment=PP_ALIGN.CENTER)


def build_slide_8_experimental_setup(prs):
    """SLIDE 8: EXPERIMENTAL SETUP"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, WHITE)
    add_slide_header(slide, 'Experimental Setup')

    # Dataset info
    add_textbox(slide, Inches(0.6), Inches(1.3), Inches(5.5), Inches(0.4),
                'Dataset', font_size=16, bold=True, color=NAVY)
    add_bullet_list(slide, Inches(0.8), Inches(1.7), Inches(11.5), Inches(1.0), [
        '71,800 PRNG seeds (Mersenne Twister) + 71,800 QRNG seeds (ANU Quantum API)',
        '143,600 total 20\u00d720 mazes generated via recursive backtracking',
        '~35,000\u201340,000 training mazes per condition  |  1,000 unseen evaluation mazes per condition',
    ], font_size=14)

    # Hyperparameters table header
    add_textbox(slide, Inches(0.6), Inches(3.0), Inches(5.5), Inches(0.4),
                'Algorithm-Specific Configurations', font_size=16, bold=True, color=NAVY)

    # Create table
    rows, cols = 6, 4
    table_shape = slide.shapes.add_table(rows, cols, Inches(0.8), Inches(3.5), Inches(8.0), Inches(2.5))
    table = table_shape.table

    headers = ['Parameter', 'DQN', 'A2C', 'PPO']
    data = [
        ['Learning Rate', '1 \u00d7 10\u207b\u00b3', '7 \u00d7 10\u207b\u2074', '3 \u00d7 10\u207b\u2074'],
        ['Batch Size', '512', 'N/A (rollout)', '512'],
        ['Network', 'MLP(256, 256)', 'MLP(64, 64)', 'MLP(256, 256)'],
        ['Exploration', '\u03b5-greedy (1.0\u21920.05)', 'Entropy: 0.0', 'Entropy: 0.01'],
        ['Timesteps / Trials', '10M / 3', '10M / 3', '10M / 3'],
    ]

    for i, header in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = header
        for paragraph in cell.text_frame.paragraphs:
            paragraph.font.size = Pt(13)
            paragraph.font.bold = True
            paragraph.font.color.rgb = WHITE
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY

    for r, row_data in enumerate(data):
        for c, value in enumerate(row_data):
            cell = table.cell(r + 1, c)
            cell.text = value
            for paragraph in cell.text_frame.paragraphs:
                paragraph.font.size = Pt(12)
                paragraph.font.color.rgb = DARK_GRAY
            if r % 2 == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = LIGHT_GRAY

    # Tools
    add_textbox(slide, Inches(0.6), Inches(6.2), Inches(11.5), Inches(0.4),
                'Tools: Python  |  Stable-Baselines3  |  Gymnasium  |  scipy.stats  |  ANU Quantum Random Number API',
                font_size=13, color=MEDIUM_GRAY, alignment=PP_ALIGN.CENTER)


def build_slide_9_results(prs):
    """SLIDE 9: PERFORMANCE RESULTS - Maze Structural Analysis"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, WHITE)
    add_slide_header(slide, 'Maze Structural Analysis: PRNG vs QRNG')

    # Histogram figure
    hist_path = os.path.join(FIGURES_DIR, 'histogram_structural.png')
    add_image_safe(slide, hist_path, Inches(0.3), Inches(1.3), width=Inches(8.0), height=Inches(3.2))

    # Key numbers box
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.5), Inches(1.3), Inches(4.5), Inches(2.2))
    shape.fill.solid()
    shape.fill.fore_color.rgb = LIGHT_GRAY
    shape.line.color.rgb = ACCENT_BLUE
    tf = shape.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = 'Key Metrics'
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.alignment = PP_ALIGN.CENTER
    metrics = [
        ('Path Length', 'PRNG \u03bc=87.50 | QRNG \u03bc=87.51'),
        ('Tortuosity', 'Both \u03bc=2.57, Md=2.47'),
        ('Dead-Ends', 'Both \u03bc=11.84, Md=12.00'),
    ]
    for label, value in metrics:
        p2 = tf.add_paragraph()
        p2.text = f'{label}: {value}'
        p2.font.size = Pt(11)
        p2.font.color.rgb = DARK_GRAY

    # Statistical validation box
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.5), Inches(3.7), Inches(4.5), Inches(1.8))
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor(0xE8, 0xEE, 0xF7)
    shape.line.color.rgb = ACCENT_BLUE
    tf = shape.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = 'Statistical Validation'
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = NAVY
    p.alignment = PP_ALIGN.CENTER
    stats = [
        'Mann-Whitney U: all p > 0.05',
        'PERMANOVA: p = 0.7493',
        'ERA Hull: PRNG=0.0131, QRNG=0.0125',
    ]
    for s in stats:
        p2 = tf.add_paragraph()
        p2.text = s
        p2.font.size = Pt(11)
        p2.font.color.rgb = DARK_GRAY

    # Takeaway
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(5.0), Inches(12.1), Inches(0.7))
    shape.fill.solid()
    shape.fill.fore_color.rgb = NAVY
    tf = shape.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = 'The maze generation algorithm \u2014 not the seed source \u2014 determines structural output'
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.alignment = PP_ALIGN.CENTER


def build_slide_10_comparison(prs):
    """SLIDE 10: COMPARISON WITH BASELINE"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, WHITE)
    add_slide_header(slide, 'DRL Agent Performance: QRNG vs PRNG')

    # PPO training comparison image (use individual report images if comparison doesn't exist)
    ppo_prng_path = os.path.join(BASE_DIR, 'ppo/outputs/training_reports/report_1/training_reports_prng/success_rate_prng.png')
    ppo_qrng_path = os.path.join(BASE_DIR, 'ppo/outputs/training_reports/report_1/training_reports_qrng/success_rate_qrng.png')

    add_textbox(slide, Inches(0.6), Inches(1.2), Inches(6.0), Inches(0.3),
                'PPO Training Curves (Success Rate)', font_size=14, bold=True, color=NAVY)

    add_image_safe(slide, ppo_prng_path, Inches(0.3), Inches(1.6), width=Inches(4.2), height=Inches(2.3))
    add_image_safe(slide, ppo_qrng_path, Inches(4.6), Inches(1.6), width=Inches(4.2), height=Inches(2.3))

    add_textbox(slide, Inches(0.3), Inches(3.9), Inches(4.2), Inches(0.3),
                'PRNG: Higher variance, 1 trial collapsed', font_size=11, color=MEDIUM_GRAY, alignment=PP_ALIGN.CENTER)
    add_textbox(slide, Inches(4.6), Inches(3.9), Inches(4.2), Inches(0.3),
                'QRNG: Tighter clustering, consistent', font_size=11, color=MEDIUM_GRAY, alignment=PP_ALIGN.CENTER)

    # Evaluation table
    add_textbox(slide, Inches(0.6), Inches(4.3), Inches(8.0), Inches(0.3),
                'Generalization Evaluation (Intra vs Cross-Domain)', font_size=14, bold=True, color=NAVY)

    rows, cols = 7, 5
    table_shape = slide.shapes.add_table(rows, cols, Inches(0.8), Inches(4.7), Inches(11.5), Inches(2.0))
    table = table_shape.table

    headers = ['Algorithm', 'Agent', 'Intra SR', 'Cross SR', 'Gap (pp)']
    data = [
        ['A2C', 'PRNG', '61.20%', '60.30%', '+0.90'],
        ['A2C', 'QRNG', '58.70%', '59.50%', '-0.80'],
        ['DQN', 'PRNG', '11.03%', '12.37%', '-1.33'],
        ['DQN', 'QRNG', '9.80%', '8.97%', '+2.57'],
        ['PPO', 'PRNG', '73.27%', '71.53%', '+1.74'],
        ['PPO', 'QRNG', '72.43%', '74.00%', '-1.57'],
    ]

    for i, header in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = header
        for paragraph in cell.text_frame.paragraphs:
            paragraph.font.size = Pt(11)
            paragraph.font.bold = True
            paragraph.font.color.rgb = WHITE
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY

    for r, row_data in enumerate(data):
        for c, value in enumerate(row_data):
            cell = table.cell(r + 1, c)
            cell.text = value
            for paragraph in cell.text_frame.paragraphs:
                paragraph.font.size = Pt(11)
                paragraph.font.color.rgb = DARK_GRAY
                paragraph.alignment = PP_ALIGN.CENTER
            if r % 2 == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = LIGHT_GRAY


def build_slide_11_interpretation(prs):
    """SLIDE 11: INTERPRETATION"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, WHITE)
    add_slide_header(slide, 'Key Findings & Interpretation')

    # Three columns
    columns = [
        ('What Improved?', RGBColor(0xE3, 0xEF, 0xFC), [
            'QRNG-trained agents showed tighter inter-trial convergence (PPO, A2C)',
            'QRNG-trained PPO showed slight negative generalization gap (-1.57 pp) \u2014 marginally better cross-domain transfer',
        ]),
        ('Why No Significant\nDifference?', RGBColor(0xFC, 0xF0, 0xE3), [
            'Recursive backtracking algorithm acts as a structural bottleneck',
            'Constrains output diversity regardless of seed entropy quality',
            'Both seed sources passed identical randomness validation (Shannon entropy = 1.0)',
        ]),
        ('Limitations', RGBColor(0xF5, 0xE6, 0xE6), [
            'Limited to 20\u00d720 2D mazes and one generation algorithm',
            'DQN poorly suited to partial observability (LiDAR-based POMDP)',
            'QRNG constrained by API rate limits (71,800 seeds)',
        ]),
    ]

    col_width = 3.8
    gap = 0.3
    start_x = 0.6

    for i, (title, bg_color, items) in enumerate(columns):
        x = start_x + i * (col_width + gap)

        # Column box
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                        Inches(x), Inches(1.5), Inches(col_width), Inches(4.5))
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        shape.line.color.rgb = MEDIUM_GRAY

        # Column title
        add_textbox(slide, Inches(x + 0.2), Inches(1.6), Inches(col_width - 0.4), Inches(0.7),
                    title, font_size=16, bold=True, color=NAVY, alignment=PP_ALIGN.CENTER)

        # Column items
        add_bullet_list(slide, Inches(x + 0.2), Inches(2.5), Inches(col_width - 0.4), Inches(3.3),
                       items, font_size=13, color=DARK_GRAY)


def build_slide_12_technical(prs):
    """SLIDE 12: TECHNICAL OUTPUT / DEMO"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, WHITE)
    add_slide_header(slide, 'Implementation Evidence')

    # ERA Plot (bottom-left in spec, but let's use it prominently)
    era_path = os.path.join(FIGURES_DIR, 'era_plot.png')
    add_image_safe(slide, era_path, Inches(0.3), Inches(1.3), width=Inches(6.3), height=Inches(5.0))

    # Boxplot
    boxplot_path = os.path.join(FIGURES_DIR, 'boxplot_structural.png')
    add_image_safe(slide, boxplot_path, Inches(6.8), Inches(1.3), width=Inches(6.2), height=Inches(2.8))

    # A2C Training comparison
    a2c_path = os.path.join(BASE_DIR, 'a2c/outputs/training_comparison.png')
    add_image_safe(slide, a2c_path, Inches(6.8), Inches(4.3), width=Inches(6.2), height=Inches(2.8))


def build_slide_13_conclusions(prs):
    """SLIDE 13: CONCLUSIONS"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, WHITE)
    add_slide_header(slide, 'Conclusions')

    objectives = [
        ('Objective 1: Structural Diversity',
         'Fail to reject H\u2080 \u2014 No significant structural difference between PRNG and QRNG mazes\n(Mann-Whitney U: all p > 0.05, PERMANOVA: p = 0.7493)\nThe generation algorithm is the primary determinant of structural output.',
         RGBColor(0xE3, 0xEF, 0xFC)),
        ('Objective 2: Training Impact',
         'Fail to reject H\u2080 \u2014 Both seed conditions produced comparable training success rates and reward progression across A2C, DQN, and PPO over 10M timesteps.',
         RGBColor(0xFC, 0xF0, 0xE3)),
        ('Objective 3: Generalization',
         'Fail to reject H\u2080 \u2014 All generalization gaps within \u00b12.6 percentage points across all architectures. Seed-level randomness has no measurable impact on zero-shot generalization.',
         RGBColor(0xE8, 0xF5, 0xE3)),
    ]

    for i, (title, text, bg_color) in enumerate(objectives):
        y = 1.4 + i * 1.4
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                        Inches(0.6), Inches(y), Inches(12.1), Inches(1.25))
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        shape.line.color.rgb = MEDIUM_GRAY
        tf = shape.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = NAVY
        p2 = tf.add_paragraph()
        p2.text = text
        p2.font.size = Pt(12)
        p2.font.color.rgb = DARK_GRAY

    # Key takeaway box
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                    Inches(0.6), Inches(5.8), Inches(12.1), Inches(0.8))
    shape.fill.solid()
    shape.fill.fore_color.rgb = NAVY
    shape.line.fill.background()
    tf = shape.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = 'The recursive backtracking algorithm \u2014 not the entropy source \u2014 is the critical bottleneck for structural diversity in procedural maze generation.'
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.alignment = PP_ALIGN.CENTER


def build_slide_14_recommendations(prs):
    """SLIDE 14: RECOMMENDATIONS"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, WHITE)
    add_slide_header(slide, 'Recommendations for Future Work')

    recommendations = [
        'Use QRNG directly in maze generation via custom Fisher-Yates shuffle \u2014 bypass the Mersenne Twister intermediary entirely',
        'Test alternative generation algorithms (Wilson\'s, Prim\'s) that impose fewer structural constraints on output diversity',
        'Scale to larger mazes (30\u00d730, 40\u00d740) where structural memorization becomes harder and seed entropy may matter more',
        'Replace DQN with DRQN (recurrent variant) to fairly evaluate value-based methods under partial observability',
        'Investigate QRNG\'s training stability effect \u2014 the tighter PPO/A2C convergence clustering warrants study with 10+ trials',
    ]

    for i, rec in enumerate(recommendations):
        y = 1.5 + i * 1.05

        # Number
        circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.6), Inches(y + 0.1), Inches(0.4), Inches(0.4))
        circle.fill.solid()
        circle.fill.fore_color.rgb = ACCENT_BLUE
        circle.line.fill.background()
        tf = circle.text_frame
        p = tf.paragraphs[0]
        p.text = str(i + 1)
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.alignment = PP_ALIGN.CENTER

        # Text
        add_textbox(slide, Inches(1.2), Inches(y), Inches(11.5), Inches(0.9),
                    rec, font_size=15, color=DARK_GRAY)


def build_slide_15_thankyou(prs):
    """SLIDE 15: THANK YOU"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, WHITE)

    # Top accent bar
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), SLIDE_WIDTH, Inches(0.6))
    shape.fill.solid()
    shape.fill.fore_color.rgb = NAVY
    shape.line.fill.background()

    # Thank You
    add_textbox(slide, Inches(1), Inches(2.0), Inches(11.3), Inches(1.5),
                'Thank You',
                font_size=44, bold=True, color=NAVY, alignment=PP_ALIGN.CENTER)

    # Divider
    add_accent_line(slide, Inches(4.5), Inches(3.5), Inches(4.3))

    # Team info
    add_textbox(slide, Inches(1), Inches(4.0), Inches(11.3), Inches(0.5),
                'Antony, Aldrich Ryan V.  |  Baricante, Mark Angelo R.  |  Mirabel, Kevin Hans Aurick S.',
                font_size=16, color=DARK_GRAY, alignment=PP_ALIGN.CENTER)

    add_textbox(slide, Inches(1), Inches(4.6), Inches(11.3), Inches(0.5),
                'Adviser: John Richard M. Esguerra, MSCS',
                font_size=14, color=MEDIUM_GRAY, alignment=PP_ALIGN.CENTER)

    # Ready for Q&A
    add_textbox(slide, Inches(1), Inches(5.5), Inches(11.3), Inches(0.5),
                'We are ready for your questions.',
                font_size=18, bold=True, color=ACCENT_BLUE, alignment=PP_ALIGN.CENTER)

    # Bottom accent bar
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(6.9), SLIDE_WIDTH, Inches(0.6))
    shape.fill.solid()
    shape.fill.fore_color.rgb = NAVY
    shape.line.fill.background()


def main():
    prs = Presentation()
    prs.slide_width = SLIDE_WIDTH
    prs.slide_height = SLIDE_HEIGHT

    print('Building slides...')
    build_slide_1_title(prs)
    print('  Slide 1: Title - done')
    build_slide_2_overview(prs)
    print('  Slide 2: Overview - done')
    build_slide_3_research_gap(prs)
    print('  Slide 3: Research Gap - done')
    build_slide_4_objectives(prs)
    print('  Slide 4: Objectives - done')
    build_slide_5_conceptual(prs)
    print('  Slide 5: Conceptual Framework - done')
    build_slide_6_pipeline(prs)
    print('  Slide 6: Pipeline - done')
    build_slide_7_model_design(prs)
    print('  Slide 7: Model Design - done')
    build_slide_8_experimental_setup(prs)
    print('  Slide 8: Experimental Setup - done')
    build_slide_9_results(prs)
    print('  Slide 9: Results - done')
    build_slide_10_comparison(prs)
    print('  Slide 10: Comparison - done')
    build_slide_11_interpretation(prs)
    print('  Slide 11: Interpretation - done')
    build_slide_12_technical(prs)
    print('  Slide 12: Technical Output - done')
    build_slide_13_conclusions(prs)
    print('  Slide 13: Conclusions - done')
    build_slide_14_recommendations(prs)
    print('  Slide 14: Recommendations - done')
    build_slide_15_thankyou(prs)
    print('  Slide 15: Thank You - done')

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, 'thesis_defense_presentation.pptx')
    prs.save(output_path)
    print(f'\nPresentation saved to: {output_path}')
    print(f'Total slides: {len(prs.slides)}')


if __name__ == '__main__':
    main()
```

- [ ] **Step 2: Run the slide generation script**

```bash
cd /Users/angelobaricante/CS-Thesis-Model-Training && python3 presentation/generate_slides.py
```

Expected output:
```
Building slides...
  Slide 1: Title - done
  ...
  Slide 15: Thank You - done

Presentation saved to: .../presentation/output/thesis_defense_presentation.pptx
Total slides: 15
```

- [ ] **Step 3: Verify the output file exists and has reasonable size**

```bash
ls -lh presentation/output/thesis_defense_presentation.pptx
```

Expected: File exists with size > 100KB (includes embedded images).

---

### Task 4: Generate and Verify Final Presentation

**Files:**
- Run: `presentation/generate_figures.py` (generates figure PNGs)
- Run: `presentation/generate_slides.py` (generates PPTX)
- Verify: `presentation/output/thesis_defense_presentation.pptx`

- [ ] **Step 1: Run full pipeline**

```bash
cd /Users/angelobaricante/CS-Thesis-Model-Training
python3 presentation/generate_figures.py && python3 presentation/generate_slides.py
```

- [ ] **Step 2: Open and visually inspect the presentation**

```bash
open presentation/output/thesis_defense_presentation.pptx
```

Verify all 15 slides are present and check:
- Slide 1: Title, names, date visible
- Slides 5-8: Methodology content readable
- Slide 9: Histogram image embedded correctly
- Slide 10: PPO training curves visible, evaluation table readable
- Slide 12: ERA plot and boxplot visible
- Slide 13: Three conclusion blocks with navy takeaway box

- [ ] **Step 3: Commit all presentation files**

```bash
git add presentation/
git commit -m "Add thesis defense presentation generator and output"
```
