# FedCharge-RL — measured example results

Synthetic e-bike charging simulation. Mean ± sample SD across seed-level means; each seed averages all evaluation days and stations. SD is not a confidence interval. Lower cost may reflect unmet demand: compare fulfillment and reward together.

| Scheduler | Reward ↑ | USD/day ↓ | Energy fulfillment ↑ | Sessions complete ↑ | Solar fraction ↑ | Peak grid kW ↓ |
|---|---|---|---|---|---|---|
| edf | -48.265 ± 1.589 | 3.901 ± 0.046 | 0.586 ± 0.005 | 0.323 ± 0.011 | 0.192 ± 0.009 | 1.500 ± 0.000 |
| fcfs | -50.725 ± 1.616 | 3.747 ± 0.038 | 0.568 ± 0.006 | 0.432 ± 0.006 | 0.198 ± 0.009 | 1.500 ± 0.001 |
| federated_q | -62.928 ± 8.989 | 3.115 ± 0.564 | 0.500 ± 0.050 | 0.300 ± 0.044 | 0.222 ± 0.030 | 1.500 ± 0.000 |
| local_q | -65.700 ± 7.261 | 3.218 ± 0.295 | 0.491 ± 0.035 | 0.336 ± 0.029 | 0.204 ± 0.020 | 1.499 ± 0.002 |
| pooled_q | -65.530 ± 9.438 | 3.009 ± 0.483 | 0.485 ± 0.051 | 0.330 ± 0.058 | 0.221 ± 0.017 | 1.499 ± 0.002 |
| shortest_remaining | -56.470 ± 1.601 | 3.449 ± 0.054 | 0.533 ± 0.006 | 0.551 ± 0.005 | 0.210 ± 0.010 | 1.500 ± 0.001 |
| solar_only | -128.021 ± 1.536 | 0.000 ± 0.000 | 0.126 ± 0.006 | 0.022 ± 0.003 | 1.000 ± 0.000 | 0.000 ± 0.000 |

Configuration and environment: [metadata.json](metadata.json). Raw paired outcomes: [evaluation.csv](evaluation.csv).
