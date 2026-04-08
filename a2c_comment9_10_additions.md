# A2C Paragraph Additions for Comments 9 and 10

## Comment 9 Fix - Deep Interpretation (WHY results happened)

**Where to insert:** At the end of the A2C **Training** discussion, right after the paragraph that ends with *"...neither seed source producing a clear or consistent advantage across trials."* (p. 92 in PDF, last paragraph before *Deep Q-Network* heading)

**Paragraph to add:**

> The absence of a training advantage for either seed source can be directly attributed to the structural equivalence of the maze environments established in Section 4.1. Because the recursive backtracking algorithm constrains the output space to perfect mazes with fixed topological properties, regardless of whether the input seed originates from a deterministic or quantum source, both PRNG and QRNG training environments present statistically identical navigational challenges, as confirmed by the Mann-Whitney U tests (all p > 0.05) and PERMANOVA (p = 0.7493). Consequently, A2C agents trained on QRNG-seeded mazes encounter the same distribution of dead-ends, corridor lengths, and junction densities as those trained on PRNG-seeded mazes. The generation algorithm, not the entropy source, determines the structural diversity of the training distribution. Since both distributions are equivalent, neither seed source provides a richer or more varied set of experiences from which the agent can learn. This explains why A2C's convergence speed, final success rate, and reward progression remain comparable across both conditions.

---

## Comment 10 Fix - Technical Explanation (exploration vs exploitation)

**Where to insert:** In the A2C **Generalization** discussion, right after the paragraph that references Kirk et al. (2023) and ends with *"...due to their continual adaptation to the current data distribution."* (This is in the generalization subsection, before the Path Efficiency heading)

**Paragraph to add:**

> From an exploration-exploitation perspective, A2C's exploration behavior is primarily governed by the entropy bonus coefficient in the policy loss function, which encourages the agent to maintain stochastic action selection and avoid premature convergence to a deterministic policy. This entropy-driven exploration operates independently of the maze structure. The agent samples actions from its learned probability distribution over the discrete action space, regardless of whether the current maze was generated from a PRNG or QRNG seed. Since both seed sources produce mazes with equivalent distributions of dead-ends, branching junctions, and corridor configurations, the exploration-exploitation trade-off remains unchanged across conditions. Neither environment provides inherently greater exploration variability. An agent navigating a QRNG-seeded maze encounters a comparable frequency of decision points (degree-3 and degree-4 junctions) and exploration traps (dead-ends) as one navigating a PRNG-seeded maze. As a result, the policy's balance between exploiting known rewarding paths and exploring novel corridors develops at the same rate under both training conditions, which further explains the comparable generalization gaps observed.
