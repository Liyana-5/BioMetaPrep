from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class SampleMetadata(BaseModel):
    # ---- identity / linkage ----
    study_id: str = Field(..., description="Study accession (e.g., GSE...)")
    sample_id: str = Field(..., description="Sample accession (e.g., GSM...)")
    organism: str = Field(..., description="Canonical organism name")
    run_id: Optional[str] = Field(None, description="SRA Run accession (e.g., SRR...)")
    bioproject_id: Optional[str] = Field(None, description="BioProject (e.g., PRJNA...)")
    biosample_id: Optional[str] = Field(None, description="BioSample (e.g., SAMN...)")

    # ---- biology (single-cell relevant) ----
    tissue: Optional[str] = None
    cell_source: Optional[str] = Field(
        None, description="e.g., PBMC, bone marrow, cell line, sorted cells"
    )
    cell_type: Optional[str] = None
    marker: Optional[str] = None

    disease: Optional[str] = None
    disease_phase: Optional[str] = None

    # ---- study design / grouping ----
    subject_id: Optional[str] = Field(None, description="Patient / donor identifier")
    treatment: Optional[str] = None
    treatment_time: Optional[str] = None
    response: Optional[str] = None
    timepoint: Optional[str] = Field(None, description="Follow-up / timepoint label")
    batch: Optional[str] = None

    # ---- technical ----
    assay: Optional[str] = None
    platform: Optional[str] = None
    instrument: Optional[str] = None
    library_layout: Optional[str] = None  # SINGLE / PAIRED etc.

    # optional derived grouping label (nice for downstream)
    condition: Optional[str] = Field(
        None, description="Derived grouping label (optional) e.g. CML|treated|blast"
    )
