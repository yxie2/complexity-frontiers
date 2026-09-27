# Complexity Frontiers

### Circuits, Proofs, and Algebra

Research papers and reproducible code on circuit lower bounds, proof complexity,
and algebraic geometry, motivated by P versus NP and VP versus VNP.

**Draft status.** The papers in this repository are research drafts and have not
undergone peer review. Scrutiny from mathematicians and other researchers is
warmly welcomed. Please report suspected errors, gaps in proofs, unclear
arguments, or reproducibility issues through
[GitHub Issues](https://github.com/yxie2/complexity-frontiers/issues), identifying
the paper and the relevant theorem, section, or page.

**Ying Xie** · Kennesaw State University · [yxie2@kennesaw.edu](mailto:yxie2@kennesaw.edu)

[![Permanent paper checks](https://github.com/yxie2/complexity-frontiers/actions/workflows/permanent-checks.yml/badge.svg)](https://github.com/yxie2/complexity-frontiers/actions/workflows/permanent-checks.yml)
[![Sensitive monotone checks](https://github.com/yxie2/complexity-frontiers/actions/workflows/finite-checks.yml/badge.svg)](https://github.com/yxie2/complexity-frontiers/actions/workflows/finite-checks.yml)
[![Elementary symmetric checks](https://github.com/yxie2/complexity-frontiers/actions/workflows/elementary-symmetric-checks.yml/badge.svg)](https://github.com/yxie2/complexity-frontiers/actions/workflows/elementary-symmetric-checks.yml)

## Papers

The order reflects an editorial assessment of the breadth of the results,
depth of the methods, and potential usefulness for further research.

| Paper | Materials | Status |
| --- | --- | --- |
| **Dimensions of permanental varieties in arbitrary size** | [Paper and reproduction guide](papers/all-size-permanents/README.md) · [PDF](papers/all-size-permanents/paper.pdf) · [LaTeX](papers/all-size-permanents/main.tex) · [Code](papers/all-size-permanents/anc/) | [Zenodo preprint](https://zenodo.org/records/22901136). |
| **Symmetric-determinant apolarity in odd characteristic** | [Paper and reproduction guide](papers/symmetric-determinant-apolarity/README.md) · [PDF](papers/symmetric-determinant-apolarity/paper.pdf) · [LaTeX](papers/symmetric-determinant-apolarity/main.tex) · [Code](papers/symmetric-determinant-apolarity/anc/) | [Zenodo record](https://zenodo.org/records/22950380). |
| **Principal components and singularities of orthogonal frame varieties** | [Paper and reproduction guide](papers/orthogonal-frame-varieties/README.md) · [PDF](papers/orthogonal-frame-varieties/paper.pdf) · [LaTeX](papers/orthogonal-frame-varieties/main.tex) · [Code](papers/orthogonal-frame-varieties/anc/) | [Zenodo record](https://zenodo.org/records/22985617). |
| **Strongly Exponential Sensitive Monotone Bounds in VP via Eulerian Conditioning** | [Paper and reproduction guide](papers/sensitive-monotone-vp/README.md) · [PDF](papers/sensitive-monotone-vp/paper.pdf) · [LaTeX](papers/sensitive-monotone-vp/main.tex) · [Code](papers/sensitive-monotone-vp/anc/) | [Zenodo preprint](https://zenodo.org/records/22783087). |
| **Derivative and multiplicity loci of elementary symmetric polynomials in positive characteristic** | [Paper and reproduction guide](papers/elementary-symmetric-loci/README.md) · [PDF](papers/elementary-symmetric-loci/paper.pdf) · [LaTeX](papers/elementary-symmetric-loci/main.tex) · [Code](papers/elementary-symmetric-loci/anc/) | [Zenodo preprint](https://zenodo.org/records/22929810). |
| **F-purity of the maximal permanental ideal of a generic three-by-four matrix** | [Paper and reproduction guide](papers/three-by-four-permanents/README.md) · [PDF](papers/three-by-four-permanents/paper.pdf) · [LaTeX](papers/three-by-four-permanents/main.tex) · [Code](papers/three-by-four-permanents/anc/) | [Zenodo preprint](https://zenodo.org/records/22879129). |
| **Frobenius splitting and singular loci of prime-size permanents** | [Paper and reproduction guide](papers/prime-size-permanents/README.md) · [PDF](papers/prime-size-permanents/paper.pdf) · [LaTeX](papers/prime-size-permanents/main.tex) · [Code](papers/prime-size-permanents/anc/) | [Zenodo preprint](https://zenodo.org/records/22878451). |

**Permanental dimensions in arbitrary size.** This paper determines the
dimensions of proper permanental varieties in characteristic different from
two. It gives exact critical-locus codimension for the permanent in every
size and proves that maximal permanents of a generic near-square matrix
generate a geometrically reduced complete intersection.

**Symmetric-determinant apolarity.** This paper determines the ordinary apolar
ideal of the generic symmetric determinant in every size over a field of
odd characteristic. It gives explicit additional generators, the Hilbert
series, and the exact weak and strong Lefschetz thresholds.

**Orthogonal frame varieties.** This paper gives defining equations,
normality and depth results for a triangular family of principal components,
and counterexamples to rationality at the prime threshold. It also classifies
the generic transverse cones in the stated parameter range.

**Sensitive monotone bounds in VP.** This paper establishes strongly
exponential sensitive lower bounds for monotone arithmetic circuits, for
explicit targets that have small general arithmetic circuits. Its
consequences concern monotone approximation and counting.

**Elementary-symmetric derivative and multiplicity loci.** This paper
determines derivative and multiplicity loci in positive characteristic,
including their dimensions, components attaining the larger dimension,
generic multiplicities, and translation stabilizers.

**Three-by-four permanents.** This paper characterizes exactly which odd
characteristics give an F-pure quotient by the maximal permanents of a generic
three-by-four matrix, using an explicit Frobenius coefficient calculation.

**Prime-size permanents.** This paper gives a Frobenius-splitting argument
for maximal near-square permanents at prime sizes, with consequences for
reducedness, singular codimension, and strength. The arbitrary-size paper
extends its principal dimension and reducedness conclusions by a separate
geometric method.

Each manuscript states its hypotheses, proofs, and limitations. These
results do not establish an unrestricted circuit separation, VP versus VNP,
or P versus NP.

## Reproduce the finite checks

Use Python 3.11 and run the commands below from the repository root.
The suites listed below have archived results. The verifiers check file hashes,
run the code in temporary copies, and compare the new results with those
records without overwriting them.

### Permanental dimensions in arbitrary size

```sh
python scripts/verify_permanents.py all-size-permanents
```

No additional Python packages are required. The checks cover 817 exact polynomial
equalities for sizes two through five and 87,376 coordinate-support pairs for
sizes two through eight. See the [reproduction guide](papers/all-size-permanents/README.md#reproduce-the-checks)
and [recorded results](papers/all-size-permanents/anc/verification_results.json).

### Symmetric-determinant apolarity

```sh
python scripts/verify_paper_code.py symmetric-determinant-apolarity
```

Only the Python standard library is required. The checker covers exact
derivative ranks, Hilbert functions, generator spans, and Lefschetz maps.
See the [code guide](papers/symmetric-determinant-apolarity/anc/README.md)
for scope and provenance.

### Orthogonal frame varieties

```sh
python -m pip install -r papers/orthogonal-frame-varieties/anc/requirements.txt
python scripts/verify_paper_code.py orthogonal-frame-varieties
```

The five programs check Veronese and Gale equations, Hilbert-series
calculations, transverse chart identities, and threshold parameters.
See the [code guide](papers/orthogonal-frame-varieties/anc/README.md)
for scope and provenance.

### Sensitive monotone bounds in VP

```sh
python -m pip install -r papers/sensitive-monotone-vp/anc/requirements.txt
python scripts/verify_sensitive_monotone.py
```

The seven checks cover counting, conditioning, spectral estimates, and the
shared-gate coefficient argument. See the [reproduction guide](papers/sensitive-monotone-vp/README.md#verification)
and [recorded results](papers/sensitive-monotone-vp/anc/RUN_CHECKS.json).

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

### Run all available check suites

```sh
python -m pip install -r papers/orthogonal-frame-varieties/anc/requirements.txt
python -m pip install -r papers/sensitive-monotone-vp/anc/requirements.txt
python -m pip install -r papers/elementary-symmetric-loci/anc/requirements.txt
python scripts/verify_permanents.py all-size-permanents
python scripts/verify_paper_code.py symmetric-determinant-apolarity
python scripts/verify_paper_code.py orthogonal-frame-varieties
python scripts/verify_sensitive_monotone.py
python scripts/verify_elementary_symmetric.py
python scripts/verify_permanents.py three-by-four-permanents
python scripts/verify_permanents.py prime-size-permanents
```

GitHub Actions runs the
[sensitive monotone checks](https://github.com/yxie2/complexity-frontiers/actions/workflows/finite-checks.yml),
the [permanent checks](https://github.com/yxie2/complexity-frontiers/actions/workflows/permanent-checks.yml),
and the [elementary symmetric checks](https://github.com/yxie2/complexity-frontiers/actions/workflows/elementary-symmetric-checks.yml)
in separate workflows.

These checks test finite identities and circuit constructions. They do not
prove the asymptotic theorems or establish independent peer review or novelty.

## Cite the work

Please cite the individual paper whose results or code you use. Each has a
separate citation below and its own machine-readable citation file.

### Permanental dimensions in arbitrary size

> Ying Xie. *Dimensions of permanental varieties in arbitrary size*.
> Zenodo, 2026. https://doi.org/10.5281/zenodo.22901136.

[Citation metadata](papers/all-size-permanents/CITATION.cff) · [Zenodo record](https://zenodo.org/records/22901136)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22901136.svg)](https://doi.org/10.5281/zenodo.22901136)

### Symmetric-determinant apolarity

> Ying Xie. *Symmetric-determinant apolarity in odd characteristic*.
> Zenodo, 2026. https://zenodo.org/records/22950380.

[Citation metadata](papers/symmetric-determinant-apolarity/CITATION.cff) · [Zenodo record](https://zenodo.org/records/22950380)

### Orthogonal frame varieties

> Ying Xie. *Principal components and singularities of orthogonal frame varieties*.
> Zenodo, 2026. https://zenodo.org/records/22985617.

[Citation metadata](papers/orthogonal-frame-varieties/CITATION.cff) · [Zenodo record](https://zenodo.org/records/22985617)

### Sensitive monotone bounds in VP

> Ying Xie. *Strongly Exponential Sensitive Monotone Bounds in VP via Eulerian
> Conditioning*. Zenodo, 2026. https://doi.org/10.5281/zenodo.22783087.

[Citation metadata](papers/sensitive-monotone-vp/CITATION.cff) · [Zenodo record](https://zenodo.org/records/22783087)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22783087.svg)](https://doi.org/10.5281/zenodo.22783087)

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
seven papers as references. Each Zenodo link identifies the individual
record listed with it.

## Feedback

Mathematical corrections, questions about a proof step, and reproducibility
issues are welcome through [GitHub Issues](https://github.com/yxie2/complexity-frontiers/issues).
Please identify the paper, theorem or page, and the precise issue. For code
reports, include the command and relevant software versions.

## Acknowledgment

All seven manuscripts retain their acknowledgments to OpenAI GPT-6.
Each manuscript states the assistance acknowledged for that work.

## Licenses

Verification code, result records, and repository documentation are available
under the [MIT License](LICENSE).

Manuscript-specific license notices are listed separately:

| Paper | Manuscript license information |
| --- | --- |
| Permanental dimensions in arbitrary size | [CC BY 4.0 notice](papers/all-size-permanents/LICENSE.md), consistent with its Zenodo record. |
| Symmetric-determinant apolarity | Consult the [Zenodo record](https://zenodo.org/records/22950380) for manuscript license information. |
| Orthogonal frame varieties | Consult the [Zenodo record](https://zenodo.org/records/22985617) for manuscript license information. |
| Sensitive monotone bounds in VP | [CC BY 4.0 notice](papers/sensitive-monotone-vp/LICENSE.md), consistent with its Zenodo record. |
| Elementary-symmetric derivative and multiplicity loci | [CC BY 4.0 notice](papers/elementary-symmetric-loci/LICENSE.md), consistent with its Zenodo record. |
| Three-by-four permanents | [CC BY 4.0 notice](papers/three-by-four-permanents/LICENSE.md), consistent with its Zenodo record. |
| Prime-size permanents | [CC BY 4.0 notice](papers/prime-size-permanents/LICENSE.md), consistent with its Zenodo record. |

Archives contain both manuscripts and code; the corresponding license terms
apply to each file. Dependencies retain their respective licenses.
