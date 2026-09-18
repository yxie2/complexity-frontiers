"""Exact checks of the new pair margin; not an asymptotic proof."""
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import sympy as sp

ROOT = Path(__file__).resolve().parent


def main():
    a, c = sp.symbols("a c")
    difference = a*(a-c)/(1-c)-(a-c)**2
    factored = c*(a-c)*(a+1-c)/(1-c)
    assert sp.cancel(difference-factored) == 0

    # Direct counting of ordered pairs for every coloring of small clusters,
    # independent of the closed-form probability used in the manuscript.
    colorings = 0
    for L in range(5, 11):
        for mask in range(1 << L):
            labels = [i for i in range(L) if (mask >> i) & 1]
            count = sum(i != j for i in labels for j in labels)
            density = F(len(labels), L)
            actual = F(count, L*(L-1))
            assert actual == density*(density-F(1,L))/(1-F(1,L))
            assert actual >= max(density-F(1,L), 0)**2
            colorings += 1

    # The product truncation is essential near empty color classes.
    # Check all discrete density pairs over a wider range without square roots.
    density_pairs = 0
    rejected_half_clone = 0
    for L in range(5, 65):
        cL = F(1,L)
        for j in range(L+1):
            A = F(j,L)
            pA = F(j*(j-1),L*(L-1))
            for k in range(L+1):
                B = F(k,L)
                pB = F(k*(k-1),L*(L-1))
                lower = max(A*B-cL*(A+B),0)
                assert pA*pB >= lower**2
                density_pairs += 1
        # One colored label disproves the tempting half-clone deficit.
        assert F(1,L)-F(1,2*L) > 0
        assert F(1*(1-1),L*(L-1)) == 0
        rejected_half_clone += 1

    delta = F(25,54)
    margin = delta*F(33,100)*F(67,100)-F(1,32)
    assert margin == F(16,225)
    excess = margin**2-F(1,200)
    assert excess == F(23,405000)
    assert 35218*excess >= 2 and 35217*excess < 2
    assert F(100-1,3*100) == F(33,100)
    d,L=734,32
    rows=[]
    for name,D in [("base_clique",(d+1)*d*L-1),("state_clique",2*d*L-1)]:
        K=L*D
        rows.append({"host":name,"degree":D,"N_upper_factor":K,
                     "a":str(F(1,7680000)/(2*K)),
                     "b":str(F(1,7680000)/(3*K))})
    result={
        "status":"PASS",
        "checked_at_utc":datetime.now(timezone.utc).isoformat(),
        "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "manuscript_sha256":hashlib.sha256((ROOT.parent/"main.tex").read_bytes()).hexdigest(),
        "symbolic_factorization_checked":True,
        "direct_colorings_checked":colorings,
        "density_pairs_checked":density_pairs,
        "incorrect_half_clone_bounds_rejected":rejected_half_clone,
        "square_root_mean_margin":str(margin),
        "mean_excess_over_one_two_hundredth":str(excess),
        "minimum_integer_v_for_two_term_loss":35218,
        "host_constants":rows,
        "scope":"Finite exact identities and constants only. The sign, spectral, expectation, and conditioning arguments are proved analytically in the manuscript."
    }
    (ROOT/"PAIR_MARGIN_CHECK.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))


if __name__ == "__main__":
    main()
