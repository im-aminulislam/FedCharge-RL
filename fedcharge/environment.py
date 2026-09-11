"""Discrete-time, solar-assisted e-bike charging simulation. Units: kW, kWh, h, USD."""
from dataclasses import dataclass
import math
import random

SLOTS = 96
DT = 0.25
ACTIONS = ("pause", "edf", "fcfs", "shortest_remaining", "solar_only")
N_STATES = 6 * 3 * 3 * 2 * 2

@dataclass(frozen=True)
class Station:
    name: str
    sessions: int
    arrival_hour: float
    solar_kw: float
    grid_kw: float = 1.5
    ports: int = 6
    port_kw: float = 0.35

    def __post_init__(self):
        values = (self.arrival_hour, self.solar_kw, self.grid_kw, self.port_kw)
        if not all(math.isfinite(v) for v in values):
            raise ValueError("Station parameters must be finite")
        if not self.name or type(self.sessions) is not int or self.sessions < 1:
            raise ValueError("Station needs a name and positive integer session count")
        if type(self.ports) is not int or self.ports < 1 or self.port_kw <= 0:
            raise ValueError("Port count and port power must be positive")
        if self.solar_kw < 0 or self.grid_kw < 0 or not 0 <= self.arrival_hour < 24:
            raise ValueError("Invalid power or arrival hour")

@dataclass(frozen=True)
class Session:
    arrival: int
    departure: int
    energy_kwh: float

@dataclass(frozen=True)
class Scenario:
    sessions: tuple[Session, ...]
    solar: tuple[float, ...]
    price: tuple[float, ...]


def generate(station, seed):
    """All exogenous randomness is drawn before policy execution."""
    rng = random.Random(seed)
    sessions = []
    for _ in range(station.sessions):
        arrival = max(0, min(88, round(rng.gauss(station.arrival_hour * 4, 9))))
        departure = min(SLOTS, arrival + rng.randint(8, 28))
        sessions.append(Session(arrival, departure, rng.uniform(0.3, 1.1)))
    cloud = rng.uniform(0.5, 1.0)
    solar = tuple(station.solar_kw * max(0, math.sin(math.pi * (t * DT - 6) / 12))
                  * cloud if 6 <= t * DT <= 18 else 0.0 for t in range(SLOTS))
    price = tuple(0.38 if 16 <= t * DT < 21 else 0.18 if 7 <= t * DT < 16 else 0.10
                  for t in range(SLOTS))
    return Scenario(tuple(sessions), solar, price)


class ChargingEnv:
    """Preemptive allocation; ports can be reassigned only at slot boundaries."""
    def __init__(self, station, scenario):
        if len(scenario.solar) != SLOTS or len(scenario.price) != SLOTS:
            raise ValueError("Scenario must contain 96 solar and price values")
        if any(not math.isfinite(v) or v < 0 for v in scenario.solar + scenario.price):
            raise ValueError("Solar and price must be finite and nonnegative")
        for s in scenario.sessions:
            if not (type(s.arrival) is int and type(s.departure) is int
                    and 0 <= s.arrival < s.departure <= SLOTS
                    and math.isfinite(s.energy_kwh) and s.energy_kwh > 0):
                raise ValueError("Invalid session")
        self.station, self.scenario = station, scenario
        self.t = 0
        self.remaining = [s.energy_kwh for s in scenario.sessions]
        self.trace = []
        self.total_reward = 0.0

    def active(self):
        return [i for i, s in enumerate(self.scenario.sessions)
                if s.arrival <= self.t < s.departure and self.remaining[i] > 1e-9]

    def state(self):
        if self.t >= SLOTS:
            return 0  # ignored on terminal updates
        active = self.active()
        time_bin = self.t // 16
        price_bin = 0 if self.scenario.price[self.t] < 0.15 else 1 if self.scenario.price[self.t] < 0.3 else 2
        queue_bin = 0 if not active else 1 if len(active) <= self.station.ports else 2
        urgent = int(any(self.scenario.sessions[i].departure - self.t <= 4 for i in active))
        sun = int(self.scenario.solar[self.t] >= self.station.port_kw)
        return ((((time_bin * 3 + price_bin) * 3 + queue_bin) * 2 + urgent) * 2 + sun)

    def step(self, action):
        if self.t >= SLOTS:
            raise RuntimeError("Episode is finished")
        if type(action) is not int or not 0 <= action < len(ACTIONS):
            raise ValueError("Action must be an integer from 0 through 4")
        t, st = self.t, self.station
        active = self.active()
        if action in (1, 4):
            active.sort(key=lambda i: (self.scenario.sessions[i].departure, i))
        elif action == 2:
            active.sort(key=lambda i: (self.scenario.sessions[i].arrival, i))
        elif action == 3:
            active.sort(key=lambda i: (self.remaining[i], i))
        solar_available = self.scenario.solar[t] * DT
        budget = 0 if action == 0 else solar_available + (0 if action == 4 else st.grid_kw * DT)
        delivered = 0.0
        allocations = []
        for i in active[:st.ports]:
            energy = min(self.remaining[i], st.port_kw * DT, max(0.0, budget - delivered))
            self.remaining[i] = max(0.0, self.remaining[i] - energy)
            delivered += energy
            if energy > 0:
                allocations.append((i, energy))
        solar_used = min(delivered, solar_available)
        grid = max(0.0, delivered - solar_used)
        missed = sum(self.remaining[i] for i, s in enumerate(self.scenario.sessions) if s.departure == t + 1)
        cost = grid * self.scenario.price[t]
        reward = delivered - cost - 4.0 * missed
        self.total_reward += reward
        self.trace.append(dict(slot=t, delivered_kwh=delivered, solar_kwh=solar_used,
                               grid_kwh=grid, cost_usd=cost, missed_kwh=missed,
                               reward=reward, action=ACTIONS[action], allocations=allocations))
        self.t += 1
        return self.state(), reward, self.t == SLOTS

    def metrics(self):
        if self.t != SLOTS:
            raise RuntimeError("Metrics require a completed episode")
        demand = sum(s.energy_kwh for s in self.scenario.sessions)
        delivered = sum(x["delivered_kwh"] for x in self.trace)
        solar = sum(x["solar_kwh"] for x in self.trace)
        return dict(reward=self.total_reward,
                    cost_usd=sum(x["cost_usd"] for x in self.trace),
                    delivered_kwh=delivered, unmet_kwh=sum(self.remaining),
                    demand_kwh=demand, fulfillment=delivered / demand if demand else 1.0,
                    completion_rate=sum(r <= 1e-9 for r in self.remaining) / len(self.remaining) if self.remaining else 1.0,
                    solar_fraction=solar / delivered if delivered else 0.0,
                    peak_grid_kw=max(x["grid_kwh"] / DT for x in self.trace))
