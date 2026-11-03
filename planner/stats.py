"""Sample size, power and read-out math for A/B tests on rates (CTR, conversion, MQL rate).
Standard library only. All formulas are the textbook two-proportion z-test."""
from math import sqrt, ceil
from statistics import NormalDist

N = NormalDist()


def sample_size_per_variant(baseline, relative_lift, alpha=0.05, power=0.8):
    """Visitors (or sends, or clicks) needed in EACH variant to detect a relative lift."""
    if not 0 < baseline < 1:
        raise ValueError("baseline must be a rate between 0 and 1, e.g. 0.04")
    if relative_lift <= 0:
        raise ValueError("relative_lift must be positive, e.g. 0.25 for +25%")
    p1 = baseline
    p2 = baseline * (1 + relative_lift)
    if p2 >= 1:
        raise ValueError("lift pushes the rate above 100%")
    z_a = N.inv_cdf(1 - alpha / 2)
    z_b = N.inv_cdf(power)
    p_bar = (p1 + p2) / 2
    num = (z_a * sqrt(2 * p_bar * (1 - p_bar)) + z_b * sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    return ceil(num / (p2 - p1) ** 2)


def min_detectable_lift(baseline, n_per_variant, alpha=0.05, power=0.8):
    """Smallest relative lift you could reliably detect with n per variant (bisection)."""
    lo, hi = 1e-4, 20.0
    for _ in range(80):
        mid = (lo + hi) / 2
        try:
            need = sample_size_per_variant(baseline, mid, alpha, power)
        except ValueError:
            hi = mid
            continue
        if need > n_per_variant:
            lo = mid
        else:
            hi = mid
    return hi


def weeks_needed(n_per_variant, weekly_volume_per_variant):
    if weekly_volume_per_variant <= 0:
        raise ValueError("weekly volume must be positive")
    return ceil(n_per_variant / weekly_volume_per_variant)


def read_result(success_a, n_a, success_b, n_b, alpha=0.05):
    """Two-proportion z-test plus an honest verdict."""
    if min(n_a, n_b) <= 0:
        raise ValueError("sample sizes must be positive")
    pa, pb = success_a / n_a, success_b / n_b
    pooled = (success_a + success_b) / (n_a + n_b)
    se = sqrt(pooled * (1 - pooled) * (1 / n_a + 1 / n_b)) or float("nan")
    z = (pb - pa) / se if se and se == se else 0.0
    p_value = 2 * (1 - N.cdf(abs(z)))
    se_diff = sqrt(pa * (1 - pa) / n_a + pb * (1 - pb) / n_b)
    zc = N.inv_cdf(1 - alpha / 2)
    ci = (pb - pa - zc * se_diff, pb - pa + zc * se_diff)
    rel = (pb - pa) / pa if pa else float("nan")
    n_min = min(n_a, n_b)
    base = pa if pa > 0 else pooled
    mdl = min_detectable_lift(base, n_min) if 0 < base < 1 else float("nan")
    if p_value < alpha:
        verdict = "Significant: B differs from A" if pb != pa else "No difference"
    else:
        verdict = ("No evidence of a difference. The test was too small to see a lift smaller than "
                   f"about {mdl:.0%}; treat as noise or directional only.")
    return {
        "rate_a": pa, "rate_b": pb, "relative_lift": rel, "z": z, "p_value": p_value,
        "ci_diff_low": ci[0], "ci_diff_high": ci[1], "min_detectable_lift": mdl, "verdict": verdict,
    }
