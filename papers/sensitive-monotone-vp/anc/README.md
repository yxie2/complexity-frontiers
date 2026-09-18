# Finite checks accompanying the preprint

**Strongly Exponential Sensitive Monotone Bounds in VP via Eulerian Conditioning**

Ying Xie, Kennesaw State University, yxie2@kennesaw.edu.

These files reproduce the finite checks in Appendix D. The written proofs
in main.tex are the authoritative presentation. Running these programs
does not prove the asymptotic lower bounds.

## Run

Use Python 3.10 or later. The supplied result records specify the exact
Python and package versions used for the packaging check. From this directory:

    python -m pip install -r requirements.txt
    python -X utf8 run_checks.py

The runner executes seven checks, writes their result JSON files and
RUN_CHECKS.json, and saves diagnostic output in check_logs/.
It does not access the network. Installing dependencies is a separate step.
Each checker can also be run individually with Python.

| Script | What is checked |
| --- | --- |
| check_euler_conditioning.py | Exact BEST multiplicities, last-exit sampling, local permutation exposure, direct parity gadgets, and rational constants |
| check_euler_refinements.py | Smaller-host implementation, locality, state-spectrum identities, and finite parameter checks |
| check_pair_margin.py | Discrete pair-density inequalities and exact cluster-coloring calculations |
| check_shared_decomposition.py | Balanced-product removal with global substitution at every use of a shared gate |
| check_lowest_component.py | Least homogeneous component extraction in shared arithmetic DAGs |
| check_counting_normalization.py | Gate profiles, exact normalization, Boolean agreement, and a large-formal-degree example |
| check_shared_charge.py | Global replacement with exponentially many paths, distinct nodes computing the same polynomial, reciprocal rescalings, and the signed rectangle charge |

The files verify.py, check_inactive_forest.py, and check_all_step_cover.py
are imported helper modules. Only the functions
called by the listed checks are needed here.

MANIFEST.json records the names, sizes, and SHA-256 hashes of the supplied
ancillary files. The result records identify the checker and helper source
hashes; where a written argument is referenced, its hash identifies ../main.tex.
No exploratory notes or external workspace files are needed. Result timestamps
and elapsed times change on a rerun; the exact finite counts and identities
are the relevant comparisons.

The toy graphs do not satisfy the large-degree spectral hypotheses of the
main theorem. Graph examples, fixed pseudorandom seeds, and exhaustive
coverage are distinguished in the individual JSON records.
