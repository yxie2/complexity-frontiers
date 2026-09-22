# Dimensions of permanental varieties in arbitrary size

**Ying Xie** · Kennesaw State University · yxie2@kennesaw.edu

[PDF](paper.pdf) · [LaTeX](main.tex) · [Verification code](anc/)
· [Recorded results](anc/verification_results.json) · [Submission package](submission_package.zip)
· [Source package](source_package.zip) · [Zenodo preprint](https://zenodo.org/records/22901136)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22901136.svg)](https://doi.org/10.5281/zenodo.22901136)

## Status and results

Zenodo preprint; nine pages. DOI: [10.5281/zenodo.22901136](https://doi.org/10.5281/zenodo.22901136).
This version has not been peer reviewed. The repository PDF is identical to
`dimensions_of_permanental_varieties.pdf` in [Zenodo record 22901136](https://zenodo.org/records/22901136).

For a generic matrix over a field of characteristic different from two, the
manuscript proves

$$\dim K[X]/I_h(a,b)=\max(a,b)(h-1)$$

when $1\leq h\leq\min(a,b)$ and $h<\max(a,b)$. It gives critical-locus
codimension $2n$ for the permanent of every order $n\geq2$, and separately
proves that maximal permanents of a generic $k\times(k+1)$ matrix generate
a geometrically reduced complete intersection. Further consequences concern
the Hilbert series and the permanent's product count.

The [prime-size paper](../prime-size-permanents/README.md) supplies a distinct
Frobenius-splitting argument. The [three-by-four paper](../three-by-four-permanents/README.md)
studies Frobenius purity. The dimension and reducedness results here do not
imply Frobenius purity or an unrestricted circuit lower bound.

## Cite this preprint

> Ying Xie. *Dimensions of permanental varieties in arbitrary size*.
> Zenodo, 2026. https://doi.org/10.5281/zenodo.22901136.

```bibtex
@misc{xie2026permanentdimensions,
  author = {Xie, Ying},
  title = {Dimensions of permanental varieties in arbitrary size},
  year = {2026},
  publisher = {Zenodo},
  doi = {10.5281/zenodo.22901136},
  url = {https://doi.org/10.5281/zenodo.22901136},
  note = {Preprint}
}
```

Machine-readable citation metadata is in [CITATION.cff](CITATION.cff).

## Reproduce the checks

From the repository root, with Python 3.11 or later:

```sh
python scripts/verify_permanents.py all-size-permanents
```

Only the Python standard library is required. The wrapper checks file hashes
and both portable archives, runs the verification in a temporary directory,
and compares the new results with the archived records.

The checks cover 817 exact polynomial equalities at sizes two through five
and 87,376 coordinate-support pairs at sizes two through eight. They test
the bordered expansions, cubic identities in both orientations, highest-degree
parts, and support model used in the paper. These finite checks supplement
the written proofs; they do not certify the arbitrary-size theorems, peer
review, or novelty.

The standalone command from this directory is:

```sh
python anc/verify.py --compare anc/verification_results.json
```

## Build the paper

Install a TeX distribution with `pdflatex`, Latin Modern, `geometry`, `amsmath`,
`amssymb`, `amsthm`, `mathtools`, `microtype`, and `hyperref`. From this directory:

```sh
python build.py
```

The bibliography is included in the source. The build creates `build/main.pdf`;
the published PDF is stored as `paper.pdf`.

The portable ZIP files contain source, code, recorded results, citation metadata,
licenses, and build instructions. The submission ZIP also includes the PDF.
They contain no internal review notes or build logs.
[ARTIFACTS.json](ARTIFACTS.json) records the file and archive-member hashes.

## Acknowledgment

The manuscript retains the author's acknowledgment to OpenAI GPT-6 for
assistance with research exploration, proof development, verification code,
and manuscript preparation.

## License

The manuscript is licensed under [CC BY 4.0](LICENSE.md), as listed in its
Zenodo record. Verification code, result records, and documentation are
licensed under the [MIT License](LICENSE_CODE).
