from pathlib import Path
import re
import pandas as pd
import typer
from biometaprep.normalize.clean import normalize_metadata

app = typer.Typer(help="BioMetaPrep: normalize and validate public single-cell genomics metadata.")


def infer_study_id(infile: Path, df: pd.DataFrame) -> str:
    """Infer study ID from a dataframe column or from the filename (e.g., GSE12345)."""
    if "study_id" in df.columns:
        vals = df["study_id"].dropna().astype(str)
        if len(vals) > 0:
            return vals.iloc[0].strip()

    m = re.search(r"(GSE\d+)", infile.name, flags=re.IGNORECASE)
    if m:
        return m.group(1).upper()

    return "UNKNOWN"


@app.command()
def normalize(
    infile: Path = typer.Argument(..., help="Input metadata file (CSV/TSV)"),
    outdir: Path = typer.Option(Path("out"), help="Output directory"),
    study_id: str = typer.Option(
        "", help="Study ID for output filename (e.g., GSE1234). If blank, infer from file."
    ),
) -> None:
    """Normalize a raw metadata table into a canonical schema."""
    outdir.mkdir(parents=True, exist_ok=True)

    # robust delimiter detection (pandas sniffs separator)
    df = pd.read_csv(infile, sep=None, engine="python", comment="#")

    # strip BOM from headers (Windows/export issue)
    df.columns = [str(c).lstrip("\ufeff") for c in df.columns]

    clean_df, qc_warnings = normalize_metadata(df)

    # infer study id from (1) user arg (2) cleaned df (3) raw df (4) filename
    sid = (study_id or "").strip()
    if not sid:
        sid = infer_study_id(infile, clean_df)
    if sid == "UNKNOWN":
        sid = infer_study_id(infile, df)

    clean_file = outdir / f"{sid}_metadata_clean.tsv"
    report_file = outdir / f"{sid}_report.md"

    clean_df.to_csv(clean_file, sep="\t", index=False)

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# BioMetaPrep normalization report\n\n")
        f.write(f"- Study ID: {sid}\n")
        f.write(f"- Rows processed: {len(df)}\n")
        f.write(f"- Rows kept: {len(clean_df)}\n")
        f.write(f"- Warnings: {len(qc_warnings)}\n\n")

        if qc_warnings:
            f.write("## Warnings (first 200)\n")
            for w in qc_warnings[:200]:
                f.write(f"- {w}\n")
            if len(qc_warnings) > 200:
                f.write(f"\n... ({len(qc_warnings) - 200} more warnings)\n")

    typer.echo(f"Clean metadata written to: {clean_file}")
    typer.echo(f"Report written to: {report_file}")


if __name__ == "__main__":
    app()
