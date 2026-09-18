# Strongly Exponential Sensitive Monotone Bounds in VP via Eulerian Conditioning

**Ying Xie** · Kennesaw State University · yxie2@kennesaw.edu

[Read the paper](paper.pdf) · [Zenodo record](https://zenodo.org/records/22783087)
· [LaTeX source](main.tex) · [Verification code](anc/)
· [Source archive](arxiv_source.zip)

## Publication status

- Preprint dated September 15, 2026; 28 pages.
- DOI: [10.5281/zenodo.22783087](https://doi.org/10.5281/zenodo.22783087).
- Submitted to arXiv on September 15, 2026; announcement pending as of
  September 18, 2026. No arXiv identifier is assigned here.
- This repository makes no claim of acceptance by a peer-reviewed venue.

## Main theorem

The manuscript states that there are constants $a,b>0$ and explicit families
$F_N,P_N$ on $N$ variables, for all sufficiently large $N$, such that $F_N$
has a linear-size monotone circuit, $P_N$ is in uniform VP, and

$$
\operatorname{monSIZE}(F_N\pm\epsilon P_N)\ge 2^{bN}
\qquad\text{for }2^{-aN}\le\epsilon\le\tfrac12.
$$

The circuit model permits arbitrary nonnegative real constants and unrestricted
fan-out. Here $P_N$ comes from an arborescence polynomial and $F_N$ from a
product of outgoing-choice sums. See the paper for the finite construction,
constants, padding, and the approximation and counting consequences.

## Connections within this paper

```mermaid
flowchart LR
    A[Local permutations on an expander] --> B[Eulerian conditioning]
    B --> C[Balanced-partition discrepancy]
    C --> D[Coefficient charge for shared gates]
    D --> E[Sensitive monotone lower bound]
    E --> F[Approximation and counting consequences]
```

The targets have small general arithmetic circuits. The theorem concerns the
monotone model and sensitivity to coefficient perturbations; it does not give
a general arithmetic or Boolean circuit separation.

## Verification

From the repository root, with Python 3.11:

```sh
python -m pip install -r papers/sensitive-monotone-vp/anc/requirements.txt
python scripts/verify_sensitive_monotone.py
```

The wrapper checks [ARTIFACTS.json](ARTIFACTS.json) and the ancillary manifest,
then runs the archived checker suite in a temporary copy. The seven checks
cover BEST counting and parity gadgets, spectral and conditioning identities,
pair-density inequalities, shared-gate decomposition, lowest homogeneous
components, counting normalization, and the shared-gate coefficient charge.
Only recorded timestamps and elapsed times are ignored in result comparisons.
See [anc/README.md](anc/README.md) for the exact coverage of each checker.

The finite tests support the constructions and calculations. The asymptotic
claims depend on the written proofs.

## Build the paper

From this directory, using PDFLaTeX:

```sh
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

The bibliography is included in `main.tex`; no BibTeX step is needed. The
committed `paper.pdf` is the archived preprint; `main.pdf` is the local rebuild.

## Version and citation

The PDF matches the file in the linked Zenodo record. The LaTeX and ancillary
files are preserved byte-for-byte from the accompanying source package.
[ARTIFACTS.json](ARTIFACTS.json) records their SHA-256 hashes and public provenance.

```bibtex
@misc{xie2026sensitive,
  author    = {Ying Xie},
  title     = {Strongly Exponential Sensitive Monotone Bounds in VP
               via Eulerian Conditioning},
  year      = {2026},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.22783087},
  url       = {https://doi.org/10.5281/zenodo.22783087}
}
```

The manuscript retains its acknowledgment of OpenAI GPT-6. The manuscript is
licensed under CC BY 4.0; accompanying code and result records are MIT-licensed.
