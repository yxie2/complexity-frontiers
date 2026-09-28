# Exact supplementary checks

These files accompany Ying Xie's *Sharp singularity thresholds for
off-diagonal Gram maps*. The proofs in the paper do not depend on the
finite computations.

Use Python 3.11 or later. No third-party packages are required. From this
directory, run:

```text
python -X utf8 check_gram_fourier_arithmetic.py
python -X utf8 check_direct_gram_counts.py
python -X utf8 check_odd_gram_first_jets.py
python -X utf8 check_valuation_strata.py
```

The programs write their JSON results beside the scripts. The direct-count
program takes roughly two minutes on the development machine, the arithmetic
and first-jet programs take roughly fifteen seconds each, and the standalone
valuation checker takes less than a second. Timings depend on the machine.
Each JSON result records the producer's SHA-256 hash. A successful run exits
normally and writes a top-level `status` of `PASS`; failed assertions stop it.

- `check_gram_fourier_arithmetic.py` checks threshold arithmetic through
  h=20,000, the exact ideal-threshold arithmetic, finite-ring product and
  Gauss identities, and exhaustive small hollow-matrix controls.
  Its `necessity` result also compares the direct even/odd isotropic
  obstruction with an independent maximization of F(h) for 179,101
  parameter pairs. This comparison does not use the prime-threshold formula.
- `check_direct_gram_counts.py` compares direct vector enumeration with
  exact Fourier inversion for 22 prescribed fibers over small fields,
  Z/9, and F_3[t]/(t^2).
- `check_odd_gram_first_jets.py` compares direct first-jet counts obtained
  from Jacobian ranks with signed Fourier inversion. It imports the Ring
  class from `check_direct_gram_counts.py`; keep both scripts together.
- `check_valuation_strata.py` is standalone. It enumerates kernels directly,
  without Smith elimination, for 3,048 hollow matrices in twelve cases over
  Z/3^L and F_3[t]/(t^L). It checks the common-valuation decomposition,
  the exact scalar product count, all 280 fixed-pivot fibers in these cases,
  and the mixed-valuation example over Z/27. Its image-length histograms
  verify the pivot bound coefficient by coefficient, hence for every
  positive weight parameter in the listed finite cases. The output is
  `valuation_strata_checks.json`; the run takes less than a second on
  the development machine.

The supplied JSON outputs all have status PASS. SHA256SUMS.txt records
the packaged scripts and results. Check those hashes before rerunning:
the programs overwrite their result files, and elapsed times will change.
To compare a rerun with the supplied result, omit only its top-level
`seconds` field; the remaining JSON data should agree exactly.

Both the arXiv source archive and the review archive contain this entire
directory. The review archive also includes the paper PDF, editable
`main.tex`, a root README, and checksums for every distributed file.
The review PDF also contains all ten files in this directory as document
attachments, together with `gram_verification_code.zip`. Save that ZIP from
the PDF reader's Attachments panel and extract it to obtain `anc/`.
Some browser previews do not expose PDF attachments; a PDF reader with
an Attachments panel or the external archive provides access in that case.

These finite checks supplement the proofs in the paper. They do not verify
constructibility, flatness, geometric integrality over arbitrary fields,
or the log-resolution argument for the threshold at the origin.
