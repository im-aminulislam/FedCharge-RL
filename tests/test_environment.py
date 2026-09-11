import unittest
from fedcharge.environment import Station, Scenario, Session, ChargingEnv, generate, SLOTS, DT, N_STATES

class EnvironmentTests(unittest.TestCase):
    def setUp(self):
        self.station = Station("test", 12, 9, 0.4)

    def test_generator_reproducibility(self):
        self.assertEqual(generate(self.station, "same"), generate(self.station, "same"))
        self.assertNotEqual(generate(self.station, "same"), generate(self.station, "different"))

    def test_conservation_and_constraints_all_policies(self):
        for action in range(5):
            for seed in range(4):
                scenario = generate(self.station, seed)
                env = ChargingEnv(self.station, scenario)
                for t in range(SLOTS):
                    self.assertIn(env.state(), range(N_STATES))
                    env.step(action)
                    row = env.trace[-1]
                    self.assertAlmostEqual(row["delivered_kwh"], row["grid_kwh"] + row["solar_kwh"])
                    self.assertLessEqual(row["grid_kwh"], self.station.grid_kw * DT + 1e-10)
                    self.assertLessEqual(row["solar_kwh"], scenario.solar[t] * DT + 1e-10)
                    self.assertLessEqual(len(row["allocations"]), self.station.ports)
                    for i, energy in row["allocations"]:
                        self.assertLessEqual(energy, self.station.port_kw * DT + 1e-10)
                        self.assertLessEqual(scenario.sessions[i].arrival, t)
                        self.assertLess(t, scenario.sessions[i].departure)
                m = env.metrics()
                self.assertAlmostEqual(m["demand_kwh"], m["delivered_kwh"] + m["unmet_kwh"])
                self.assertAlmostEqual(sum(r["missed_kwh"] for r in env.trace), m["unmet_kwh"])
                self.assertAlmostEqual(m["reward"], m["delivered_kwh"] - m["cost_usd"] - 4*m["unmet_kwh"])
                if action == 4:
                    self.assertEqual(m["cost_usd"], 0)

    def test_exact_single_slot_physics_and_terminal_penalty(self):
        st = Station("single", 1, 0, 0, grid_kw=1, ports=1, port_kw=1)
        scenario = Scenario((Session(95,96,0.5),), (0.0,)*95+(0.5,), (0.2,)*96)
        env = ChargingEnv(st, scenario)
        for _ in range(95):
            env.step(0)
        _,reward,done=env.step(1)
        self.assertTrue(done)
        self.assertAlmostEqual(reward, 0.25 - 0.025 - 4*0.25)
        self.assertAlmostEqual(env.metrics()["cost_usd"], 0.025)
        self.assertAlmostEqual(env.trace[-1]["solar_kwh"], 0.125)
        with self.assertRaises(RuntimeError):
            env.step(1)

    def test_departed_sessions_cannot_charge(self):
        scenario=Scenario((Session(0,1,0.5),), (0.0,)*96, (0.1,)*96)
        env=ChargingEnv(self.station,scenario)
        env.step(0)
        for _ in range(95):
            env.step(1)
        self.assertEqual(env.metrics()["delivered_kwh"],0)
        self.assertAlmostEqual(env.metrics()["reward"],-2)

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            Station("bad",1,9,-1)
        with self.assertRaises(ValueError):
            ChargingEnv(self.station,Scenario((Session(4,4,1),),(0.0,)*96,(0.1,)*96))
        env=ChargingEnv(self.station,generate(self.station,0))
        for value in (-1, 5, 1.2, True):
            with self.assertRaises(ValueError):
                env.step(value)
        with self.assertRaises(RuntimeError):
            env.metrics()

if __name__ == "__main__":
    unittest.main()
