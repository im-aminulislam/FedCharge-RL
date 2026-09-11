# Validation record

Preparation date: 2026-09-07. Runtime: Python 3.12.13 on Linux.

## Executed checks

- `python3 -m unittest discover -s tests -v`: **12 tests passed**.
- Quick configuration: completed 2 seeds and 126 evaluation rows.
- Benchmark configuration: completed 5 seeds and 1,260 evaluation rows, with 3,600 training-log rows.
- Physics tests: per-slot energy balance, total requested/delivered/unmet balance, grid and port caps, active-session eligibility, and departure penalties across all actions.
- Analytical example: hand-calculated solar/grid energy split, cost, and terminal reward matched simulation output.
- Learning tests: weighted averaging, table independence, terminal/nonterminal TD targets, reproducible training, and nonzero learned updates.
- Integration test: paired evaluation scenarios across methods, all report artifacts, transition accounting, and protection against overwriting existing output.

The complete measured benchmark is in `results/example/`. The quick run is a preparation check and is excluded from the packaged evidence to keep one canonical example run.

## Result interpretation

EDF achieved a mean reward of −48.265 versus −62.928 for federated Q-learning. Federation's mean reward exceeded local Q-learning (−65.700) and pooled Q-learning (−65.530), but the five-seed experiment does not establish statistical significance. All observed results, including weaker learner performance, are retained.

- Offline Python wheel build completed successfully using existing build tools.
- Included checkpoint replay exactly reproduced the stored evaluation metrics for seed 11 / campus / day 0.
- Source fingerprint, raw CSV row counts, and README/document links were verified.

## Not executed or established

The extended configuration, GitHub-hosted CI matrix, real-hardware validation, networking, privacy attacks, and deployment were not run. The CI workflow is supplied for execution after upload. No claim of optimality, convergence, novelty, publication, or real-world performance follows from these tests.
