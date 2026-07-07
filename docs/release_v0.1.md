# HyCell-JEPA v0.1 Release Notes

## What Is Included

HyCell-JEPA v0.1 is an engineering MVP and portfolio release. It includes:

- Toy data generation.
- Gene-set scoring.
- EvidenceGraph construction.
- Compact encoders.
- JEPA transition core over toy compact readouts.
- HDF adapter.
- Biological verifier.
- Target-state planner.
- Streamlit demo.
- Toy benchmark scripts.
- Real-data loaders and schema validation.
- GSE130973 processed GEO Matrix Market ingestion.
- GSE130973 real-matrix summary and encoder smoke.
- Cloud RTX 4090 workflow scaffold.
- Result packaging.
- Goal 1-7 and release verification scripts.

## How To Reproduce

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the release verifier:

```bash
bash scripts/verify_release.sh
```

Optional real-data smoke requires manually downloaded GSE130973 processed GEO files in:

```text
data/raw/gse130973/
```

Then run:

```bash
python scripts/prepare_gse130973.py --raw-dir data/raw/gse130973 --out data/processed/gse130973/gse130973_smoke.npz --max-cells 5000 --max-genes 2000
python scripts/eval_real_smoke.py --input data/processed/gse130973/gse130973_smoke.npz
python scripts/train_real_smoke.py --config configs/train_gse130973_smoke.yaml
```

## Known Limitations

- Engineering MVP only.
- Not clinical advice.
- Not wet-lab validated.
- Not a complete virtual cell.
- Not Lingshu-Cell-scale transcriptome diffusion.
- Toy data is synthetic engineering validation.
- GSE130973 smoke data is unfiltered human skin single-cell data.
- GSE130973 age and state labels are unknown from the three matrix files alone.
- No HDF-only or fibroblast-only real-data subset exists yet.
- Planner outputs are toy demonstrations, not recommendations.

## Recommended Next Steps

- Add reliable GSE130973 metadata and cell-type annotation.
- Create a documented HDF/fibroblast subset only after metadata supports it.
- Add a small real perturbation dataset.
- Improve evidence grounding for verifier rules.
- Add runtime and memory reports for local and cloud workflows.

## What Not To Claim

Do not claim:

- Biological discovery.
- Rejuvenation.
- Treatment recommendation.
- HDF-specific GSE130973 conclusions.
- Wet-lab validation.
- Clinical utility.
- Full virtual-cell simulation.
- Lingshu-Cell-scale capability.
