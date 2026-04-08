# Thesis Final Defense Presentation Design Spec

## Overview

Design specification for the CS Thesis Final Defense PowerPoint presentation for "Enhancing Autonomous Navigation Robustness in Unstructured Environments using Quantum-Seeded Procedural Maze Generation."

**Defense Date:** April 8, 2026
**Team:** Antony, Aldrich Ryan V. / Baricante, Mark Angelo R. / Mirabel, Kevin Hans Aurick S.
**Adviser:** John Richard M. Esguerra, MSCS
**Institution:** Batangas State University, College of Informatics and Computing Sciences

## Strategic Framing: "The Rigorous Benchmark"

The presentation frames the study as a rigorous empirical benchmark that answers a question nobody had tested before. The null result IS the contribution -- the study proved the generation algorithm is the structural bottleneck, not the seed entropy source. This framing directly addresses the risk of panelists questioning why QRNG showed no significant advantage.

Key messaging principles:
- Never apologize for null results -- present them as scientific discovery
- Emphasize methodological rigor (71,800 seeds, 3 DRL architectures, 3 trials, statistical validation)
- The bottleneck finding provides clear guidance for future researchers
- Subtle positive signals (QRNG convergence stability) are mentioned but not oversold

## Constraints

- **Slide count:** Strictly 15 slides per the required presentation template
- **Duration:** ~17 minutes total presentation
- **Style:** Minimalist, academic/university aesthetic
- **Design rules:** Minimal text (no paragraphs), use diagrams/charts/tables, readable font, clean layout
- **Member split:** 3 members, assignments TBD (Member 1: Problem+Objectives, Member 2: Methodology, Member 3: Results+Conclusion)
- **All existing figures/diagrams from the thesis are available** for direct use in slides

## Time Allocation

| Slides | Section | Duration | Rubric Weight |
|--------|---------|----------|---------------|
| 1-4 | Problem + Objectives | ~3 min | 10% |
| 5-8 | Methodology | ~6 min | 15% |
| 9-11 | Results + Analysis | ~5 min | 15% |
| 12 | Technical Output | ~1 min | 5% |
| 13-14 | Conclusions + Recommendations | ~2 min | 5% |
| 15 | Thank You / Q&A | -- | -- |

## Slide-by-Slide Specification

---

### SLIDE 1: TITLE SLIDE

**Content:**
- Title: "Enhancing Autonomous Navigation Robustness in Unstructured Environments using Quantum-Seeded Procedural Maze Generation"
- Members: Antony, Aldrich Ryan V. / Baricante, Mark Angelo R. / Mirabel, Kevin Hans Aurick S.
- Adviser: John Richard M. Esguerra, MSCS
- Panel Members: [to be filled]
- Date: April 8, 2026
- BatStateU logo

**Design:** Clean, centered text hierarchy. Title prominent, names smaller below.

---

### SLIDE 2: OVERVIEW OF THE STUDY

**Content:**
- Background (2-3 bullets):
  - "Procedural Content Generation (PCG) relies on PRNGs to create training environments for DRL agents"
  - "QRNGs provide true randomness from quantum phenomena -- but have never been tested in PCG"
- Research Problem: "Does the source of seed-level randomness affect maze structural diversity and DRL agent generalization?"
- Motivation: "DRL agents overfit to training environments; structural randomization is underexplored vs. visual domain randomization"

**Design:** Three distinct blocks -- Background, Problem, Motivation. Short bullet points only.

---

### SLIDE 3: RESEARCH GAP

**Content:**
- Three bullets:
  - "Existing PCG studies exclusively use PRNGs -- no empirical evaluation of QRNG in procedural generation"
  - "Domain randomization research focuses on visual changes (textures, lighting), not structural randomization"
  - "No study has tested whether true quantum entropy improves DRL zero-shot generalization"
- Visual: Simple diagram showing two established domains (QRNG in cryptography, PRNG in PCG) with an unexplored intersection

**Design:** Diagram takes 60% of slide, bullets take 40%.

---

### SLIDE 4: OBJECTIVES OF THE STUDY

**Content:**
- General Objective: "Evaluate the impact of QRNG vs. PRNG seeds on procedural maze generation and DRL agent navigation"
- Specific Objectives:
  1. "Determine how PRNG and QRNG influence structural complexity and diversity of mazes (path length, tortuosity, dead-ends)"
  2. "Determine the extent QRNG-based sources impact training of DRL agents (success rate, rewards)"
  3. "Evaluate generalization performance of QRNG-trained vs. PRNG-trained agents on unseen mazes"

**Design:** General objective at top, three numbered specific objectives below. Each objective concise (1-2 lines max).

---

### SLIDE 5: CONCEPTUAL / SYSTEM OVERVIEW

**Content:**
- Visual: Conceptual Framework Diagram (Figure 5 from thesis)
- Brief labels showing three-stage flow:
  - Input: PRNG seeds (Mersenne Twister) + QRNG seeds (ANU Quantum API) + Recursive Backtracking
  - Process: Maze Generation, Structural Evaluation, DRL Training, Generalization Testing
  - Output: Maze comparison, RL performance evaluation, QRNG suitability assessment

**Design:** Diagram takes 80% of slide. Minimal surrounding text.

**Source figure:** Conceptual Framework Diagram (thesis Figure 5, p.38)

---

### SLIDE 6: OVERALL PIPELINE

**Content:**
- Clean numbered flowchart, 7 steps:
  1. Generate Seeds (PRNG: Mersenne Twister 64-bit / QRNG: ANU API with bitwise concatenation to 64-bit)
  2. Validate Seed Quality (Shannon Entropy, Autocorrelation)
  3. Generate Mazes (Recursive Backtracking, 20x20 grid, 71,800 per group)
  4. Extract Maze Metrics (path length, tortuosity, dead-ends, junction proportions)
  5. Train DRL Agents (A2C, DQN, PPO -- 10M timesteps, 3 trials each)
  6. Evaluate Generalization (1,000 unseen mazes: intra-domain + cross-domain)
  7. Statistical Comparison (Shapiro-Wilk, Mann-Whitney U, PERMANOVA)

**Design:** Vertical or horizontal flowchart with numbered boxes and arrows. Minimal text per box.

---

### SLIDE 7: MODEL / ALGORITHM DESIGN

**Content:**
- Split into two visual panels:
- Left panel -- Environment Design:
  - 20x20 maze grid illustration
  - Observation: 10-dim vector (8 LiDAR rays + 2D target direction)
  - Action space: {Up, Down, Left, Right}
  - Reward structure (simplified): Goal +250, Wall -0.75, Step -0.005, Timeout -7, New Cell +2.0, Progress +0.5x
- Right panel -- DRL Architectures:
  - Diagram: Input(10) -> MLP Hidden Layers -> Output(4 actions)
  - Three models: A2C (MLP 64,64), DQN (MLP 256,256), PPO (MLP 256,256)
  - One-line rationale: "Three DRL families to benchmark the randomness source, not the model"

**Design:** Two-column layout. Left = environment, Right = model architecture. Clean separation.

---

### SLIDE 8: EXPERIMENTAL SETUP

**Content:**
- Dataset: 71,800 PRNG seeds + 71,800 QRNG seeds = 143,600 total mazes
- Train/Test: ~35,000-40,000 training mazes / 1,000 unseen evaluation mazes per condition
- Hyperparameters table:

| Parameter | DQN | A2C | PPO |
|-----------|-----|-----|-----|
| Learning Rate | 1x10^-3 | 7x10^-4 | 3x10^-4 |
| Network | MLP(256,256) | MLP(64,64) | MLP(256,256) |
| Timesteps | 10M | 10M | 10M |
| Trials | 3 | 3 | 3 |

- Tools: Python, Stable-Baselines3, Gymnasium, scipy.stats, ANU Quantum API

**Design:** Table prominent in center. Dataset/tools info above and below.

---

### SLIDE 9: PERFORMANCE RESULTS

**Content:**
- Title: "Maze Structural Analysis: PRNG vs QRNG"
- Left side: Histogram figure (thesis Figure 6) -- overlapping distributions for path length, tortuosity, dead-end count
- Right side: Key numbers callout box:
  - Path Length: PRNG mean=87.50 vs QRNG mean=87.51
  - Tortuosity: both mean=2.57, median=2.47
  - Dead-ends: both mean=11.84, median=12.00
- Bottom strip: Statistical validation summary:
  - Mann-Whitney U: all p > 0.05 (no significant difference)
  - PERMANOVA: p = 0.7493 (no multivariate effect)
  - ERA hull areas: PRNG=0.0131 vs QRNG=0.0125
- Takeaway line: "The maze generation algorithm -- not the seed source -- determines structural output"

**Design:** Two-column top (chart + numbers), one-row bottom (stats). Takeaway in bold at bottom.

**Source figures:** Thesis Figure 6 (p.78)

---

### SLIDE 10: COMPARISON WITH BASELINE

**Content:**
- Title: "DRL Agent Performance: QRNG-trained vs PRNG-trained"
- Top half: PPO training curves side-by-side (thesis Figure 12)
  - PRNG: one trial collapsed, higher variance
  - QRNG: tighter clustering, consistent convergence
  - Caption: "PPO training curves -- QRNG showed more consistent convergence"
- Bottom half: Consolidated evaluation table:

| Algorithm | Agent | Intra SR | Cross SR | Gap (pp) |
|-----------|-------|----------|----------|----------|
| A2C | PRNG | 61.20% | 60.30% | +0.90 |
| A2C | QRNG | 58.70% | 59.50% | -0.80 |
| DQN | PRNG | 11.03% | 12.37% | -1.33 |
| DQN | QRNG | 9.80% | 8.97% | +2.57 |
| PPO | PRNG | 73.27% | 71.53% | +1.74 |
| PPO | QRNG | 72.43% | 74.00% | -1.57 |

- Takeaway: "All generalization gaps within +/-2.6 pp -- no consistent advantage for either seed source"

**Design:** Two-row layout. Training curves on top, table on bottom. Keep table compact.

**Source figures:** Thesis Figure 12 (p.96)

---

### SLIDE 11: INTERPRETATION

**Content:**
- Title: "Key Findings & Interpretation"
- Three-block layout:
- Block 1 -- "What improved?"
  - "QRNG-trained agents showed tighter inter-trial convergence (PPO, A2C)"
  - "QRNG-trained PPO showed slight negative generalization gap (-1.57 pp) -- marginally better cross-domain transfer"
- Block 2 -- "Why no significant difference?"
  - "Recursive backtracking algorithm acts as a structural bottleneck"
  - "Constrains output diversity regardless of seed entropy quality"
  - "Both seed sources passed identical randomness validation (Shannon entropy = 1.0)"
- Block 3 -- "Limitations"
  - "Limited to 20x20 2D mazes and one generation algorithm"
  - "DQN poorly suited to partial observability (LiDAR-based POMDP)"
  - "QRNG constrained by API rate limits (71,800 seeds)"

**Design:** Three equal-width columns or stacked blocks. Each with a header and 2-3 bullets. Clean separation.

---

### SLIDE 12: TECHNICAL OUTPUT / DEMO

**Content:**
- Title: "Implementation Evidence"
- Grid layout of 4 visual panels:
  - Top-left: Sample PRNG maze vs sample QRNG maze side-by-side
  - Top-right: Screenshot of training logs / terminal output
  - Bottom-left: ERA plot (thesis Figure 9 -- overlapping convex hulls)
  - Bottom-right: Boxplot comparison (thesis Figure 7)

**Design:** 2x2 grid, minimal captions. Purely visual proof of working implementation.

**Source figures:** Thesis Figure 9 (p.83), Figure 7 (p.79), plus maze screenshots and training logs from the repo.

---

### SLIDE 13: CONCLUSIONS

**Content:**
- Title: "Conclusions"
- Three numbered blocks mapped to objectives:
  1. Objective 1 (Structural Diversity): "Fail to reject H0 -- No significant structural difference (Mann-Whitney U: all p > 0.05, PERMANOVA: p = 0.7493). The generation algorithm is the primary determinant."
  2. Objective 2 (Training Impact): "Fail to reject H0 -- Both seed conditions produced comparable training success rates and reward progression across A2C, DQN, and PPO."
  3. Objective 3 (Generalization): "Fail to reject H0 -- All generalization gaps within +/-2.6 pp. Seed-level randomness has no measurable impact on zero-shot generalization within this scope."
- Bottom callout (bold): "The recursive backtracking algorithm -- not the entropy source -- is the critical bottleneck for structural diversity in procedural maze generation."

**Design:** Three stacked blocks with objective number. Bottom callout in a highlighted box. This is the most important sentence of the entire presentation.

---

### SLIDE 14: RECOMMENDATIONS

**Content:**
- Title: "Recommendations for Future Work"
- Five bullets:
  1. "Use QRNG directly in maze generation (custom Fisher-Yates shuffle) -- bypass the Mersenne Twister intermediary"
  2. "Test alternative generation algorithms (Wilson's, Prim's) that impose fewer structural constraints"
  3. "Scale to larger mazes (30x30, 40x40) where structural memorization is harder"
  4. "Replace DQN with DRQN to fairly evaluate value-based methods under partial observability"
  5. "Investigate QRNG's training stability effect (tighter PPO/A2C convergence) with more trials"

**Design:** Clean numbered list. Each recommendation is one line.

---

### SLIDE 15: THANK YOU

**Content:**
- "Thank You"
- Group members and adviser
- "We are ready for your questions."

**Design:** Centered, clean. No clutter.

---

## Presentation Member Assignment (Suggested)

| Member | Slides | Section | Duration |
|--------|--------|---------|----------|
| Member 1 | 1-4 | Problem + Objectives | ~3 min |
| Member 2 | 5-8 | Methodology | ~6 min |
| Member 3 | 9-14 | Results + Conclusions + Recommendations | ~8 min |

**Note:** Member 3 has the most slides but slides 12-15 are fast (visual proof + bullet lists). Member 2 has fewer slides but the densest content. The team should assign based on who can best explain technical methodology vs. who can best defend the null results with confidence.

**All members must be prepared to answer Q&A on all sections.**

## Visual Design Guidelines

- **Style:** Minimalist, academic/university aesthetic
- **Colors:** Stick to 2-3 colors max -- a primary dark color (navy or dark gray), an accent color, and white background
- **Fonts:** Clean sans-serif (e.g., Calibri, Helvetica, or similar). Title: 28-32pt, Body: 18-22pt, Captions: 14-16pt
- **Charts/figures:** Use directly from thesis -- they are already well-formatted
- **Tables:** Minimal borders, alternating row shading for readability
- **Slide density:** Max 5-6 bullet points per slide. If a slide feels crowded, it is crowded.
- **No paragraphs on any slide**

## Q&A Preparation Notes

The following questions are likely given the null result framing:

### Methodology questions:
- "Why did you use QRNG seeds to initialize Mersenne Twister instead of using quantum bits directly?" -- Answer: Technical constraint of Python's random module. This is acknowledged as a limitation and listed as Recommendation #1.
- "Why these specific hyperparameters?" -- Answer: Empirically determined per algorithm to ensure each operated within its stability region. Common environmental parameters held constant to isolate the seed source.
- "Why only 3 trials?" -- Answer: Computational constraint on local hardware. Acknowledged as limitation; Recommendation #5 suggests 10+ runs.

### Results questions:
- "If there's no significant difference, what's the contribution?" -- Answer: The study is the first empirical test of QRNG in PCG. It established that the generation algorithm is the bottleneck, providing clear direction for future research. The benchmarking framework itself is a contribution.
- "Why did DQN perform so poorly?" -- Answer: DQN is architecturally incompatible with partial observability (POMDP). It treats each observation as a complete state, which fails in LiDAR-only maze navigation. This is consistent with Hausknecht & Stone (2017).
- "Why did QRNG show tighter convergence in PPO/A2C?" -- Answer: An observed trend but not statistically validated with only 3 trials. Could be meaningful or could be an artifact. Listed as Recommendation #5 for future work.

### Validation questions:
- "Is the result statistically valid with your sample sizes?" -- Answer: Yes. 71,800 seeds per group, sub-sampled to n=5,000 for Shapiro-Wilk sensitivity. Mann-Whitney U and PERMANOVA are appropriate non-parametric tests for non-normal distributions.
- "How generalizable is this finding?" -- Answer: Generalizable within recursive backtracking on 20x20 grids. Other algorithms, larger sizes, and higher dimensions remain open questions (explicitly stated as recommendations).
