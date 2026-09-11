PYTHON ?= python3
.PHONY: test demo benchmark extended

test:
	$(PYTHON) -m unittest discover -s tests -v

demo:
	$(PYTHON) -m fedcharge.experiment --config configs/quick.json --out results/quick

benchmark:
	$(PYTHON) -m fedcharge.experiment --config configs/benchmark.json --out results/benchmark

extended:
	$(PYTHON) -m fedcharge.experiment --config configs/extended.json --out results/extended
