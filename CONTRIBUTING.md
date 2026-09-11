# Contributing

Describe the issue, proposed change, and expected scientific or engineering benefit in an issue before a large change. Small fixes can be submitted directly.

1. Fork and clone the repository; create a descriptive branch.
2. Use Python 3.10 or newer; no runtime dependencies are required.
3. Add a regression test when fixing simulator accounting or learning behavior.
4. Run `python -m unittest discover -s tests -v`.
5. Run the quick configuration into a fresh output directory.
6. Describe changes to the environment, reward, observation, or seed protocol explicitly. Such changes invalidate direct comparison with earlier outputs.

Do not add generated personal information, credentials, or unsupported performance claims. New experiment claims need the full configuration, raw seed-level outputs, and a reproducible command. Keep negative results. AI-assisted contributions are welcome when reviewed and disclosed.
