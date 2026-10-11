"""Revolving first-hire guarantee pool: break-even contribution and ruin.

Analysis only: nothing here moves money. Stdlib only and deterministic
(fixed seeds), so every figure in README.md can be reproduced with
`python3 experiments/revolving-guarantee/model.py`.

One job, in order:
  - with probability p the covered event happens (client nonpayment, or a
    failed first job in the client-refund variant) and the pool pays G;
  - otherwise the worker is paid, and remits the contribution k with
    probability q;
  - every job costs the pool c (verification, payout and collection).
Pool change per job: +k with prob (1-p)q, -G with prob p, then -c.
"""
import math
import random

def break_even(p, q, G, c):
    """Contribution k* that keeps expected pool principal unchanged."""
    if not 0 <= p < 1 or not 0 < q <= 1:
        raise ValueError("need 0 <= p < 1 and 0 < q <= 1")
    return (p * G + c) / ((1 - p) * q)

def drift(p, q, G, c, k):
    """Expected pool change per job."""
    return (1 - p) * q * k - p * G - c

def adjustment_coefficient(p, q, G, c, k):
    """Lundberg R > 0 solving E[exp(-R X)] = 1; None if drift <= 0.

    The Cramer-Lundberg bound then gives P(ever ruined | capital u) <= exp(-R u).
    """
    if drift(p, q, G, c, k) <= 0:
        return None
    def f(r):
        return ((1 - p) * q * math.exp(-r * (k - c)) + p * math.exp(r * (G + c))
                + (1 - p) * (1 - q) * math.exp(r * c) - 1)
    lo, hi = 1e-12, 1.0
    while f(hi) < 0:
        hi *= 2
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(mid) < 0:
            lo = mid
        else:
            hi = mid
    return lo

def early_death(p, q):
    """P(the first covered event comes before the first remitted contribution).

    With capital below 2(G + c), one such claim leaves too little to back
    another job, and with no job there is no contribution: the pool stops.
    This floor does not depend on the contribution k.
    """
    return p / (p + (1 - p) * q)

def worker_net_per_job(p, q, G, c, k, wage, a, s, refunds_to_workers):
    """Expected net gain to workers per job against what is otherwise available.

    a: share of guaranteed jobs the guarantee causes (counterfactual hires);
    s: the worker's net share of the wage after valuing their time.
    refunds_to_workers: True when the pool pays the worker on the covered
    event (nonpayment insurance); False when it refunds the client.
    """
    gain = a * (1 - p) * s * wage
    if refunds_to_workers:
        gain += p * G
    return gain - (1 - p) * q * k

def simulate(p, q, G, c, k, capital=100.0, jobs=1000, runs=20000, seed=7,
             shock_share=0.0, shock_factor=1.0, block=10):
    """Share of runs ruined within `jobs` sequential jobs.

    Ruin: the pool cannot pay a claim in full, or cannot cover c.
    Correlated failures: jobs come in blocks of `block`; a block is a shock
    block with probability shock_share, where the covered-event probability
    is p * shock_factor (capped at 1). Other blocks use a lower probability,
    so the average stays p and pricing on p is not mechanically wrong.
    """
    rng = random.Random(seed)
    p_bad = min(1.0, p * shock_factor)
    p_good = (p - shock_share * p_bad) / (1 - shock_share) if shock_share < 1 else p_bad
    if p_good < 0:
        raise ValueError("shock too large for this p")
    ruined = 0
    jobs_backed = 0
    for _ in range(runs):
        x = capital
        pj = p
        for j in range(jobs):
            if shock_share and j % block == 0:
                pj = p_bad if rng.random() < shock_share else p_good
            if x < G + c:
                ruined += 1
                break
            x -= c
            u = rng.random()
            if u < pj:
                x -= G
            elif rng.random() < q:
                x += k
            jobs_backed += 1
    return ruined / runs, jobs_backed / runs

def capital_for_target(p, q, G, c, k, target=0.05, jobs=1000, runs=2000, **shock):
    """Smallest starting capital (to $10) with simulated ruin within `jobs` at or below target."""
    lo, hi = 0.0, 100000.0
    if simulate(p, q, G, c, k, capital=hi, jobs=jobs, runs=runs, **shock)[0] > target:
        return None
    while hi - lo > 10:
        mid = (lo + hi) / 2
        if simulate(p, q, G, c, k, capital=mid, jobs=jobs, runs=runs, **shock)[0] <= target:
            hi = mid
        else:
            lo = mid
    return math.ceil(hi / 10) * 10

def loading_for_target(p, q, G, c, capital=100.0, target=0.05, jobs=1000, runs=2000, **shock):
    """Smallest k (to $0.25) with simulated ruin within `jobs` at or below target.

    Bisection on k between break-even and 5G; ruin falls as k rises.
    """
    lo = math.floor(break_even(p, q, G, c) * 4) / 4
    hi = 5.0 * G
    if simulate(p, q, G, c, hi, capital=capital, jobs=jobs, runs=runs, **shock)[0] > target:
        return None
    while hi - lo > 0.25:
        mid = math.floor((lo + hi) * 2) / 4
        if mid <= lo:
            mid = lo + 0.25
        if simulate(p, q, G, c, mid, capital=capital, jobs=jobs, runs=runs, **shock)[0] <= target:
            hi = mid
        else:
            lo = mid
    return hi

SCENARIOS = [
    # name, p, q, G, c
    ("platform nonpayment, low", 0.02, 0.9, 60, 1.0),
    ("platform nonpayment, mid", 0.05, 0.7, 60, 2.0),
    ("failed first job (Pallais 18%)", 0.18, 0.7, 60, 2.0),
    ("failed first job, weak remittance", 0.18, 0.5, 60, 2.0),
    ("failed first job, high", 0.30, 0.7, 60, 2.0),
    ("partial guarantee G=$20", 0.18, 0.7, 20, 2.0),
]

def report(wage=60.0):
    rows = []
    for name, p, q, G, c in SCENARIOS:
        k0 = break_even(p, q, G, c)
        ruin0, backed0 = simulate(p, q, G, c, k0, jobs=1000, runs=2000)
        k5 = loading_for_target(p, q, G, c)
        k5s = loading_for_target(p, q, G, c, shock_share=0.1, shock_factor=3.0)
        R = adjustment_coefficient(p, q, G, c, k5) if k5 else None
        k125 = 1.25 * k0
        rows.append({
            "scenario": name, "p": p, "q": q, "G": G, "c": c,
            "k_break_even": round(k0, 2), "k_share_of_wage": round(k0 / wage, 3),
            "ruin_1000_jobs_at_break_even": round(ruin0, 3),
            "mean_jobs_backed_at_break_even": round(backed0, 1),
            "dead_before_first_contribution": round(early_death(p, q), 3) if 100 < 2 * (G + c) else None,
            "k_for_5pct_ruin_100usd": k5,
            "k_for_5pct_ruin_100usd_correlated": k5s,
            "lundberg_bound_at_that_k": round(math.exp(-R * 100), 3) if R else None,
            "capital_for_5pct_ruin_at_1.25x_break_even": capital_for_target(p, q, G, c, k125),
            "capital_for_5pct_ruin_at_1.25x_correlated": capital_for_target(p, q, G, c, k125, shock_share=0.1, shock_factor=3.0),
        })
    return rows

if __name__ == "__main__":
    import json
    print(json.dumps(report(), indent=1))
