# Pseudocode for Chapter 3 (Methodology)

## Placement

**Where:** Section 3.2, after the "Mathematical Model and Algorithm Design" subsection (around page 48), before "Deep Reinforcement Learning Implementation."

**Intro sentence:**
> To provide a complete overview of the experimental methodology, Algorithm 1 presents the full pipeline used in the study, following the order of the methodology from seed generation through statistical comparison.

---

## Algorithm 1: QRNG vs PRNG Training Pipeline

```
INPUT:
    71,800 PRNG seeds (Mersenne Twister, 64-bit)
    71,800 QRNG seeds (ANU Quantum API, 64-bit)
    Grid size = 20 × 20
    Algorithms = A2C, DQN, PPO
    Training timesteps = 10,000,000
    Evaluation mazes = 1,000 per condition

BEGIN

    // ─── Step 1: Generate Seeds ───
    Generate PRNG seeds using Python random module (Mersenne Twister)
    Fetch QRNG seeds from ANU Quantum API as uint16 blocks
    Concatenate every 4 blocks bitwise into one 64-bit integer
    Save both seed sets to CSV

    // ─── Step 2: Validate Seed Quality ───
    FOR each seed set (PRNG and QRNG):
        Compute Shannon Entropy
        Compute Autocorrelation at multiple lags
        Confirm entropy is near maximum and autocorrelation is near zero
    END FOR

    // ─── Step 3: Generate Mazes ───
    FOR each seed set (PRNG and QRNG):
        FOR each seed in the set:
            Create a 20 × 20 grid filled with walls
            Seed the random number generator with the current seed
            Carve paths using Recursive Backtracking starting from (1, 1)
            Set start = (1, 1) and goal = (18, 18)
            Store the resulting maze
        END FOR
    END FOR

    // ─── Step 4: Extract Maze Metrics ───
    FOR each generated maze:
        Build a cell graph from open (walkable) cells
        Find shortest path from start to goal using Dijkstra
        Compute tortuosity = shortest path length / Manhattan distance
        Collapse cell graph into corridor graph (merge straight chains)
        Count dead-ends, junctions, degree-3 and degree-4 nodes
        Compute junction proportions (p3, p4)
        Count straight vs turning corridors and mean turns per corridor
        Compute linearity and leniency for Expressive Range Analysis
    END FOR

    // ─── Step 5: Train DRL Agents ───
    FOR each algorithm (A2C, DQN, PPO):
        FOR each seed source (PRNG, QRNG):
            Repeat 3 training runs and average results:
                Set up parallel maze environments with LiDAR observations
                    (8 ray-cast distances + 2D target direction = 10 inputs)
                Stack 4 consecutive frames as input
                Train agent for 10,000,000 timesteps using shaped reward
                Log episode reward, success rate, and steps per episode
            Save trained model weights
        END FOR
    END FOR

    // ─── Step 6: Evaluate Generalization ───
    FOR each trained agent:
        Freeze model weights (no further learning)
        Intra-domain test: run on 1,000 unseen mazes from same seed source
        Cross-domain test: run on 1,000 unseen mazes from opposite seed source
        Record success rate, average reward, and average steps
        Compute Generalization Gap = Intra success rate − Cross success rate
    END FOR

    // ─── Step 7: Statistical Comparison ───
    FOR each maze structural metric:
        Test normality using Shapiro-Wilk (sample of 5,000)
        IF both groups are normal:
            Compare using Welch t-test
        ELSE:
            Compare using Mann-Whitney U test
        END IF
    END FOR
    Run PERMANOVA on all non-normal metrics combined
        (z-score normalized, Euclidean distance, 1,000 permutations)
    Report significance at α = 0.05

END
```

---

## Notes

1. This goes in **Section 3.2** as a single algorithm block. No appendix sub-algorithms needed — this is self-contained.

2. **Table cross-references** within your paper: the "shaped reward" refers to Table 1 (Reward Function Structure), the training hyperparameters refer to Table 3 (Common Environmental Parameters) and Table 4 (Algorithm-Specific Configurations).

3. **Formatting tip:** In your Word document, use Courier New 10pt inside a bordered box, or whatever algorithm formatting your school template requires.

4. **Per Aldrich's note:** Steps follow the methodology order, not the dean's suggested numbering.
