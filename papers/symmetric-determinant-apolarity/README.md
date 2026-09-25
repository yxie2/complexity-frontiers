# Symmetric-determinant apolarity in odd characteristic

**Ying Xie** · Kennesaw State University · yxie2@kennesaw.edu

[PDF](paper.pdf) · [LaTeX](main.tex) · [arXiv source package](arxiv_submission.zip)
· [Zenodo record](https://zenodo.org/records/22950380)

## Results

This twelve-page manuscript determines the apolar ideal of the generic
symmetric determinant under ordinary differentiation over a field of odd
characteristic. Beyond the classical quadratic relations, it gives explicit
minimal generators indexed by subsets of size $2p-2$, computes the Hilbert
series through bounded Dyck paths, and determines the Lefschetz thresholds:
the weak Lefschetz property holds exactly when $N\leq 2p-2$, and the strong
Lefschetz property holds exactly when $N<p$.

The proof identifies apolar relations with radicals of invariant pairings
for $\mathrm{SL}_2$ and obtains explicit generators from the Steinberg
symmetrizer. Lemma 3.1 includes the coefficientwise polynomial argument;
Proposition 4.2 gives the factorization maps, precise source citations,
and the contraction argument for arbitrary $N$.

## Build the paper

With pdfLaTeX and the standard packages listed in the source, run from
this directory:

~~~sh
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
~~~

The generated file is main.pdf; the distributed manuscript is
[paper.pdf](paper.pdf). The bibliography is embedded in main.tex, so BibTeX
and external figures are unnecessary.

The arXiv archive contains only main.tex. Its extracted source was compiled
separately and produced a byte-identical PDF. The manuscript has no displayed
date, and its PDF creation and modification timestamps are suppressed.
The [artifact manifest](ARTIFACTS.json) records the distributed file hashes.

## Cite this preprint

> Ying Xie. *Symmetric-determinant apolarity in odd characteristic*.
> Zenodo, 2026. https://zenodo.org/records/22950380.

Machine-readable citation metadata is in [CITATION.cff](CITATION.cff).
Consult the linked Zenodo record for publication and manuscript license
information.

## Acknowledgment

The author acknowledges OpenAI GPT-6 for assistance with research exploration,
proof development, verification code, and manuscript preparation.
