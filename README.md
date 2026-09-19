# Complexity Frontiers

### Circuits, Proofs, and Algebra

Research papers and reproducible code on circuit lower bounds, proof complexity,
and algebraic geometry, motivated by P versus NP and VP versus VNP.

**Ying Xie** · Kennesaw State University · [yxie2@kennesaw.edu](mailto:yxie2@kennesaw.edu)

[![Finite checks](https://github.com/yxie2/complexity-frontiers/actions/workflows/finite-checks.yml/badge.svg)](https://github.com/yxie2/complexity-frontiers/actions/workflows/finite-checks.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22783087.svg)](https://doi.org/10.5281/zenodo.22783087)

## Papers

| Paper | Materials | Status |
| --- | --- | --- |
| **Strongly Exponential Sensitive Monotone Bounds in VP via Eulerian Conditioning** | [Paper and reproduction guide](papers/sensitive-monotone-vp/README.md) · [PDF](papers/sensitive-monotone-vp/paper.pdf) · [LaTeX](papers/sensitive-monotone-vp/main.tex) · [Code](papers/sensitive-monotone-vp/anc/) | Zenodo preprint. Submitted to arXiv; announcement pending. |

The first paper studies sensitive lower bounds for **monotone arithmetic
circuits**, for targets that have small general arithmetic circuits. The result
does not separate VP from VNP or P from NP. Its precise hypotheses, proofs,
and limitations are in the manuscript.

Future papers will be added with their own statements, sources, reproduction
instructions, and publication status. This overview describes the papers
released in this repository.

## Reproduce the finite checks

Use Python 3.11 and run from the repository root:

```sh
python -m pip install -r papers/sensitive-monotone-vp/anc/requirements.txt
python scripts/verify_sensitive_monotone.py
```

The verifier checks file hashes, runs the seven supplied checks in a temporary
copy, and compares their substantive results with the archived records. It does
not overwrite the supplied results. GitHub Actions runs the same command.

These checks test finite identities and circuit constructions. They do not
prove the asymptotic theorems or establish independent peer review or novelty.

## Cite the work

Please cite the individual paper when using its results or code:

> Ying Xie. *Strongly Exponential Sensitive Monotone Bounds in VP via Eulerian
> Conditioning*. Zenodo, 2026. https://doi.org/10.5281/zenodo.22783087.

Machine-readable citation information is in [CITATION.cff](CITATION.cff).
The DOI identifies the paper's Zenodo record, not this whole collection.

## Feedback

Mathematical corrections, questions about a proof step, and reproducibility
issues are welcome through [GitHub Issues](https://github.com/yxie2/complexity-frontiers/issues).
Please identify the paper, theorem or page, and the precise issue. For code
reports, include the command and relevant software versions.

## Acknowledgment

The sensitive-monotone paper acknowledges OpenAI GPT-6 for assistance with
research exploration, proof development, verification code, and manuscript
preparation. Its acknowledgment is preserved in the released manuscript.

## Licenses

Verification code, result records, and repository documentation are available
under the [MIT License](LICENSE).

The sensitive-monotone manuscript, including its PDF and LaTeX source, is
available under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/),
consistent with its Zenodo record. See the [paper license notice](papers/sensitive-monotone-vp/LICENSE.md).
The source archive contains both manuscript and code; the corresponding
license applies to each file. Dependencies retain their respective licenses.
