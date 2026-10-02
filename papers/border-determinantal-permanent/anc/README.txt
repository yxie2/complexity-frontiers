Verification code for
Smooth slices and superquadratic border determinantal complexity of the permanent
Ying Xie, Kennesaw State University, yxie2@kennesaw.edu

Requirements: Python 3.10 or later and the packages in requirements.txt.
Tested with Python 3.13 and SymPy 1.14.0.

From this directory:
    python -m pip install -r requirements.txt
    python -X utf8 run_verification.py

Run without Python's -O option: the exact controls use assertions.
The runner verifies MANIFEST.json, copies the scripts to a temporary
directory, runs eight suites, and compares the resulting JSON with
results/. Only measured runtime is ignored in this comparison.
The supplied files are not overwritten by verification.

Suites:
1. check_polar_composition.py: selector minors and permanent identities,
   matching moment identities, polar coefficients, Schur elimination,
   and additional conservative parameter controls.
2. check_algebraic_transfer.py: multiplicity and characteristic controls.
3. check_non_skew_tradeoff.py: projective-bundle coefficients, state
   Jacobians with reused gates, and the non-skew gate tradeoff.
4. check_rational_state_level.py: level-polar coefficients, valid-division
   pivots, canceled-pole examples, and deliberately incorrect pivots.
5. check_homogeneous_fft.py: homogeneous set-multilinear FFT controls.
6. check_column_coefficient_compression.py: exact symbolic column
   equations, disjointness-matrix ranks, and constant-block removal.
7. check_improved_border_parameters.py: every integer n from 64 to
   1,000,000, plus 9,462 distinct large and boundary samples.
8. check_compressed_border_parameters.py: every integer n from 512 to
   1,000,000, plus 1,886 distinct large and boundary samples.

The two parameter suites perform 2,010,774 checks in total. Their
exhaustive intervals overlap; this is not a count of distinct integers.
Large samples are finite controls. The manuscript proves the uniform
inequalities and their asymptotic consequences.

check_hybrid_charge.py and check_multilinear_fft.py supply shared exact
arithmetic and circuit routines. Mathematical proofs are in the paper;
these computations are supporting checks, not formal proof certificates.
