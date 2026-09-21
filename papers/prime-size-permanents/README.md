# Frobenius splitting and singular loci of prime-size permanents

**Ying Xie** · Kennesaw State University · yxie2@kennesaw.edu

[PDF](paper.pdf) · [LaTeX](main.tex) · [Verification code](anc/)
· [Recorded results](anc/verification_results.json) · [Review package](review_package.zip)

## Status and results

Research manuscript for expert review; ten pages. This version has not been
peer reviewed. No journal acceptance, DOI, or arXiv identifier is claimed.

For a prime $p$, the manuscript proves that the maximal permanents of a generic
$(p-1)\times p$ matrix form a geometrically reduced complete intersection of
height $p$ in characteristic $p$ and characteristic zero. It gives ambient
critical codimension $2p$ for the square permanent in these characteristics.
In characteristic zero, propagation gives $2q\le s(n)\le2n$, where $q$ is
the largest prime at most $n$, and hence an asymptotically sharp bound.
The paper also treats partial row expansions and strength. These geometric
invariants alone do not establish an unrestricted circuit lower bound.

## Reproduce the checks

From the repository root, with Python 3.11 or later:

```sh
python scripts/verify_permanents.py prime-size-permanents
```

Only the Python standard library is required. The wrapper checks the artifact
hashes and archive contents, runs the verification in a temporary directory,
and compares the output with the archived results without modifying them.

The checks cover small-prime trace coefficients and cyclic orbits, 128
generator-change cases, the row-expansion equations on every two-by-two matrix
over the field with two elements and every three-by-three matrix over the field
with three elements, cyclic fixed-point residues for primes below 200, and all
90 selected bordered cofactors at sizes three through seven. Finite-field point
counts do not determine geometric dimensions. The general conclusions depend
on the proofs in the manuscript and remain subject to mathematical refereeing.

## Build the paper

From this directory:

```sh
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

The bibliography is included in the source. The build creates `main.pdf`;
the reviewed PDF is stored as `paper.pdf`.

The review ZIP contains a standalone copy of the paper, source, instructions,
verification program, and recorded results. [ARTIFACTS.json](ARTIFACTS.json)
records SHA-256 hashes. Citation metadata is in [CITATION.cff](CITATION.cff).
The manuscript retains its acknowledgment.
