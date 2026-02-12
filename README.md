# BioMetaPrep

BioMetaPrep is a lightweight Python CLI tool for normalising and validating heterogeneous public
genomics metadata (CSV/TSV) into a canonical, analysis-ready schema.

It is designed to support reproducible downstream workflows by improving metadata consistency,
interoperability, and transparency (via validation warnings and simple QC reporting).

## Key features
- Column harmonisation via synonym mapping (e.g. study/sample/run IDs, biology and technical fields)
- Standardised NA token handling and string cleaning
- Organism canonicalisation (e.g. Homo sapiens / Mus musculus)
- Schema validation using Pydantic (row-level validation + warnings)
- Deterministic derived fields (e.g. condition labels for grouping)
- CLI interface for reproducible execution

## Installation (development)
```bash
pip install -e .
```
## Usage 
```bash
biometaprep path/to/metadata.tsv --outdir path/to/outputdir
```

## Outputs
- *_metada_clean.tsv (canonicalised metadata)

- *_report.md (summary + validation warnings)

## Status
Actively developed. Intended to be integrated as a preprocessing component in larger bioinformatics pipelines (e.g. Snakemake/Nextflow)

---
Author : Liyana Saleem
