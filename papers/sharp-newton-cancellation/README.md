# Sharp Newton-edge bounds and cancellation families with one nonzero quadratic norm

**Ying Xie** · Kennesaw State University · [yxie2@kennesaw.edu](mailto:yxie2@kennesaw.edu)

[PDF](paper.pdf) · [LaTeX](main.tex) · [Verification code and certificates](anc/)
· [Code ZIP](verification.zip) · [arXiv source package](arxiv_submission.zip)
· [Zenodo record](https://zenodo.org/records/23094728)

## Results

This fourteen-page manuscript studies $q(P,Q,R)=PQ+R^2$ over fields of
characteristic different from two with real-valued nonarchimedean valuations.
Let $n$ count occupied vector coefficients and suppose exactly one has
nonzero quadratic norm. Write $V$ for the number of strict lower Newton
edges and $U$ for the number having width one.

- At six supports, $V\le11$ and $U\le10$. Both bounds are attained
  simultaneously over every nontrivially valued field in the stated class.
- At every prime, integer six-support examples have scalar sparsity fourteen
  and exactly ten simple nonzero local roots of distinct valuations.
- At five supports, the sharp bound is $V\le8$, with every-prime examples
  attaining $V=U=8$.
- For every $n\ge8$ and every prime, an integer family has $V=2n+1$,
  $U=2n$, and scalar sparsity $3n-4$, with input bit lengths $O(n^2\log p)$.

The six-support upper bounds use a computer-assisted proof: the written
reduction covers arbitrary input exponents and valuations, and exact
integer certificates check the resulting finite systems. The five-support
bound and the all-size construction have written proofs in the manuscript.
These results concern the stated quadratic model and do not establish an
unrestricted circuit lower bound or a separation of VP and VNP.

## Reproduce the checks

From the repository root, with Python 3.11 or later:

```sh
python scripts/verify_newton_cancellation.py
```

Only the Python standard library is required. The wrapper checks file hashes
and archive contents, then runs all five verification programs in an isolated
temporary directory. It compares their mathematical results with the archived
results and leaves the repository files unchanged. To check hashes and archive
contents without rerunning the arithmetic, add `--integrity-only`.

The upper-bound checks cover 2,359 marked patterns, including 962 linear
certificate trees for $V\le11$; the unit-edge bound checks four support
shapes and ten primary cases. Further programs verify the equality examples,
formal field-uniform sharpness, rule controls, five-support examples, and
the larger family. See [the code guide](anc/README.txt) and
[recorded results](verification_results.json).

To use the code independently, extract [verification.zip](verification.zip)
into an empty directory and run `python -B -X utf8 verify.py` there.
Python optimization flags must be disabled because the exact checkers use
assertions. No solver or network connection is needed.

## Build the manuscript

With pdfLaTeX installed, run from this paper directory:

```sh
pdflatex -interaction=nonstopmode -halt-on-error -no-shell-escape main.tex
pdflatex -interaction=nonstopmode -halt-on-error -no-shell-escape main.tex
```

The bibliography is included in `main.tex`. The supplied arXiv ZIP contains
the same source and the ancillary verification archive. Its source was
compiled locally with Tectonic; the resulting PDF text matches `paper.pdf`.

## Cite this work

> Ying Xie. *Sharp Newton-edge bounds and cancellation families with one nonzero quadratic norm*.
> [Zenodo record 23094728](https://zenodo.org/records/23094728).

[Citation metadata](CITATION.cff) · [Artifact hashes](ARTIFACTS.json)
· [License information](LICENSE.md)

## Acknowledgment

The author thanks OpenAI’s GPT-6 for assistance with exploratory calculations,
proof development, code checks, and manuscript drafting. The author takes
responsibility for the mathematical claims and the final manuscript.
