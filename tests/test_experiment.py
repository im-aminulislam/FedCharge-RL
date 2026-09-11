import csv
import json
from pathlib import Path
import tempfile
import unittest
from fedcharge.experiment import run, validate

class ExperimentTests(unittest.TestCase):
    def config(self):
        return dict(rounds=1,local_episodes=1,eval_episodes=2,seeds=[3,7],alpha=0.1,gamma=0.9,
                    epsilon_start=0.7,epsilon_end=0.1,epsilon_decay=0.9,
                    stations=[dict(name="a",sessions=4,arrival_hour=9,solar_kw=0.4),
                              dict(name="b",sessions=5,arrival_hour=17,solar_kw=0.1)])

    def test_end_to_end_pairing_reports_and_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows=run(self.config(),Path(tmp)/"out")
            self.assertEqual(len(rows),2*2*2*7)
            for seed in (3,7):
                for station in ("a","b"):
                    for episode in (0,1):
                        matched=[r for r in rows if (r["seed"],r["station"],r["episode"])==(seed,station,episode)]
                        self.assertEqual(len({r["scenario_seed"] for r in matched}),1)
                        self.assertEqual(len({r["demand_kwh"] for r in matched}),1)
            out=Path(tmp)/"out"
            for name in ("report.html","RESULTS.md","evaluation.csv","training.csv","summary.csv","paired_deltas.csv","trace.csv","metadata.json","checkpoint-3.json"):
                self.assertGreater((out/name).stat().st_size,0)
            metadata=json.loads((out/"metadata.json").read_text())
            self.assertEqual(metadata["transitions_per_learning_method_per_seed"],192)
            with (out/"summary.csv").open() as f:
                self.assertEqual(len(list(csv.DictReader(f))),7)
            with self.assertRaises(ValueError):
                run(self.config(),out)

    def test_invalid_config(self):
        config=self.config()
        config["seeds"]=[3,3]
        with self.assertRaises(ValueError):
            validate(config)

if __name__ == "__main__":
    unittest.main()
