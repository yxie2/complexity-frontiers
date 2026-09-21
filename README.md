# Complexity Frontiers

### Circuits, Proofs, and Algebra

Research papers and reproducible code on circuit lower bounds, proof complexity,
and algebraic geometry, motivated by P versus NP and VP versus VNP.

**Ying Xie** · Kennesaw State University · [yxie2@kennesaw.edu](mailto:yxie2@kennesaw.edu)

[![Finite checks](https://github.com/yxie2/complexity-frontiers/actions/workflows/finite-checks.yml/badge.svg)](https://github.com/yxie2/complexity-frontiers/actions/workflows/finite-checks.yml)
[![Permanent paper checks](https://github.com/yxie2/complexity-frontiers/actions/workflows/permanent-checks.yml/badge.svg)](https://github.com/yxie2/complexity-frontiers/actions/workflows/permanent-checks.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22783087.svg)](https://doi.org/10.5281/zenodo.22783087)

## Papers

| Paper | Materials | Status |
| --- | --- | --- |
| **Strongly Exponential Sensitive Monotone Bounds in VP via Eulerian Conditioning** | [Paper and reproduction guide](papers/sensitive-monotone-vp/README.md) · [PDF](papers/sensitive-monotone-vp/paper.pdf) · [LaTeX](papers/sensitive-monotone-vp/main.tex) · [Code](papers/sensitive-monotone-vp/anc/) | Zenodo preprint. Submitted to arXiv; announcement pending. |
| **F-purity of the maximal permanental ideal of a generic three-by-four matrix** | [Paper and reproduction guide](papers/three-by-four-permanents/README.md) · [PDF](papers/three-by-four-permanents/paper.pdf) · [LaTeX](papers/three-by-four-permanents/main.tex) · [Code](papers/three-by-four-permanents/anc/) | Research manuscript for expert review. |
| **Frobenius splitting and singular loci of prime-size permanents** | [Paper and reproduction guide](papers/prime-size-permanents/README.md) · [PDF](papers/prime-size-permanents/paper.pdf) · [LaTeX](papers/prime-size-permanents/main.tex) · [Code](papers/prime-size-permanents/anc/) | Research manuscript for expert review. |

The first paper studies sensitive lower bounds for **monotone arithmetic
circuits**, for targets that have small general arithmetic circuits. The result
does not separate VP from VNP or P from NP. Its precise hypotheses, proofs,
and limitations are in the manuscript.

The permanent papers study maximal-permanent ideals, Frobenius splitting,
and singular codimensions. Their algebraic conclusions do not by themselves
give an unrestricted circuit separation. Each paper has its own statements,
sources, reproduction instructions, and review status.

## Reproduce the finite checks

Use Python 3.11 and run from the repository root:

```sh
python -m pip install -r papers/sensitive-monotone-vp/anc/requirements.txt
python scripts/verify_sensitive_monotone.py
```

This verifier checks file hashes, runs the seven supplied checks in a temporary
copy, and compares their substantive results with the archived records. It does
not overwrite the supplied results. GitHub Actions runs the same command.

For both permanent papers, no additional Python packages are required:

```sh
python scripts/verify_permanents.py
```

The permanent verifier checks artifact and archive hashes, runs each paper's
code in a temporary copy, and requires exact agreement with the archived
results. A separate GitHub Actions workflow runs these checks.

These checks test finite identities and circuit constructions. They do not
prove the asymptotic theorems or establish independent peer review or novelty.

## Cite the work

Please cite the individual paper when using its results or code:

> Ying Xie. *Strongly Exponential Sensitive Monotone Bounds in VP via Eulerian
> Conditioning*. Zenodo, 2026. https://doi.org/10.5281/zenodo.22783087.

Machine-readable citation information is in [CITATION.cff](CITATION.cff).
The DOI identifies the paper's Zenodo record, not this whole collection.
The two permanent papers have their own citation metadata:
[three-by-four paper](papers/three-by-four-permanents/CITATION.cff) and
[prime-size paper](papers/prime-size-permanents/CITATION.cff).

## Feedback

Mathematical corrections, questions about a proof step, and reproducibility
issues are welcome through [GitHub Issues](https://github.com/yxie2/complexity-frontiers/issues).
Please identify the paper, theorem or page, and the precise issue. For code
reports, include the command and relevant software versions.

## Acknowledgment

The sensitive-monotone paper acknowledges OpenAI GPT-6 for assistance with
research exploration, proof development, verification code, and manuscript
preparation. Its acknowledgment is preserved in the released manuscript.
The two permanent manuscripts likewise retain their acknowledgments.

## Licenses

Verification code, result records, and repository documentation are available
under the [MIT License](LICENSE).

The sensitive-monotone manuscript, including its PDF and LaTeX source, is
available under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/),
consistent with its Zenodo record. See the [paper license notice](papers/sensitive-monotone-vp/LICENSE.md).
The source archive contains both manuscript and code; the corresponding
license applies to each file. Dependencies retain their respective licenses.
