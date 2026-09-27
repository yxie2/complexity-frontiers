# Orthogonal-frame verification code

These five programs reproduce finite exact-arithmetic checks supporting
*Principal components and singularities of orthogonal frame varieties*.

From the repository root, using Python 3.11 or later:

```sh
python -m pip install -r papers/orthogonal-frame-varieties/anc/requirements.txt
python scripts/verify_paper_code.py orthogonal-frame-varieties
```

The verifier checks artifact hashes, runs the scripts in a temporary copy,
and compares their JSON output with the records in this directory. Only
elapsed times are ignored. It leaves the archived records unchanged.
Use `--integrity-only` to check the package without running computations.

| Program | Coverage |
| --- | --- |
| `orthogonal_basis_veronese.py` | Exact Veronese equations on twelve rational orthogonal bases, isotropic nonmembership witnesses, and a standard-form example. |
| `six_by_six_canonical_controls.py` | Symbolic cross-product identities, 165 nonzero independence coefficients, and 31 Weyl-dimension/Hilbert-series comparisons. |
| `triangular_frame_controls.py` | Integer threshold and stratum calculations for k = 3 through 30; finite-field Gale chart signs, vanishing, and boundary witnesses for k = 3 through 8. |
| `orthogonal_transverse_chart.py` | Six symbolic chart identities, explicit unit-minor rank witnesses, and one residual tangent-quadratic example. |
| `orthogonal_threshold_density.py` | Integer parameter and threshold checks through k = 1000, plus prime-threshold blocks through k = 300. |

Each `.py` file has a corresponding archived `.json` result. The source and
result files are copied unchanged from the existing research computations;
[PROVENANCE.json](PROVENANCE.json) records their source paths and SHA-256 hashes.
Fixed random seeds make the finite samples reproducible.

These checks supplement the manuscript's proofs. Finite samples do not prove
the all-size defining-ideal, normality, depth, or singularity theorems.
Code and result records are covered by the repository's [MIT license](../../../LICENSE).
