"""Run the seven finite checks accompanying the paper; no network access is used."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import importlib.metadata
import json
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
CHECKS = {
    "check_euler_conditioning.py": "EULER_CONDITIONING_CHECK.json",
    "check_euler_refinements.py": "EULER_REFINEMENTS_CHECK.json",
    "check_pair_margin.py": "PAIR_MARGIN_CHECK.json",
    "check_shared_decomposition.py": "SHARED_DECOMPOSITION_CHECK.json",
    "check_lowest_component.py": "LOWEST_COMPONENT_CHECK.json",
    "check_counting_normalization.py": "COUNTING_NORMALIZATION_CHECK.json",
    "check_shared_charge.py": "SHARED_CHARGE_CHECK.json",
}


def run_one(item):
    script, result_name = item
    started = time.monotonic()
    result = subprocess.run(
        [sys.executable, "-X", "utf8", str(ROOT / script)],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=900,
    )
    log = ROOT / "check_logs" / (Path(script).stem + ".txt")
    log.write_text(result.stdout + "\n" + result.stderr, encoding="utf-8")
    if result.returncode != 0:
        raise RuntimeError(f"{script} exited {result.returncode}; inspect {log.name}")
    record = json.loads((ROOT / result_name).read_text(encoding="utf-8"))
    if record.get("status") != "PASS":
        raise RuntimeError(f"{result_name} did not report PASS")
    row = {
        "script": script, "result": result_name, "status": "PASS",
        "script_sha256": hashlib.sha256((ROOT / script).read_bytes()).hexdigest(),
        "result_sha256": hashlib.sha256((ROOT / result_name).read_bytes()).hexdigest(),
        "elapsed_seconds": round(time.monotonic() - started, 3),
    }
    print(f"PASS {script}", flush=True)
    return row


def main():
    (ROOT / "check_logs").mkdir(exist_ok=True)
    with ThreadPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(run_one, CHECKS.items()))
    report = {
        "status": "PASS",
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "dependencies": {name: importlib.metadata.version(name)
                         for name in ("networkx", "numpy", "sympy")},
        "checks": rows,
        "scope": "Finite identities and implementations only; the asymptotic theorems require the written proofs.",
    }
    (ROOT / "RUN_CHECKS.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("All seven finite checks passed.", flush=True)


if __name__ == "__main__":
    main()
