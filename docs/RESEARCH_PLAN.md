# Research extensions

These are proposed extensions, not implemented features or established findings.

| Question | Proposed experiment | Required evidence |
| --- | --- | --- |
| Does state compression hide useful information? | Add energy backlog and slack bins; compare with current observation | Locked evaluation seeds, table-size and coverage reporting |
| When does federation help? | Vary client arrival, demand, and solar heterogeneity | Per-client paired outcomes and negative-transfer analysis |
| How often should clients aggregate? | Vary local episodes while keeping total transitions constant | Service/reward versus communication payload |
| Is the service-cost tradeoff stable? | Sweep reward weights on a validation split | Final held-out test after weight selection |
| How close are policies to a strong benchmark? | Add a constrained optimization scheduler | Matching physical assumptions and a clear information-access budget |
| Does a global model transfer? | Hold out whole station distributions | Zero-shot evaluation and a separately measured adaptation budget |
| Can federation protect user data? | Define a threat model; add suitable privacy mechanisms | Measured privacy/utility tradeoff, not architecture-only claims |
| Can this run at the edge? | Profile inference; build a hardware-in-the-loop adapter | Timing, safety interlocks, and validation with charger experts |

## Suggested first independent contribution

Add a per-station results table using the existing evaluation CSV, then compare which client benefits or loses under federation. Form a hypothesis about arrival-time or solar heterogeneity, write it before a new run, and test it using an untouched evaluation configuration. This provides a focused contribution that can be explained clearly in a PhD discussion.

## Interview preparation

Be ready to explain: what a Q-value represents; why the action is a dispatch heuristic; how Q-table averaging differs from averaging raw data; why the observation is partially observable; how all methods receive identical evaluation scenarios; why cost alone is misleading; and why keeping data local does not prove privacy.
