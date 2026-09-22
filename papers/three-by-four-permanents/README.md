# F-purity of the maximal permanental ideal of a generic three-by-four matrix

**Ying Xie** · Kennesaw State University · yxie2@kennesaw.edu

[PDF](paper.pdf) · [LaTeX](main.tex) · [Verification code](anc/)
· [Recorded results](anc/verification_results.json) · [Review package](review_package.zip)
· [Zenodo preprint](https://zenodo.org/records/22879129)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22879129.svg)](https://doi.org/10.5281/zenodo.22879129)

## Status and results

Zenodo preprint; eight pages. DOI: [10.5281/zenodo.22879129](https://doi.org/10.5281/zenodo.22879129).
This version has not been peer reviewed. The repository PDF is identical to
`three_by_four.pdf` in [Zenodo record 22879129](https://zenodo.org/records/22879129).

For a generic three-by-four matrix over a field of odd characteristic $p$,
the manuscript proves that the quotient by its four maximal permanents is
$F$-pure exactly when $p\equiv1\pmod6$. It gives an explicit formula for the
associated coefficient by reducing it to a Domb-number sum. Appendix A
contains polynomial certificates for the finite transformation used in the
calculation. See the manuscript for the hypotheses and proofs.

The companion [arbitrary-size paper](../all-size-permanents/README.md),
[Zenodo 22901136](https://zenodo.org/records/22901136), treats dimensions and
reducedness in characteristic different from two. The Frobenius-purity questions
studied here provide arithmetic information beyond those geometric conclusions.

## Cite this preprint

> Ying Xie. *F-purity of the maximal permanental ideal of a generic
> three-by-four matrix*. Zenodo, 2026. https://doi.org/10.5281/zenodo.22879129.

```bibtex
@misc{xie2026threebyfourpermanents,
  author = {Xie, Ying},
  title = {{F}-purity of the maximal permanental ideal of a generic three-by-four matrix},
  year = {2026},
  publisher = {Zenodo},
  doi = {10.5281/zenodo.22879129},
  url = {https://doi.org/10.5281/zenodo.22879129},
  note = {Preprint}
}
```

Machine-readable citation metadata is in [CITATION.cff](CITATION.cff).

## Reproduce the checks

From the repository root, with Python 3.11 or later:

```sh
python scripts/verify_permanents.py three-by-four-permanents
```

Only the Python standard library is required. The wrapper checks the artifact
hashes and archive contents, runs the verification in a temporary directory,
and compares the output with the archived results without modifying them.

The checks cover the quartic determinant identity, constant terms, both cleared
telescoping certificates, summand identities through degree 60, residue values
for odd primes below 200, and independent projective-column counts through
characteristic 19. Finite checks supplement the written arguments; they do not
establish the all-prime statements or replace mathematical refereeing.

## Build the paper

From this directory:

```sh
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

The bibliography is included in the source. The build creates `main.pdf`;
the reviewed PDF is stored as `paper.pdf`.

The review ZIP contains a standalone copy of the paper, source, instructions,
verification programs, and recorded results. [ARTIFACTS.json](ARTIFACTS.json)
records SHA-256 hashes. Citation metadata is in [CITATION.cff](CITATION.cff).
The manuscript retains its acknowledgment.

## License

The manuscript is licensed under [CC BY 4.0](LICENSE.md), as listed in its
Zenodo record. Verification code, result records, and repository documentation
are licensed under the repository's [MIT License](../../LICENSE).
