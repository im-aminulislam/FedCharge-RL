"""Run training and paired evaluation; preserve raw evidence and configuration."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import platform
import statistics
import sys
from .environment import Station, ChargingEnv, generate, N_STATES, ACTIONS, SLOTS
from .learning import train, greedy, scenario_seed


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def validate(config):
    for key in ("rounds", "local_episodes", "eval_episodes"):
        if type(config[key]) is not int or config[key] < 1:
            raise ValueError(f"{key} must be a positive integer")
    seeds = config["seeds"]
    if not seeds or any(type(s) is not int for s in seeds) or len(set(seeds)) != len(seeds):
        raise ValueError("seeds must be distinct integers")
    for key in ("alpha", "gamma", "epsilon_start", "epsilon_end", "epsilon_decay"):
        if not 0 <= config[key] <= 1:
            raise ValueError(f"{key} must be in [0, 1]")
    if config["alpha"] == 0 or config["epsilon_end"] > config["epsilon_start"]:
        raise ValueError("Invalid learning rate or epsilon schedule")
    stations = [Station(**s) for s in config["stations"]]
    if len(stations) < 2 or len({s.name for s in stations}) != len(stations):
        raise ValueError("Use at least two uniquely named stations")
    return stations


def run(config, out):
    stations = validate(config)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    if any(out.iterdir()):
        raise ValueError("Output directory must be empty to protect previous experiments")
    rows, history, traces = [], [], []
    for seed in config["seeds"]:
        global_q, local, pooled, log = train(stations, config, seed)
        history.extend(log)
        checkpoint = {"schema_version": 1, "seed": seed, "config": config,
                      "federated_q": global_q, "local_q": local, "pooled_q": pooled}
        (out / f"checkpoint-{seed}.json").write_text(json.dumps(checkpoint), encoding="utf-8")
        for i, station in enumerate(stations):
            for episode in range(config["eval_episodes"]):
                key = scenario_seed(seed, "evaluation", i, episode)
                scenario = generate(station, key)
                methods = {"fcfs": 2, "edf": 1, "shortest_remaining": 3, "solar_only": 4,
                           "federated_q": global_q, "local_q": local[i], "pooled_q": pooled}
                for method, policy in methods.items():
                    env = ChargingEnv(station, scenario)
                    for _ in range(SLOTS):
                        env.step(policy if isinstance(policy, int) else greedy(policy, env.state()))
                    rows.append(dict(seed=seed, station=station.name, episode=episode,
                                     scenario_seed=key, method=method, **env.metrics()))
                    if seed == config["seeds"][0] and i == 0 and episode == 0:
                        traces.extend(dict(method=method, **{k:v for k,v in t.items() if k != "allocations"}) for t in env.trace)
        print(f"Finished seed {seed}", flush=True)
    write_csv(out / "evaluation.csv", rows)
    write_csv(out / "training.csv", history)
    write_csv(out / "trace.csv", traces)
    metric_names = list(rows[0])[5:]
    summaries = []
    # Seed-level averages are the replicate unit; do not count correlated days as seeds.
    for method in sorted({r["method"] for r in rows}):
        result = {"method": method, "n_seeds": len(config["seeds"])}
        for metric in metric_names:
            values = [statistics.mean(r[metric] for r in rows if r["method"] == method and r["seed"] == seed)
                      for seed in config["seeds"]]
            result[metric + "_mean"] = statistics.mean(values)
            result[metric + "_sd"] = statistics.stdev(values) if len(values) > 1 else 0.0
        summaries.append(result)
    write_csv(out / "summary.csv", summaries)
    paired = []
    for base in sorted({r["method"] for r in rows} - {"federated_q"}):
        for seed in config["seeds"]:
            fed = [r for r in rows if r["method"] == "federated_q" and r["seed"] == seed]
            other = {(r["station"], r["episode"]): r for r in rows if r["method"] == base and r["seed"] == seed}
            paired.append(dict(seed=seed, baseline=base, **{m + "_delta": statistics.mean(
                r[m] - other[(r["station"], r["episode"])][m] for r in fed) for m in metric_names}))
    write_csv(out / "paired_deltas.csv", paired)
    source_hash = hashlib.sha256()
    for path in sorted(Path(__file__).parent.glob("*.py")):
        source_hash.update(path.name.encode())
        source_hash.update(path.read_bytes())
    provenance = dict(config=config, python=sys.version, platform=platform.platform(),
                      source_sha256=source_hash.hexdigest(),
                      transitions_per_learning_method_per_seed=config["rounds"] * config["local_episodes"] * len(stations) * SLOTS,
                      federated_float64_payload_bytes_per_seed=2 * config["rounds"] * len(stations) * N_STATES * len(ACTIONS) * 8,
                      communication_note="Analytical full-table upload plus broadcast payload; excludes transport and serialization overhead.")
    (out / "metadata.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    from .report import render
    render(out)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/quick.json")
    parser.add_argument("--out", default="results/run")
    args = parser.parse_args()
    try:
        config = json.loads(Path(args.config).read_text(encoding="utf-8"))
        run(config, args.out)
    except (ValueError, KeyError, OSError, TypeError) as exc:
        parser.exit(2, f"Error: {exc}\n")

if __name__ == "__main__":
    main()
