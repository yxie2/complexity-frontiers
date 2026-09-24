# Complexity Frontiers

### Circuits, Proofs, and Algebra

Research papers and reproducible code on circuit lower bounds, proof complexity,
and algebraic geometry, motivated by P versus NP and VP versus VNP.

**Ying Xie** · Kennesaw State University · [yxie2@kennesaw.edu](mailto:yxie2@kennesaw.edu)

[![Sensitive monotone checks](https://github.com/yxie2/complexity-frontiers/actions/workflows/finite-checks.yml/badge.svg)](https://github.com/yxie2/complexity-frontiers/actions/workflows/finite-checks.yml)
[![Permanent paper checks](https://github.com/yxie2/complexity-frontiers/actions/workflows/permanent-checks.yml/badge.svg)](https://github.com/yxie2/complexity-frontiers/actions/workflows/permanent-checks.yml)
[![Elementary symmetric checks](https://github.com/yxie2/complexity-frontiers/actions/workflows/elementary-symmetric-checks.yml/badge.svg)](https://github.com/yxie2/complexity-frontiers/actions/workflows/elementary-symmetric-checks.yml)

## Papers

| Paper | Materials | Status |
| --- | --- | --- |
| **Strongly Exponential Sensitive Monotone Bounds in VP via Eulerian Conditioning** | [Paper and reproduction guide](papers/sensitive-monotone-vp/README.md) · [PDF](papers/sensitive-monotone-vp/paper.pdf) · [LaTeX](papers/sensitive-monotone-vp/main.tex) · [Code](papers/sensitive-monotone-vp/anc/) | [Zenodo preprint](https://zenodo.org/records/22783087). |
| **Dimensions of permanental varieties in arbitrary size** | [Paper and reproduction guide](papers/all-size-permanents/README.md) · [PDF](papers/all-size-permanents/paper.pdf) · [LaTeX](papers/all-size-permanents/main.tex) · [Code](papers/all-size-permanents/anc/) | [Zenodo preprint](https://zenodo.org/records/22901136). |
| **Derivative and multiplicity loci of elementary symmetric polynomials in positive characteristic** | [Paper and reproduction guide](papers/elementary-symmetric-loci/README.md) · [PDF](papers/elementary-symmetric-loci/paper.pdf) · [LaTeX](papers/elementary-symmetric-loci/main.tex) · [Code](papers/elementary-symmetric-loci/anc/) | [Zenodo preprint](https://zenodo.org/records/22929810). |
| **F-purity of the maximal permanental ideal of a generic three-by-four matrix** | [Paper and reproduction guide](papers/three-by-four-permanents/README.md) · [PDF](papers/three-by-four-permanents/paper.pdf) · [LaTeX](papers/three-by-four-permanents/main.tex) · [Code](papers/three-by-four-permanents/anc/) | [Zenodo preprint](https://zenodo.org/records/22879129). |
| **Frobenius splitting and singular loci of prime-size permanents** | [Paper and reproduction guide](papers/prime-size-permanents/README.md) · [PDF](papers/prime-size-permanents/paper.pdf) · [LaTeX](papers/prime-size-permanents/main.tex) · [Code](papers/prime-size-permanents/anc/) | [Zenodo preprint](https://zenodo.org/records/22878451). |

The first paper studies sensitive lower bounds for **monotone arithmetic
circuits**, for targets that have small general arithmetic circuits. The result
does not separate VP from VNP or P from NP. Its precise hypotheses, proofs,
and limitations are in the manuscript.

The permanent papers study dimensions of proper permanental varieties,
reduced complete intersections, Frobenius splitting, and singular codimensions.
Their algebraic conclusions do not by themselves give an unrestricted circuit
separation. Each paper has its own statements,
sources, reproduction instructions, and review status.

The elementary-symmetric paper determines derivative and multiplicity loci,
including their characteristic-dependent dimensions, generic multiplicities,
and translation stabilizers.

## Reproduce the finite checks

Use Python 3.11 and run the commands below from the repository root.
Each paper has its own archived results. The verifiers check file hashes,
run the code in temporary copies, and compare the new results with those
records without overwriting them.

### Sensitive monotone bounds in VP

```sh
python -m pip install -r papers/sensitive-monotone-vp/anc/requirements.txt
python scripts/verify_sensitive_monotone.py
```

The seven checks cover counting, conditioning, spectral estimates, and the
shared-gate coefficient argument. See the [reproduction guide](papers/sensitive-monotone-vp/README.md#verification)
and [recorded results](papers/sensitive-monotone-vp/anc/RUN_CHECKS.json).

### Permanental dimensions in arbitrary size

```sh
python scripts/verify_permanents.py all-size-permanents
```

No additional Python packages are required. The checks cover 817 exact polynomial
equalities for sizes two through five and 87,376 coordinate-support pairs for
sizes two through eight. See the [reproduction guide](papers/all-size-permanents/README.md#reproduce-the-checks)
and [recorded results](papers/all-size-permanents/anc/verification_results.json).

### Elementary-symmetric derivative and multiplicity loci

```sh
python -m pip install -r papers/elementary-symmetric-loci/anc/requirements.txt
python scripts/verify_elementary_symmetric.py
```

The four programs check partition coefficients, 210 Groebner dimensions,
translation ideals and normal forms, local orders, and Jacobian ranks. See the
[reproduction guide](papers/elementary-symmetric-loci/README.md#reproduce-the-checks)
and [recorded results](papers/elementary-symmetric-loci/anc/).

### Three-by-four permanents

```sh
python scripts/verify_permanents.py three-by-four-permanents
```

No additional Python packages are required. The checks cover the determinant
identity, constant terms, telescoping certificates, prime residues, and
projective-column counts. See the [reproduction guide](papers/three-by-four-permanents/README.md#reproduce-the-checks)
and [recorded results](papers/three-by-four-permanents/anc/verification_results.json).

### Prime-size permanents

```sh
python scripts/verify_permanents.py prime-size-permanents
```

No additional Python packages are required. The checks cover trace coefficients,
cyclic orbits, generator changes, critical equations over finite fields, and
bordered-cofactor expansions. See the [reproduction guide](papers/prime-size-permanents/README.md#reproduce-the-checks)
and [recorded results](papers/prime-size-permanents/anc/verification_results.json).

### Run checks for all papers

```sh
python -m pip install -r papers/sensitive-monotone-vp/anc/requirements.txt
python -m pip install -r papers/elementary-symmetric-loci/anc/requirements.txt
python scripts/verify_sensitive_monotone.py
python scripts/verify_permanents.py
python scripts/verify_elementary_symmetric.py
```

The permanent command runs all three permanent suites. GitHub Actions runs the
[sensitive monotone checks](https://github.com/yxie2/complexity-frontiers/actions/workflows/finite-checks.yml),
the [permanent checks](https://github.com/yxie2/complexity-frontiers/actions/workflows/permanent-checks.yml),
and the [elementary symmetric checks](https://github.com/yxie2/complexity-frontiers/actions/workflows/elementary-symmetric-checks.yml)
in separate workflows.

These checks test finite identities and circuit constructions. They do not
prove the asymptotic theorems or establish independent peer review or novelty.

## Cite the work

Please cite the individual paper whose results or code you use. Each has a
separate citation below and its own machine-readable citation file.

### Sensitive monotone bounds in VP

> Ying Xie. *Strongly Exponential Sensitive Monotone Bounds in VP via Eulerian
> Conditioning*. Zenodo, 2026. https://doi.org/10.5281/zenodo.22783087.

[Citation metadata](papers/sensitive-monotone-vp/CITATION.cff) · [Zenodo record](https://zenodo.org/records/22783087)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22783087.svg)](https://doi.org/10.5281/zenodo.22783087)

### Permanental dimensions in arbitrary size

> Ying Xie. *Dimensions of permanental varieties in arbitrary size*.
> Zenodo, 2026. https://doi.org/10.5281/zenodo.22901136.

[Citation metadata](papers/all-size-permanents/CITATION.cff) · [Zenodo record](https://zenodo.org/records/22901136)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22901136.svg)](https://doi.org/10.5281/zenodo.22901136)

### Elementary-symmetric derivative and multiplicity loci

> Ying Xie. *Derivative and multiplicity loci of elementary symmetric polynomials in positive characteristic*.
> Zenodo, 2026. https://doi.org/10.5281/zenodo.22929810.

[Citation metadata](papers/elementary-symmetric-loci/CITATION.cff) · [Zenodo record](https://zenodo.org/records/22929810)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22929810.svg)](https://doi.org/10.5281/zenodo.22929810)

### Three-by-four permanents

> Ying Xie. *F-purity of the maximal permanental ideal of a generic
> three-by-four matrix*. Zenodo, 2026. https://doi.org/10.5281/zenodo.22879129.

[Citation metadata](papers/three-by-four-permanents/CITATION.cff) · [Zenodo record](https://zenodo.org/records/22879129)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22879129.svg)](https://doi.org/10.5281/zenodo.22879129)

### Prime-size permanents

> Ying Xie. *Frobenius splitting and singular loci of prime-size permanents*.
> Zenodo, 2026. https://doi.org/10.5281/zenodo.22878451.

[Citation metadata](papers/prime-size-permanents/CITATION.cff) · [Zenodo record](https://zenodo.org/records/22878451)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22878451.svg)](https://doi.org/10.5281/zenodo.22878451)

The root [CITATION.cff](CITATION.cff) describes the collection and lists all
five papers as references. Each Zenodo DOI identifies the individual
preprint listed with it.

## Feedback

Mathematical corrections, questions about a proof step, and reproducibility
issues are welcome through [GitHub Issues](https://github.com/yxie2/complexity-frontiers/issues).
Please identify the paper, theorem or page, and the precise issue. For code
reports, include the command and relevant software versions.

## Acknowledgment

All five manuscripts retain their acknowledgments to OpenAI GPT-6.
Each manuscript states the assistance acknowledged for that work.

## Licenses

Verification code, result records, and repository documentation are available
under the [MIT License](LICENSE).

Manuscript-specific license notices are listed separately:

| Paper | Manuscript license information |
| --- | --- |
| Sensitive monotone bounds in VP | [CC BY 4.0 notice](papers/sensitive-monotone-vp/LICENSE.md), consistent with its Zenodo record. |
| Permanental dimensions in arbitrary size | [CC BY 4.0 notice](papers/all-size-permanents/LICENSE.md), consistent with its Zenodo record. |
| Elementary-symmetric derivative and multiplicity loci | [CC BY 4.0 notice](papers/elementary-symmetric-loci/LICENSE.md), consistent with its Zenodo record. |
| Three-by-four permanents | [CC BY 4.0 notice](papers/three-by-four-permanents/LICENSE.md), consistent with its Zenodo record. |
| Prime-size permanents | [CC BY 4.0 notice](papers/prime-size-permanents/LICENSE.md), consistent with its Zenodo record. |

Archives contain both manuscripts and code; the corresponding license terms
apply to each file. Dependencies retain their respective licenses.
