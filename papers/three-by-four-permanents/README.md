# F-purity of the maximal permanental ideal of a generic three-by-four matrix

**Ying Xie** · Kennesaw State University · yxie2@kennesaw.edu

[PDF](paper.pdf) · [LaTeX](main.tex) · [Verification code](anc/)
· [Recorded results](anc/verification_results.json) · [Review package](review_package.zip)

## Status and results

Research manuscript for expert review; eight pages. This version has not been
peer reviewed. No journal acceptance, DOI, or arXiv identifier is claimed.

For a generic three-by-four matrix over a field of odd characteristic $p$,
the manuscript proves that the quotient by its four maximal permanents is
$F$-pure exactly when $p\equiv1\pmod6$. It gives an explicit formula for the
associated coefficient by reducing it to a Domb-number sum. Appendix A
contains polynomial certificates for the finite transformation used in the
calculation. See the manuscript for the hypotheses and proofs.

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
