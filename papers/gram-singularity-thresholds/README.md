# Sharp FRS and singularity thresholds for off-diagonal Gram maps

**Ying Xie**, Kennesaw State University · [yxie2@kennesaw.edu](mailto:yxie2@kennesaw.edu)

Research draft; not peer reviewed. Mathematical scrutiny, corrections, and
reproducibility reports are welcome through the repository's
[issue tracker](https://github.com/yxie2/complexity-frontiers/issues).

[PDF](paper.pdf) · [LaTeX source](main.tex) · [Code and recorded results](anc/)
· [Zenodo record](https://zenodo.org/records/23005526)
· [DOI](https://doi.org/10.5281/zenodo.23005526)

## Results and open problem

The paper determines the exact characteristic-zero FRS threshold for the
off-diagonal Gram map on $h$ vectors in dimension $M$:

$$M>F(h),\qquad F(h)=\max_{2\le r\le h}\left(2h-r+1-\frac{2h}{r}\right).$$

Here FRS means flat with reduced geometric fibers having rational
singularities. The same inequality characterizes rational singularities of
the zero fiber. The paper also computes the log canonical threshold of its
defining ideal for every $M$ and $h$, proves integral complete-intersection
fibers for all truncated coefficient maps over $\mathbb{Z}[1/2]$ in the
strict range, and gives quantitative local-field density estimates.
The sufficient bound is sharp uniformly over graphs on $h$ vertices;
individual sparse graphs can admit smaller bounds.

This gives the sharp characteristic-zero replacement for the rationality
bound asked about in Casabella and Sammartano's
[Question 8.1](https://arxiv.org/html/2512.25058v1#S8.SS1).
The sharp positive-characteristic F-rationality threshold remains open.
The earlier [orthogonal-frame paper](../orthogonal-frame-varieties/README.md)
provides counterexamples at the prime threshold and separate results on
principal components; this paper supplies the positive threshold theorem.

## Reproduce the finite checks

Use Python 3.11 or later from the repository root; no third-party packages
are needed:

```sh
python scripts/verify_gram_singularities.py
```

The verifier checks artifact hashes and archive contents, runs all four
programs in a temporary directory, and compares their outputs with the
archived results, excluding only elapsed time. It leaves the recorded
results unchanged. For the file checks alone, add `--integrity-only`.

The programs cover threshold arithmetic, finite-ring Fourier identities,
direct Gram-fiber counts, first-jet counts, and hollow valuation strata.
The [ancillary guide](anc/README.md) gives their exact scope and individual
commands. Finite calculations supplement the manuscript proofs; they do
not establish the assertions over all fields or independent peer review.

## Download and build

- [Review bundle: paper, source, and code](review_bundle.zip)
- [Code-only ZIP](gram_verification_code.zip)
- [arXiv source package](arxiv_submission.zip)
- [Artifact hashes](ARTIFACTS.json)

With pdfLaTeX installed, run these commands from this paper directory:

```sh
pdflatex -interaction=nonstopmode -halt-on-error -no-shell-escape main.tex
pdflatex -interaction=nonstopmode -halt-on-error -no-shell-escape main.tex
pdflatex -interaction=nonstopmode -halt-on-error -no-shell-escape main.tex
```

The bibliography is embedded in `main.tex`. The arXiv source ZIP includes
the same source and ancillary files. The distributed `paper.pdf` also
embeds the ancillary files and code ZIP as document attachments; a plain
LaTeX build produces the typeset manuscript without those attachments.
The source package was verified by a clean rebuild before publication.

## Cite this preprint

> Ying Xie. *Sharp FRS and singularity thresholds for off-diagonal Gram maps*.
> Zenodo, 2026. https://doi.org/10.5281/zenodo.23005526.

[Machine-readable citation](CITATION.cff) · [Manuscript license](LICENSE.md)

## Acknowledgment

The author thanks OpenAI's GPT-6 for assistance with exploratory calculations,
proof development, code checks, and manuscript drafting. The author takes
responsibility for the mathematical claims and the final manuscript.
