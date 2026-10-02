# Smooth slices and superquadratic border determinantal complexity of the permanent

**Ying Xie** · Kennesaw State University · [yxie2@kennesaw.edu](mailto:yxie2@kennesaw.edu)

[PDF](paper.pdf) · [LaTeX](main.tex) · [Verification code and results](anc/)
· [Complete release package](release_package.zip) · [arXiv source package](arxiv_submission.zip)
· [Zenodo record](https://zenodo.org/records/23108131)

## Results

This twenty-page manuscript proves an $\Omega(n^2\log n)$ lower bound for
the border determinantal complexity of the permanent over the complex numbers.
It gives the explicit bounds

$$
\overline{\mathrm{dc}}(\mathrm{per}_n)\ge
\frac{n^2(\log_2 n-5)}{64e}\qquad(n\ge64)
$$

and

$$
\overline{\mathrm{dc}}(\mathrm{per}_n)\ge
\frac{3n^2(\log_2 n-8)}{256eH_2(1/8)}\qquad(n\ge512),
$$

where $H_2$ is binary entropy. The same lower bounds hold for exact
determinantal complexity and the number of vertices in an arbitrary acyclic
algebraic branching program with affine-linear edge labels. The estimates
improve the classical quadratic bound asymptotically; they need not exceed
it throughout the displayed finite ranges.

The argument combines matching-polynomial restrictions with determinantal
kernel incidence through a fixed smooth linear slice. The manuscript credits
OpenAI for the matching restrictions, Sheshadri for the incidence mechanism,
and Guo for the shared-coefficient compression. Its additional steps include
the smooth-target transfer to coefficient limits and removal of the constant
coefficient block on the critical locus.

Further results determine the order of border determinantal complexity of
elementary symmetric polynomials and extend the permanent bounds to
algebraically closed fields of characteristic $p>n$. Separate circuit
appendices retain explicit budgets on non-skew products and nonscalar
divisions. These results do not separate VP from VNP.

## Reproduce the checks

From the repository root, with Python 3.11 or later:

```sh
python -m pip install -r papers/border-determinantal-permanent/anc/requirements.txt
python scripts/verify_border_determinantal.py
```

The wrapper verifies artifact hashes and archive contents, then runs all
eight finite verification suites in temporary copies. It compares their
outputs with the archived results, ignoring only measured runtime, and
leaves the supplied files unchanged. Add `--integrity-only` to check the
artifacts without rerunning the mathematical computations.

The suites check selector and permanent identities, polar coefficients,
multiplicity and characteristic controls, circuit-state identities,
coefficient compression, and explicit parameter inequalities. The two
parameter suites perform 2,010,774 checks in total, with overlapping
exhaustive intervals. These are supporting computations; the uniform
inequalities and asymptotic theorems are proved in the manuscript.

See [the code guide](anc/README.txt) and [recorded results](anc/results/).
The [complete release archive](release_package.zip) also contains the paper,
source, submission metadata, and portable verification code. After extracting
it, run `python -X utf8 run_verification.py` from its `verification/`
directory, with the dependencies installed. Run without Python's `-O` or
`-OO` options because the checkers use assertions.

## Build the manuscript

With pdfLaTeX installed, run from this paper directory:

```sh
pdflatex -interaction=nonstopmode -halt-on-error -no-shell-escape main.tex
pdflatex -interaction=nonstopmode -halt-on-error -no-shell-escape main.tex
```

The bibliography is embedded in `main.tex`, which loads four companion
`.tex` files. The arXiv ZIP contains precisely these five source files, with
`main.tex` at its root. The supplied PDF was built with Tectonic and matches
the PDF deposited in the linked Zenodo record. The source archive does not
include the PDF or verification code; those are available separately here.

## Cite this work

> Ying Xie. *Smooth slices and superquadratic border determinantal complexity of the permanent*.
> [Zenodo record 23108131](https://zenodo.org/records/23108131).
> DOI: [10.5281/zenodo.23108131](https://doi.org/10.5281/zenodo.23108131).

[Citation metadata](CITATION.cff) · [Artifact hashes](ARTIFACTS.json)
· [License information](LICENSE.md)

## Acknowledgment

The author thanks OpenAI’s GPT-6 for assistance with exploratory calculations,
proof development, code checks, and manuscript drafting. The author takes
responsibility for the mathematical claims and the final manuscript.
