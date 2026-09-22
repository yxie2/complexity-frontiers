"""Build the manuscript with two passes of pdflatex (shell escape disabled)."""

from pathlib import Path
import argparse
import shutil
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("build"))
    args = parser.parse_args()
    source = Path(__file__).resolve().parent
    destination = args.output_dir.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    executable = shutil.which("pdflatex")
    if executable is None:
        raise SystemExit("pdflatex was not found. Install a TeX distribution first.")
    command = [executable, "-interaction=nonstopmode", "-halt-on-error",
               "-no-shell-escape", f"-output-directory={destination}", "main.tex"]
    for number in (1, 2):
        completed = subprocess.run(command, cwd=source, capture_output=True,
                                   text=True, errors="replace")
        (destination / f"pass{number}.txt").write_text(
            completed.stdout + completed.stderr, encoding="utf-8")
        if completed.returncode:
            raise SystemExit(f"TeX pass {number} failed; see {destination / f'pass{number}.txt'}")
    log = (destination / "main.log").read_text(encoding="utf-8", errors="replace")
    problems = [line for line in log.splitlines()
                if "undefined" in line.lower() or "Overfull" in line
                or "Rerun to get" in line]
    if problems:
        raise SystemExit("Final TeX log requires attention:\n" + "\n".join(problems))
    print(destination / "main.pdf")


if __name__ == "__main__":
    main()
