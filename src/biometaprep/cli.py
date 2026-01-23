from pathlib import Path
import pandas as pd
from yaml import warnings
from biometaprep.normalize.clean import normalize_metadata
import typer

def detect_delimiter(filepath: str) -> str:
    """
    Detect whether a metadata file is comma- or tab-separated.
    Defaults to tab if unsure.
    """
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        header = f.readline()

    comma_count = header.count(",")
    tab_count = header.count("\t")

    if comma_count > tab_count:
        return ","
    return "\t"

import re

def infer_study_id(infile: Path, df: pd.DataFrame) -> str:
    # 1) from file content
    if "study_id" in df.columns:
        vals = df["study_id"].dropna().astype(str)
        if len(vals) > 0:
            return vals.iloc[0].strip()

    # 2) from filename (e.g., GSE76312)
    m = re.search(r"(GSE\d+)", infile.name, flags=re.IGNORECASE)
    if m:
        return m.group(1).upper()

    return "UNKNOWN"


app = typer.Typer(help="BioMetaPrep: normalize and validate public single-cell genomics metadata.")

@app.callback()
def main():
    """
    BioMetaPrep CLI entry point.
    """
    pass


@app.command()
def hello(name: str = "world") -> None:
    """Sanity check command."""
    typer.echo(f"BioMetaPrep says hello, {name}!")
    
@app.command()
def normalize(
    infile: Path = typer.Argument(..., help="Input metadata file (CSV/TSV)"),
    outdir: Path = typer.Option(Path("out"), help="Output directory"),
    study_id: str = typer.Option(
        "", help="Study ID for output filename (e.g., GSE76312). If blank, infer from file."
    ),
) -> None:
    """Normalize a raw metadata table into a canonical schema."""
    outdir.mkdir(parents=True, exist_ok=True)

    # robust delimiter detection
    df = pd.read_csv(infile, sep=None, engine="python", comment="#")

    # strip BOM from headers (Windows/export issue)
    df.columns = [str(c).lstrip("\ufeff") for c in df.columns]

    clean_df, warnings = normalize_metadata(df)

    sid = (study_id or "").strip() or infer_study_id(infile, df)

    clean_file = outdir / f"{sid}_metadata_clean.tsv"
    report_file = outdir / f"{sid}_report.md"

    clean_df.to_csv(clean_file, sep="\t", index=False)

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# BioMetaPrep normalization report\n\n")
        f.write(f"- Study ID: {sid}\n")
        f.write(f"- Rows processed: {len(df)}\n")
        f.write(f"- Rows kept: {len(clean_df)}\n")
        f.write(f"- Warnings: {len(warnings)}\n\n")
        if warnings:
            f.write("## Warnings (first 200)\n")
            for w in warnings[:200]:
                f.write(f"- {w}\n")
            if len(warnings) > 200:
                f.write(f"\n... ({len(warnings) - 200} more warnings)\n")


    typer.echo(f" Clean metadata written to: {clean_file}")
    typer.echo(f"Report written to: {report_file}")   


if __name__ == "__main__":
    app()
