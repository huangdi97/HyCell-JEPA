# Benchmark Report

## Status
Goal 3 toy end-to-end benchmark has been run on the deterministic toy gene-set score table.

## Latest Commands

```bash
python scripts/make_toy_data.py --config configs/toy_data.yaml
python scripts/score_gene_sets.py --input outputs/toy_data/toy_cells.csv --config configs/gene_sets.yaml
python scripts/train_jepa.py --config configs/jepa_toy.yaml
python scripts/evaluate_jepa.py --config configs/jepa_toy.yaml
python scripts/benchmark_toy.py --config configs/benchmark_toy.yaml
pytest
```

## Latest Toy Metrics
- Toy score transitions: 8
- Training transitions: 6
- Held-out eval transitions: 2
- Training MSE: `0.000000375`
- Held-out eval MSE: `0.058339536`
- All-transition evaluation MSE: `0.014585165`
- Goal 3 benchmark transition MSE: `0.014585165`
- Verifier status counts: `{"warn": 8}`
- Planner sequence for configured target: `regeneration -> control`
- Planner final distance: `0.183562100`

Per-feature all-transition MSE:
- `ecm_remodeling`: `0.005293832`
- `proliferation`: `0.012120207`
- `reprogramming_plasticity`: `0.025554769`
- `senescence`: `0.033552743`
- `stress_inflammation`: `0.010538928`
- `viability_qc_proxy`: `0.000450512`

## Remaining Planned Benchmarks
- Real-data schema validation smoke tests.
- Runtime and memory checks on local CPU/GPU.
- Demo browser interaction beyond launch/import smoke.

## Reporting Rules
- Record commands, config files, metrics, runtime, and hardware.
- Clearly distinguish toy engineering metrics from biological validation.
- Store generated benchmark outputs in `outputs/`.

## Interpretation
The current metrics only show that the compact toy transition pipeline, HDF adapter, verifier, planner, benchmark script, and demo launch path can run end to end. They do not validate biological mechanisms or intervention effects.
