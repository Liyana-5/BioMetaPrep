from __future__ import annotations

from typing import Any, Dict, List, Tuple

import pandas as pd

from .schema import SampleMetadata

# --- Column name harmonization (source -> canonical) ---
COLUMN_SYNONYMS: Dict[str, str] = {
    # identity
    "GSE_ID": "study_id",
    "gse_id": "study_id",
    "study": "study_id",
    "sample_id": "sample_id",
    "gsm_id": "sample_id",
    "GSM": "sample_id",
    "organism": "organism",
    "organism_ch1": "organism",
    "Run": "run_id",
    "run": "run_id",
    "BioProject": "bioproject_id",
    "bioproject": "bioproject_id",
    "BioSample": "biosample_id",
    "biosample": "biosample_id",
    # biology
    "tissue": "tissue",
    "cell_type": "cell_type",
    "Cell": "cell_source",
    "source_name": "cell_source",
    "phenotype": "cell_source",
    "marker": "marker",
    "disease": "disease",
    "disease_phase": "disease_phase",
    # study design
    "Patient_id": "subject_id",
    "patient_id": "subject_id",
    "donor_id": "subject_id",
    "treatment": "treatment",
    "treatment_time": "treatment_time",
    "follow_up": "timepoint",
    "timepoint": "timepoint",
    "response": "response",
    "batch": "batch",
    # technical
    "Assay Type": "assay",
    "assay": "assay",
    "platform": "platform",
    "Platform": "platform",
    "instrument": "instrument",
    "LibraryLayout": "library_layout",
    "library_layout": "library_layout",
}

NA_TOKENS = {"", "na", "n/a", "nan", "none", "null", "unknown", "not available"}


def _clean_str(x: Any) -> str | None:
    """Normalize common NA tokens and whitespace."""
    if x is None:
        return None
    s = str(x).strip()
    if s == "":
        return None
    if s.lower() in NA_TOKENS:
        return None
    return s


def _canonicalize_organism(x: str | None) -> str:
    """Map common organism spellings to canonical names."""
    if not x:
        return "UNKNOWN"
    s = x.strip().lower()
    mapping = {
        "human": "Homo sapiens",
        "homo sapiens": "Homo sapiens",
        "h. sapiens": "Homo sapiens",
        "mouse": "Mus musculus",
        "mus musculus": "Mus musculus",
        "m. musculus": "Mus musculus",
    }
    return mapping.get(s, x.strip())


def _derive_condition(row: Dict[str, Any]) -> str | None:
    """
    Create a deterministic grouping label (deduplicated).
    """
    keys = ("disease", "treatment", "disease_phase", "response", "timepoint")

    parts: List[str] = []
    seen: set[str] = set()

    for key in keys:
        v = _clean_str(row.get(key))
        if not v:
            continue
        v = v.replace(" ", "_")
        if v in seen:
            continue
        seen.add(v)
        parts.append(v)

    return "|".join(parts) if parts else None



def normalize_metadata(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """
    Convert a raw metadata table into canonical columns and validate per-row using Pydantic.
    Returns (clean_df, warnings).
    """
    # 1) rename columns (only those present)
    renamer = {c: COLUMN_SYNONYMS[c] for c in df.columns if c in COLUMN_SYNONYMS}
    df = df.rename(columns=renamer)

    records: List[Dict[str, Any]] = []
    warnings: List[str] = []

    # 2) row-wise cleaning + validation
    for idx, row in df.iterrows():
        row_dict = {k: _clean_str(v) for k, v in row.to_dict().items()}
        
        if (row_dict.get("tissue") or "").lower() == "cell line":
            row_dict["cell_source"] = row_dict.get("cell_source") or "cell line"
            row_dict["tissue"] = None

        if (row_dict.get("disease_phase") or "").lower() == "cell line":
            row_dict["cell_source"] = row_dict.get("cell_source") or "cell line"
            row_dict["disease_phase"] = None
        
        # organism canonicalization (even if missing)
        row_dict["organism"] = _canonicalize_organism(row_dict.get("organism"))

        # required fields (soft fail -> warn, but we still try)
        missing_required = [k for k in ("study_id", "sample_id") if not row_dict.get(k)]
        if missing_required:
            warnings.append(f"Row {idx}: missing required {missing_required}; row skipped")
            continue

        # derive condition (optional but useful)
        row_dict["condition"] = _derive_condition(row_dict)

        # validate into typed model
        try:
            sample = SampleMetadata(**row_dict)
            records.append(sample.model_dump())
        except Exception as e:
            warnings.append(f"Row {idx}: validation failed: {e}")

    clean_df = pd.DataFrame(records)

    # Put canonical columns first (nice UX)
    preferred_order = [
        "study_id",
        "sample_id",
        "run_id",
        "subject_id",
        "organism",
        "tissue",
        "cell_source",
        "cell_type",
        "marker",
        "disease",
        "disease_phase",
        "treatment",
        "treatment_time",
        "response",
        "timepoint",
        "batch",
        "assay",
        "platform",
        "instrument",
        "library_layout",
        "bioproject_id",
        "biosample_id",
        "condition",
    ]
    cols = [c for c in preferred_order if c in clean_df.columns] + [
        c for c in clean_df.columns if c not in preferred_order
    ]
    clean_df = clean_df.reindex(columns=cols)

    return clean_df, warnings
