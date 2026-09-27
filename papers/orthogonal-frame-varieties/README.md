# Principal components and singularities of orthogonal frame varieties

**Ying Xie** · Kennesaw State University · yxie2@kennesaw.edu

[PDF](paper.pdf) · [LaTeX](main.tex) · [Verification code and results](anc/)
· [Zenodo record](https://zenodo.org/records/22985617)

## Results

This nineteen-page manuscript studies defining ideals and singularities of
varieties of pairwise orthogonal vectors. Its principal results concern two
families adjacent to the complete-intersection and prime thresholds.

- For the triangular family, it determines the principal-component ideal
  over the complex numbers. The first case, six vectors in dimension six,
  has fifteen Gram quadrics and 330 explicit additional equations of degree twelve.
- In every characteristic different from two, the principal components in
  that family are normal, satisfy Serre's condition $S_k$ but not $S_{k+1}$,
  and have depth one below their dimension. The manuscript determines their
  non-Cohen--Macaulay locus, deficiency modules, and regularity.
- At the prime threshold, it constructs normal, frequently factorial frame
  varieties without rational singularities in characteristic zero and without
  $F$-rationality in odd characteristic. Their column counts have natural
  density one half. An exact local chart identifies the generic transverse
  singularities with cones over smooth complete intersections of quadrics.

These results answer the rationality question and the first defining-ideal
case posed by Casabella and Sammartano in
[The variety of orthogonal frames, arXiv:2512.25058v1](https://arxiv.org/abs/2512.25058v1),
and give normal but non-Cohen--Macaulay principal components. The defining-ideal
and principal-component conclusions concern the specified triangular family;
the positive transverse classification concerns the generic point of the
maximal-isotropic stratum. The manuscript states the full hypotheses and scope.

## Reproduce the finite checks

From the repository root, using Python 3.11 or later:

```sh
python -m pip install -r papers/orthogonal-frame-varieties/anc/requirements.txt
python scripts/verify_paper_code.py orthogonal-frame-varieties
```

The [code guide](anc/README.md) describes the exact scope, dependencies,
and source provenance. The verifier runs in a temporary copy and compares
the computed results with the archived records. Finite checks supplement
the manuscript proofs and do not establish the all-size theorems.

## Build the paper

With pdfLaTeX and the standard packages listed in the source, run from
this directory:

~~~sh
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
~~~

The generated file is main.pdf; the distributed manuscript is
[paper.pdf](paper.pdf). The bibliography is embedded in main.tex, and no
external figures or bibliography files are needed.

The arXiv archive contains only main.tex. Its extracted source was compiled
separately and produced a byte-identical PDF in the preparation environment.
The manuscript has no displayed date, and its PDF creation and modification
timestamps are suppressed. The [artifact manifest](ARTIFACTS.json) records
the distributed file hashes.

## Cite this preprint

> Ying Xie. *Principal components and singularities of orthogonal frame varieties*.
> Zenodo, 2026. https://zenodo.org/records/22985617.

Machine-readable citation metadata is in [CITATION.cff](CITATION.cff).
Consult the linked Zenodo record for publication and manuscript license
information.

## Acknowledgment

The author acknowledges OpenAI GPT-6 for assistance with research exploration,
proof development, verification code, and manuscript preparation.
