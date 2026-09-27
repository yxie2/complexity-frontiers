# Symmetric-determinant apolarity verification code

`verify_apolarity.py` performs exact polynomial differentiation and linear
algebra for the examples, generator spans, Hilbert functions, and Lefschetz
maps in *Symmetric-determinant apolarity in odd characteristic*.

From the repository root, using Python 3.11 or later:

```sh
python scripts/verify_paper_code.py symmetric-determinant-apolarity
```

Only the Python standard library is required. The verifier checks artifact
hashes, runs the checker in a temporary copy, and compares its output with
[verification_results.json](verification_results.json). Only elapsed time is
ignored; source hashes are checked. The archived result remains unchanged.
Use `--integrity-only` to check the package without running computations.

The checker covers:

- Integer Cayley differentiation identities at sizes four and eight.
- Direct derivative spaces and all powers of the diagonal Lefschetz map
  for sizes one through seven in characteristics 3, 5, 7, and 101.
- Exact Hilbert functions at size four over the rationals and in
  characteristic 3; at size eight over the rationals and in
  characteristics 3, 5, 7, and 101.
- Degree p - 1 generator spans at sizes four through eight for p = 3,
  and at size eight for p = 5.
- Boolean inclusion-matrix boundary checks for p = 3, 5, and 7.
  Their assembly uses the manuscript's representation-theoretic decomposition.

[PROVENANCE.json](PROVENANCE.json) records the original checker and result
paths and SHA-256 hashes. Only publication paths were adapted in the code;
the mathematical computations and archived numerical values are unchanged.

These finite checks supplement the written proofs; they do not prove the
all-size apolar-ideal or Lefschetz classification. Code and result records
are covered by the repository's [MIT license](../../../LICENSE).
