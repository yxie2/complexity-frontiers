Verification material for
Sharp Newton-edge bounds and cancellation families with one nonzero quadratic norm
Ying Xie, Kennesaw State University
yxie2@kennesaw.edu

Requirements: Python 3.11 or later, standard library only.
Extract this archive into an empty directory, then run:

    python -B -X utf8 verify.py

The runner validates MANIFEST.json and executes five checking programs.
No solver, network connection, or other research files are required.
Do not use Python's -O or -OO options: exact checks use assertions.
Reports are written into the extracted directory during verification.

verify_sharp_six.py checks complete finite coverage and exact integer
contradictions for the eleven-edge upper bound. Its inputs are
GEOMETRY_CERTIFICATE.json, PROOF_BATCH.json, and the corresponding trees
in linear_proofs/. The rules are defined in certificate_system.py and
audited separately by the checker.

verify_unit_six.py checks the ten-edge upper bound for edges of width one,
using UNIT_SIX_PROOFS.json and its selected trees.

verify_unit10_examples.py expands six integer equality examples, checks
all supporting lines and coefficient norms, verifies sixty root lifts,
and checks the formal field-uniform sharpness calculation. The module
verify_field_sharpness.py supplies exact Laurent-polynomial arithmetic.

verify_positive_control.py evaluates the rule families on an exact
eleven-edge example and checks rejection of invalid arithmetic certificates.

verify_families.py checks six five-support examples, twenty-five members
of the larger family, 144 root lifts, and the uniform tail inequalities.
Its coefficients are in family_examples/; polynomial_arithmetic.py supplies
exact rational expansion and lower-hull arithmetic.

The manuscript proves the reduction to the finite systems, the validity
of their rules, and the uniform assertions about primes and support sizes.
The programs check the finite certificates and the stated exact arithmetic.
