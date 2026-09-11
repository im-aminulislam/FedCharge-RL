# Methods and measurement protocol

## Synthetic data

Each episode is one station-day with 96 slots of 0.25 hours. A station specifies the number of sessions, mean arrival hour, installed solar power, grid-import limit, number of ports, and power per port. Defaults are 6 ports, 0.35 kW per port, and 1.5 kW maximum grid import.

Arrival slots are rounded Gaussian draws with standard deviation 9 slots, clipped to slots 0–88. Dwell time is a discrete uniform draw of 8–28 slots, clipped at the end of the day. Requested energy is uniform from 0.3 to 1.1 kWh. No guarantee is made that all requests are physically feasible; overloaded or short-dwell sessions can remain unmet even under good scheduling.

Solar output is a sine-shaped curve between 06:00 and 18:00, scaled by installed capacity and a daily uniform cloud factor in [0.5, 1.0]. There is no intra-day cloud noise. Electricity prices are synthetic USD/kWh: 0.10 before 07:00 and from 21:00, 0.18 from 07:00–16:00, and 0.38 from 16:00–21:00. These are not current utility tariffs.

| Station | Sessions/day | Mean arrival hour | Installed solar kW |
| --- | ---: | ---: | ---: |
| Campus | 40 | 9 | 1.2 |
| Commuter | 55 | 17 | 0.5 |
| Mixed use | 65 | 12 | 0.8 |

Scenario randomness is drawn completely before policy execution. Policy actions do not consume the scenario RNG or change future arrivals. Training and evaluation use distinct string seed namespaces. Both use the same station distributions; evaluation is held out by day, not by station or distribution.

## Event order and constraints

At slot t:

1. Identify arrived, unfinished sessions with `arrival <= t < departure`.
2. Construct the observation using the current tariff and solar output.
3. Select a dispatch ordering and an energy budget.
4. Select at most `ports` sessions in that order. Allocate at most `port_kw × 0.25` kWh and no more than each session's remaining request. A port cannot be reassigned mid-slot, even if its session finishes early.
5. Use solar first; import any remaining required energy within `grid_kw × 0.25` kWh. Surplus solar is curtailed. No battery storage or export exists.
6. Penalize remaining energy for sessions departing at t+1, then advance time.

Allocations are preemptive between slots. Grid limits apply independently to stations; there is no shared transformer constraint. Conversion efficiency is idealized as 100%. All requested energy has a departure deadline no later than slot 96, so terminal unmet demand is accounted for.

Energy identities over a day:

```text
requested = delivered + unmet
 delivered = solar used + grid imported
 sum(slot departure shortfalls) = final unmet
```

Tests check these identities and per-session temporal and power constraints.

## Observation and action abstraction

Observation factors: 6 four-hour time bins; 3 tariff tiers; 3 queue bins (empty, 1–ports, >ports); 2 urgency bins (any active session departing within 4 slots); 2 solar bins (solar power at least one port's rating).

This yields 216 possible encoded states and 5 dispatch actions. Some state combinations are unreachable under the fixed tariff. Different underlying queues can share a state, so the observation is not generally Markov. The policy chooses among heuristics; it cannot represent arbitrary continuous-power scheduling.

## Training

All tables start at zero. Epsilon-greedy exploration uses `epsilon = max(epsilon_end, epsilon_start × epsilon_decay^round_index)`. Exploration RNGs are deterministic and separate from scenario generation. Equal Q-values use EDF-first deterministic ordering.

Each federated round starts every client from a copy of the same global table. Clients perform standard one-step Q-learning on their own episodes. The server computes the transition-weighted arithmetic mean of complete tables. All clients participate in every round; no client sampling, dropout, asynchronous updates, compression, or robustness mechanism is implemented. Equal fixed episode budgets mean equal weights.

Local learners retain their own tables throughout training. The pooled learner retains one table and processes the same episodes in round/client/day order. Every learning method sees the same exogenous training scenarios and receives the same total transition budget; learning dynamics and state/action visits differ.

Terminal targets contain only the immediate reward. Constant learning rate, state aliasing, finite training, and heterogeneous-table averaging mean that classical asymptotic tabular convergence conditions are not established here.

## Evaluation and metrics

Evaluation disables exploration and updates. Each seed/station/day scenario is reused for all seven methods. No evaluation reward is used for early stopping or checkpoint selection. The final-round policy is evaluated.

| Metric | Definition | Interpretation |
| --- | --- | --- |
| Reward | Delivered kWh − cost USD − 4 × unmet kWh | Higher utility under the chosen numerical weights |
| Cost | Sum of grid kWh × price | Lower can reflect serving less demand |
| Delivered energy | Total session energy supplied | Higher does not by itself imply efficiency |
| Unmet energy | Energy remaining at all departures | Lower is better |
| Energy fulfillment | Delivered/requested energy | Service fraction, not battery efficiency |
| Completion rate | Fully served sessions/all sessions | Partial sessions do not count as complete |
| Solar fraction | Solar used/delivered energy | Zero when no energy is delivered |
| Peak grid kW | Largest slot grid energy / 0.25 | Station-day peak, not simultaneous network peak |

The report first averages all station-days within each seed, then reports the mean and sample SD of those seed-level means. Each station has equal weight in this macro-average despite different demand volumes. Peak power is also averaged across station-days; it is not the maximum across the entire experiment.

`paired_deltas.csv` stores per-seed averages of federated-minus-comparator differences on matched station-days. Positive reward or fulfillment deltas favor federation; negative cost or unmet deltas favor federation on that metric. Interpret cost alongside service. No confidence interval, p-value, or significance claim is produced. With one seed, the output convention uses SD=0; this is not evidence of low uncertainty.

## Communication estimate

An idealized float64 table has 216 × 5 × 8 = 8,640 bytes. Each round counts one upload and one broadcast per client: `2 × clients × rounds × 8640`. The benchmark therefore estimates 1,036,800 bytes per seed. This is analytical numeric payload, not measured network traffic. JSON checkpoints, transport headers, retries, and metadata are excluded.

## Sources

[Watkins and Dayan (1992)](https://www.gatsby.ucl.ac.uk/~dayan/papers/cjch.pdf) provides the Q-learning foundation. [McMahan et al. (2017)](https://proceedings.mlr.press/v54/mcmahan17a.html) motivates federated model averaging. Averaging Q-tables in this project is a pedagogical adaptation, not their neural-network training implementation.
