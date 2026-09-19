"""Verify the release and reproduce its finite checks without changing it."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "papers" / "sensitive-monotone-vp"
VOLATILE_FIELDS = {"elapsed_seconds"}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def substantive(record):
    # Only top-level elapsed times may differ.
    return {key: value for key, value in record.items()
            if key not in VOLATILE_FIELDS}


def main():
    artifacts = json.loads((PAPER / "ARTIFACTS.json").read_text(encoding="utf-8"))
    for item in artifacts["files"]:
        path = PAPER / item["path"]
        require(digest(path) == item["sha256"], f"Artifact hash mismatch: {item['path']}")
        require(path.stat().st_size == item["bytes"], f"Artifact size mismatch: {item['path']}")
    manifest = json.loads((PAPER / "anc" / "MANIFEST.json").read_text(encoding="utf-8"))
    for item in manifest["files"]:
        require(digest(PAPER / "anc" / item["path"]) == item["sha256"],
                f"Ancillary hash mismatch: {item['path']}")
    with zipfile.ZipFile(PAPER / "arxiv_source.zip") as archive:
        require(archive.testzip() is None, "Invalid source archive")
        expected_names = {"main.tex", "anc/MANIFEST.json"}
        expected_names.update("anc/" + item["path"] for item in manifest["files"])
        require(set(archive.namelist()) == expected_names, "Unexpected archive contents")
        for name in archive.namelist():
            require(archive.read(name) == (PAPER / name).read_bytes(),
                    f"Archive differs from unpacked file: {name}")
    print("PASS artifact, ancillary, and source-archive integrity", flush=True)

    original = json.loads((PAPER / "anc" / "RUN_CHECKS.json").read_text(encoding="utf-8"))
    require(original["status"] == "PASS" and len(original["checks"]) == 7,
            "Expected seven archived passing checks")
    with tempfile.TemporaryDirectory(prefix="sensitive-monotone-") as directory:
        temporary = Path(directory)
        shutil.copy2(PAPER / "main.tex", temporary / "main.tex")
        shutil.copytree(PAPER / "anc", temporary / "anc",
                        ignore=shutil.ignore_patterns("__pycache__", "check_logs"))
        subprocess.run([sys.executable, "-X", "utf8", str(temporary / "anc" / "run_checks.py")],
                       cwd=temporary / "anc", check=True, timeout=950)
        for item in original["checks"]:
            name = item["result"]
            expected = json.loads((PAPER / "anc" / name).read_text(encoding="utf-8"))
            actual = json.loads((temporary / "anc" / name).read_text(encoding="utf-8"))
            require(substantive(expected) == substantive(actual),
                    f"Substantive result differs from archived record: {name}")
    print("PASS all seven results match the archived substantive records", flush=True)
    print("Finite checks support the implementation; they do not prove the asymptotic theorems.")


if __name__ == "__main__":
    main()
