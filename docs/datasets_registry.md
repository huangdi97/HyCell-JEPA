# Dataset Registry

This registry tracks candidate real datasets for HyCell-JEPA engineering smoke workflows. Registry entries are not evidence of biological discovery, rejuvenation, treatment effect, or model validity.

## GSE130973

Status: first real skin aging single-cell smoke dataset.

Title: Single-cell transcriptomes of the aging human skin reveal loss of fibroblast priming.

Why selected:
- Public GEO dataset with processed Matrix Market files.
- Relevant to human skin aging and fibroblast-state questions.
- Small enough to support a local ingestion smoke path when capped with `max_cells` and `max_genes`.

Expected raw files:
- `data/raw/gse130973/GSE130973_barcodes_filtered.tsv.gz`
- `data/raw/gse130973/GSE130973_genes_filtered.tsv.gz`
- `data/raw/gse130973/GSE130973_matrix_filtered.mtx.gz`

Download source:
- GEO accession GSE130973 processed supplementary files.
- Files must be downloaded manually and placed under `data/raw/gse130973/`.
- The repository must not download these files automatically.

Limitations:
- The three filtered files provide expression matrix, gene names, and barcodes only.
- Donor age, sample metadata, and fibroblast-only annotations are not available from these three files alone.
- The smoke artifact sets age and state labels to `unknown`.
- Duplicate gene symbols may appear in the processed features file and are disambiguated deterministically in the smoke NPZ.
- The prepared NPZ is for ingestion, inspection, validation, and conversion checks only.

Do-not-claim notes:
- Do not claim fibroblast-only filtering unless reliable metadata is added and verified.
- Do not invent donor age labels.
- Do not claim this proves rejuvenation, regeneration, or aging mechanisms.
- Do not treat smoke validation as biological validation.

## Future Candidate Datasets

- scPerturb small h5ad subset for perturbation-loader exercises.
- GSE226189 bulk fibroblast aging for non-single-cell comparison work.
- GSE274955 skin aging/photoaging for future skin aging ingestion.
- CELLxGENE human skin aging collection for standardized metadata exploration.
- PerturBase for perturbation metadata and action-label mapping experiments.
