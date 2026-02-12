import subprocess
import sys
from pathlib import Path

def test_cli_smoke(tmp_path: Path):
    # 1) Create tiny input TSV
    infile = tmp_path / "tiny.tsv"
    infile.write_text(
        "Sample_ID\tOrganism\n"
        "S1\thuman\n"
        "S2\tmouse\n",
        encoding="utf-8"
    )

    # 2) Output directory
    outdir = tmp_path / "out"
    outdir.mkdir()

    # 3) Run the CLI via python -m (more reliable on Windows than console scripts)
    cmd = [sys.executable, "-m", "biometaprep", str(infile), "--outdir", str(outdir)]

    res = subprocess.run(cmd, capture_output=True, text=True)

    assert res.returncode == 0, res.stderr

    # 4) Check expected outputs exist (flexible on prefix)
    files = [p.name for p in outdir.glob("*")]
    assert any(name.endswith("_metadata_clean.tsv") for name in files), files
    assert any(name.endswith("_report.md") for name in files), files
