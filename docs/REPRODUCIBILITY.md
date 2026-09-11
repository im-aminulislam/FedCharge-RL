# Reproducing and inspecting experiments

## Local execution

Use Python 3.10+ from the root of the extracted repository. Check the exact Python version with `python --version`.

```bash
python -m unittest discover -s tests -v
python -m fedcharge.experiment --config configs/benchmark.json --out results/reproduction
```

No environment variables or credentials are needed. The direct command uses only the standard library. For complete run provenance, keep the output folder and exact source revision together.

## Files produced

| File | Contents |
| --- | --- |
| `evaluation.csv` | One row per seed, station, held-out day, and algorithm |
| `training.csv` | Episode reward during exploration, indexed by round, client, and method |
| `summary.csv` | Seed-level mean and sample SD for each metric |
| `paired_deltas.csv` | Seed-level paired federated-minus-baseline metric differences |
| `trace.csv` | All slots for all seven methods on the first evaluated station-day |
| `checkpoint-SEED.json` | Final federated, local, and pooled Q-tables plus config |
| `metadata.json` | Config, Python/platform, source SHA-256, transition and communication accounting |
| `RESULTS.md` | Human-readable result table |
| `report.html` | Offline report with exact configuration and raw-file links |

Training reward contains exploration and is not a held-out learning curve. The trace is one illustrative day, not the entire evaluation. Full raw day-level results are retained for per-station analysis.

The source fingerprint hashes sorted package Python filenames and bytes, not the entire Git repository. Record the commit hash as well after upload. Report/metadata platform fields may differ across computers. Seed namespaces and algorithm execution are deterministic on the same Python/runtime; exact float identity across all Python versions/platforms is not promised.

## Changing an experiment

Copy a configuration to a new file and edit its rounds, seeds, episode budgets, learning parameters, or station definitions. Use a new output path. The configuration is validated and embedded in metadata and checkpoints. For source-level changes to observation or reward, retain the source revision because the JSON alone does not define these choices.

There is no automatic resume mode. JSON checkpoints support inspection and inference; training starts from zero on each run. Do not mix partial outputs from different configurations.

## Planning stronger evidence

Before tuning hyperparameters, reserve separate validation and final-test seed namespaces in the runner. Tune only on validation data, then evaluate the locked design once on final test data. Increase independent training seeds, report per-client outcomes, and predefine the primary metric. The supplied runner currently provides training and evaluation splits only.

## Installation and operating systems

Direct execution works without pip installation. Optional editable installation needs setuptools and may require network access. The npm scripts assume a command named `python`; use direct `python3` or Windows `py -3` commands if needed.

A GitHub Actions workflow is supplied for Python 3.10–3.13 on Ubuntu. Its status is only known after it runs in your repository; a workflow file is not proof of a passing remote run.
