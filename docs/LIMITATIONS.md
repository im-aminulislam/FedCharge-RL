# Limitations and responsible interpretation

- **Synthetic only:** No real utility tariffs, charging traces, or measured station data are included. All demand and weather follow simplified distributions.
- **E-bike scale:** Power and energy assumptions represent a small e-bike charging scenario, not high-power passenger-car charging.
- **Partial observability:** Compact observations omit the detailed queue and energy requests. Do not claim that this is a fully observed MDP or invoke a convergence theorem without further analysis.
- **Restricted policy space:** RL selects among dispatch rules. It does not learn individual continuous charging rates.
- **Simple federation:** Clients are emulated sequentially within one process; tables are synchronously averaged. No networking, secure aggregation, differential privacy, encryption, or poisoning defense exists.
- **No formal privacy:** Keeping trajectories local during the federated update is a data-flow design choice. Updates and logs can expose information. In this prototype all data are synthetic and the runner can access every client.
- **Idealized physics:** No battery state-of-charge dynamics, degradation, voltage variation, thermal limits, efficiency losses, or charger protocol integration is modeled. Energy service is not a battery-safety model.
- **Independent stations:** Stations share a policy, not a shared power constraint. There is no feeder-level optimization.
- **No real deployment:** ESP32, MQTT, cloud services, and hardware control are future integrations, not completed features.
- **Limited evidence:** The bundled benchmark has five training seeds and three fixed client distributions. Evaluation days are new, but clients are not unseen. The extended configuration has not been used to generate the bundled results.
- **No optimal benchmark:** Heuristics and pooled Q-learning are comparators, not an oracle. A cost-minimizing solver subject to service constraints is a useful future addition.
- **Reward sensitivity:** Fixed reward weights reflect an assumed preference. Small coefficients can change rankings. No weight-tuning or sensitivity study is claimed.
- **No wait-time claim:** First-service waiting time and user fairness are not currently reported. Do not infer them from completion or energy metrics.
- **No publication claim:** This repository has no associated peer-reviewed paper, DOI, confirmed novelty, or guaranteed performance gain.

AI assisted the initial code and documentation. Before presenting this portfolio in an interview, review the implementation, reproduce results, and explain the choices and tradeoffs in your own words. Add independently verified contributions through clear commits rather than presenting planned extensions as completed work.
