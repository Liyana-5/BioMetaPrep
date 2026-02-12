from pathlib import Path
from typer.testing import CliRunner
from biometaprep.cli import app

runner = CliRunner()

def test_cli_normalize_creates_outputs(tmp_path: Path):
    infile = tmp_path / "tiny.tsv"
    infile.write_text(
        "Sample_ID\tOrganism\nS1\thuman\nS2\tmouse\n",
        encoding="utf-8",
    )
    outdir = tmp_path / "out"

    result = runner.invoke(app, [str(infile), "--outdir", str(outdir)])
    assert result.exit_code == 0, result.output

    assert any(p.name.endswith("_metadata_clean.tsv") for p in outdir.glob("*"))
    assert any(p.name.endswith("_report.md") for p in outdir.glob("*"))
