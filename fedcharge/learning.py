"""Tabular Q-learning and sample-weighted full-table federated averaging."""
import random
from .environment import ACTIONS, N_STATES, SLOTS, ChargingEnv, generate


def new_table():
    return [[0.0] * len(ACTIONS) for _ in range(N_STATES)]


def greedy(q, state):
    # Prefer EDF on ties, including previously unseen states.
    return max((1, 2, 3, 4, 0), key=lambda a: q[state][a])


def update(q, state, action, reward, next_state, done, alpha, gamma):
    target = reward if done else reward + gamma * max(q[next_state])
    q[state][action] += alpha * (target - q[state][action])


def average(tables, weights):
    if not tables or len(tables) != len(weights) or any(w <= 0 for w in weights):
        raise ValueError("Provide a positive weight for every table")
    if any(len(q) != N_STATES or any(len(row) != len(ACTIONS) for row in q) for q in tables):
        raise ValueError("Incompatible Q-table dimensions")
    total = sum(weights)
    return [[sum(w * q[s][a] for q, w in zip(tables, weights)) / total
             for a in range(len(ACTIONS))] for s in range(N_STATES)]


def scenario_seed(seed, split, station_index, episode):
    # String namespaces avoid train/evaluation collisions for any episode budget.
    return f"fedcharge-v1/{seed}/{split}/{station_index}/{episode}"


def train_episode(q, station, seed, epsilon, alpha, gamma):
    env = ChargingEnv(station, generate(station, seed))
    rng = random.Random(seed + "/exploration")
    state = env.state()
    for _ in range(SLOTS):
        action = rng.randrange(len(ACTIONS)) if rng.random() < epsilon else greedy(q, state)
        next_state, reward, done = env.step(action)
        update(q, state, action, reward, next_state, done, alpha, gamma)
        state = next_state
    return env.total_reward


def train(stations, config, seed):
    global_q = new_table()
    local = [new_table() for _ in stations]
    pooled = new_table()
    history = []
    for rnd in range(config["rounds"]):
        epsilon = max(config["epsilon_end"], config["epsilon_start"] * config["epsilon_decay"] ** rnd)
        clients = [[row[:] for row in global_q] for _ in stations]
        for i, station in enumerate(stations):
            for e in range(config["local_episodes"]):
                episode = rnd * config["local_episodes"] + e
                key = scenario_seed(seed, "train", i, episode)
                for method, q in (("federated_q", clients[i]), ("local_q", local[i]), ("pooled_q", pooled)):
                    reward = train_episode(q, station, key, epsilon, config["alpha"], config["gamma"])
                    history.append(dict(seed=seed, round=rnd + 1, station=station.name, method=method,
                                        episode=episode, epsilon=epsilon, reward=reward))
        global_q = average(clients, [config["local_episodes"] * SLOTS] * len(stations))
    return global_q, local, pooled, history
