# Derivative and multiplicity loci of elementary symmetric polynomials in positive characteristic

**Ying Xie** · Kennesaw State University · yxie2@kennesaw.edu

[PDF](paper.pdf) · [LaTeX](main.tex) · [Verification code and results](anc/)
· [arXiv source package](arxiv_submission.zip) · [Zenodo preprint](https://zenodo.org/records/22929810)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22929810.svg)](https://doi.org/10.5281/zenodo.22929810)

## Results

This ten-page preprint determines the dimensions of derivative and higher
multiplicity loci of elementary symmetric polynomials in positive characteristic.
It classifies the components attaining the larger dimension, proves their
generic smoothness, computes the generic multiplicities of coordinate
components, and identifies the translation stabilizer scheme.

For degree $d$ in $n$ variables over an algebraically closed field of characteristic
$p>0$, let $Q=p^{v_p(n-d+1)}$. If $C_q$ is the common zero scheme of the derivatives
of order exactly $q$, and $Z_s$ is defined by all derivatives of orders less than $s$,
then

$$\dim C_q=d-q-1+\mathbf{1}_{Q>d-q},\qquad 1\le q\le d-1,$$

$$\dim Z_s=d-s+\mathbf{1}_{Q>d},\qquad 2\le s\le d.$$

The first-order criterion answers the dimension question in Orzel's
Conjecture 2.11 with a correction at prime-power degrees. The manuscript gives
the precise comparison with the cited revision and distinguishes the critical
scheme from the singular scheme of the zero hypersurface.

The repository PDF is byte-identical to `elementary_symmetric_loci.pdf` in
[Zenodo record 22929810](https://zenodo.org/records/22929810). It includes the
clarified singleton-coordinate counts and the explicit case $P_r>d$ in Section 3.
The manuscript has no displayed date. This version has not been peer reviewed.

## Reproduce the checks

From the repository root, with Python 3.11 or later:

```sh
python -m pip install -r papers/elementary-symmetric-loci/anc/requirements.txt
python scripts/verify_elementary_symmetric.py
```

The verifier checks artifact hashes and the arXiv archive, runs all four
programs in a temporary directory, and compares the results with the archived
JSON records. Only elapsed runtime is excluded from the comparison. The source
hashes and all mathematical results must agree; archived files are not overwritten.

| Program | Checks |
| --- | --- |
| [First-order dimensions](anc/check_elementary_modular_dimensions.py) | 75,475 partition coefficient checks and 90 Groebner dimension calculations |
| [Higher-order loci](anc/probe_elementary_higher_orders.py) | 58,820 partition coefficient checks and 120 Groebner dimension calculations |
| [Translation stabilizers](anc/check_elementary_translation.py) | 84 ideal comparisons, 8 normal-form identities, and 55,875 binomial threshold checks |
| [Local structure](anc/check_elementary_local_structure.py) | 1,716 integer polynomial identities, 21,340 local orders, and 660 Jacobian ranks |

These are finite computational checks. The general results depend on the proofs
in the manuscript. The computations do not establish novelty or independent peer review.

To check file integrity alone, without installing SymPy:

```sh
python scripts/verify_elementary_symmetric.py --integrity-only
```

## Build the paper

With pdfLaTeX and the standard packages listed in `main.tex`, run from this directory:

```sh
python build.py
```

The build writes `build/main.pdf`. The distributed PDF is `paper.pdf`.
The bibliography is embedded in the LaTeX source, so BibTeX is unnecessary.
The arXiv ZIP contains only `main.tex` and can be compiled directly with pdfLaTeX.
[ARTIFACTS.json](ARTIFACTS.json) records the hashes of the distributed files.

## Cite this preprint

> Ying Xie. *Derivative and multiplicity loci of elementary symmetric polynomials
> in positive characteristic*. Zenodo, 2026. https://doi.org/10.5281/zenodo.22929810.

```bibtex
@misc{xie2026elementarysymmetricschemes,
  author = {Xie, Ying},
  title = {Derivative and multiplicity loci of elementary symmetric polynomials in positive characteristic},
  year = {2026},
  publisher = {Zenodo},
  doi = {10.5281/zenodo.22929810},
  url = {https://doi.org/10.5281/zenodo.22929810},
  note = {Preprint}
}
```

Machine-readable citation metadata is in [CITATION.cff](CITATION.cff).

## Acknowledgment

The author acknowledges OpenAI GPT-6 for assistance with research exploration,
proof development, verification code, and manuscript preparation.

## License

The manuscript and its LaTeX source are licensed under
[CC BY 4.0](LICENSE.md), as listed in the Zenodo record. Verification code,
result records, and documentation are licensed under the [MIT License](LICENSE_CODE).
