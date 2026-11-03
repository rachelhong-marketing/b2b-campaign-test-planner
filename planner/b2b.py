"""The B2B layer. Works back from the metric that decides (lead, MQL, SQL) to clicks,
impressions, budget and weeks, and adjusts for what makes B2B different:
leads clustered in accounts, small audiences, and a sales cycle that reports late."""
import csv
from math import ceil
from . import stats

STAGE_LABELS = {"lead": "Lead", "mql": "MQL", "sql": "SQL"}


def design_effect(leads_per_account=1.0, icc=0.05):
    """People from the same account behave alike, so 10 leads from one company count as less
    than 10 independent leads. Multiply the sample size by this number."""
    if leads_per_account < 1:
        raise ValueError("leads per account must be 1 or more")
    if not 0 <= icc <= 1:
        raise ValueError("icc must be between 0 and 1, e.g. 0.05")
    return 1 + (leads_per_account - 1) * icc


def funnel_plan(ctr, lead_rate, mql_rate, sql_rate=None, lift=0.25, cpc=None, weekly_clicks=None,
                lags=None, deff=1.0, max_weeks=12, alpha=0.05, power=0.8):
    """For each funnel stage, what it takes per version to detect `lift` on that stage.
    Rates are per click, so the test captures everything the ad or page changes downstream."""
    for name, r in (("ctr", ctr), ("lead_rate", lead_rate), ("mql_rate", mql_rate)):
        if not 0 < r < 1:
            raise ValueError(f"{name} must be a rate between 0 and 1")
    per_click = {"lead": lead_rate, "mql": lead_rate * mql_rate}
    if sql_rate:
        per_click["sql"] = per_click["mql"] * sql_rate
    lags = lags or {}
    rows = []
    for stage, rate in per_click.items():
        clicks = ceil(stats.sample_size_per_variant(rate, lift, alpha, power) * deff)
        row = {
            "stage": stage, "rate_per_click": rate, "clicks": clicks,
            "impressions": ceil(clicks / ctr), "expected_outcomes": round(clicks * rate),
            "cost": clicks * cpc if cpc else None, "run_weeks": None, "read_week": None, "fits": None,
        }
        if weekly_clicks:
            row["run_weeks"] = stats.weeks_needed(clicks, weekly_clicks)
            row["read_week"] = row["run_weeks"] + lags.get(stage, 0)
            row["fits"] = row["read_week"] <= max_weeks
        rows.append(row)
    return rows


def deepest_fit(rows):
    """The deepest stage you can still decide on within the time limit, or None."""
    fits = [r for r in rows if r["fits"]]
    return fits[-1] if fits else None


def audience_check(audience, platform_min, impressions_per_variant=None, max_frequency=None):
    """Warn when a B2B audience is too small to split, or would need too many repeat views."""
    msgs = []
    half = audience // 2
    if platform_min and half < platform_min:
        msgs.append(f"Each version would reach about {half:,} people, below the platform minimum of "
                    f"{platform_min:,}. Don't split this audience; test on a broader one or run the versions in sequence.")
    if impressions_per_variant and max_frequency and half > 0:
        freq = impressions_per_variant / half
        if freq > max_frequency:
            msgs.append(f"Each person would need to see the ad about {freq:.0f} times to reach the impressions needed "
                        f"(limit {max_frequency:g}). The audience is too small for this test; test a bigger change or a higher-volume metric.")
    return msgs


def read_funnel_file(path):
    """Read weekly results by version. Column order: what was shown, clicks, then later stages.
    Click-through is clicks per impression; every later stage is counted per click."""
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        cols = [c for c in reader.fieldnames if c not in ("week", "variant")]
        totals = {}
        for row in reader:
            t = totals.setdefault(row["variant"].strip(), dict.fromkeys(cols, 0))
            for c in cols:
                t[c] += float(row[c] or 0)
    if set(totals) != {"A", "B"}:
        raise ValueError("expected variants A and B")
    if len(cols) < 3:
        raise ValueError("need at least: shown, clicks, and one later stage")
    a, b = totals["A"], totals["B"]
    out = [(f"{cols[1]} / {cols[0]}", stats.read_result(a[cols[1]], a[cols[0]], b[cols[1]], b[cols[0]]))]
    for c in cols[2:]:
        out.append((f"{c} / {cols[1]}", stats.read_result(a[c], a[cols[1]], b[c], b[cols[1]])))
    return totals, out
