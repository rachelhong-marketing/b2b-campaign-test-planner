"""Command line: funnel, size, mdl, read, report, validate."""
import argparse
from . import stats, matrix, b2b


def main(argv=None):
    ap = argparse.ArgumentParser(prog="planner", description="Plan B2B campaign tests around leads, MQLs and SQLs, not clicks.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    f = sub.add_parser("funnel", help="work back from lead / MQL / SQL to clicks, impressions, budget and weeks")
    f.add_argument("--ctr", type=float, required=True, help="click-through rate, e.g. 0.01")
    f.add_argument("--lead-rate", type=float, required=True, help="leads per click, e.g. 0.03")
    f.add_argument("--mql-rate", type=float, required=True, help="MQLs per lead, e.g. 0.20")
    f.add_argument("--sql-rate", type=float, help="SQLs per MQL, e.g. 0.25")
    f.add_argument("--lift", type=float, default=0.25, help="relative lift to detect, e.g. 0.25")
    f.add_argument("--cpc", type=float, help="cost per click")
    f.add_argument("--weekly-clicks", type=float, help="clicks per version per week")
    f.add_argument("--mql-lag-weeks", type=int, default=0, help="weeks from click until MQL status is known")
    f.add_argument("--sql-lag-weeks", type=int, default=0, help="weeks from click until SQL status is known")
    f.add_argument("--max-weeks", type=int, default=12, help="longest you can wait for a read")
    f.add_argument("--leads-per-account", type=float, default=1.0, help="average leads per company")
    f.add_argument("--icc", type=float, default=0.05, help="how alike people in one account behave (0 to 1)")
    f.add_argument("--audience", type=int, help="matched audience size (after match rate, not the uploaded list)")
    f.add_argument("--platform-min", type=int, help="the ad platform's minimum audience size")
    f.add_argument("--max-frequency", type=float, default=10, help="most times one person should see the ad")

    s = sub.add_parser("size", help="how many per variant do I need?")
    s.add_argument("--baseline", type=float, required=True, help="current rate, e.g. 0.04")
    s.add_argument("--lift", type=float, required=True, help="relative lift to detect, e.g. 0.25")
    s.add_argument("--weekly", type=float, help="expected volume per variant per week")
    s.add_argument("--power", type=float, default=0.8)
    s.add_argument("--leads-per-account", type=float, default=1.0, help="average leads per company")
    s.add_argument("--icc", type=float, default=0.05)

    m = sub.add_parser("mdl", help="smallest lift I can detect with what I have")
    m.add_argument("--baseline", type=float, required=True)
    m.add_argument("--n", type=int, required=True, help="per variant")

    r = sub.add_parser("read", help="read a finished test")
    for k in ("success-a", "n-a", "success-b", "n-b"):
        r.add_argument(f"--{k}", type=float, required=True)

    rp = sub.add_parser("report", help="read weekly results by version, stage by stage")
    rp.add_argument("path")

    v = sub.add_parser("validate", help="check a test matrix CSV")
    v.add_argument("path")

    a = ap.parse_args(argv)
    if a.cmd == "funnel":
        return _funnel(a)
    if a.cmd == "size":
        n = stats.sample_size_per_variant(a.baseline, a.lift, power=a.power)
        deff = b2b.design_effect(a.leads_per_account, a.icc)
        if deff > 1:
            n = int(n * deff + 0.999)
            print(f"Adjusted x{deff:.2f} because leads cluster in accounts.")
        print(f"Need about {n:,} per variant ({2 * n:,} total) to detect a {a.lift:.0%} lift from {a.baseline:.2%}.")
        if a.weekly:
            w = stats.weeks_needed(n, a.weekly)
            print(f"At {a.weekly:,.0f} per variant per week that is about {w} weeks.")
            if w > 8:
                print("That is long. Consider a bigger change to test, a higher-volume metric, or reading this as direction only.")
    elif a.cmd == "mdl":
        d = stats.min_detectable_lift(a.baseline, a.n)
        print(f"With {a.n:,} per variant you can only reliably detect a lift of about {d:.0%} or more.")
    elif a.cmd == "read":
        res = stats.read_result(a.success_a, a.n_a, a.success_b, a.n_b)
        print(f"A: {res['rate_a']:.2%}   B: {res['rate_b']:.2%}   relative lift: {res['relative_lift']:+.1%}")
        print(f"p-value: {res['p_value']:.3f}   95% CI for difference: {res['ci_diff_low']:+.2%} to {res['ci_diff_high']:+.2%}")
        print(res["verdict"])
    elif a.cmd == "report":
        totals, reads = b2b.read_funnel_file(a.path)
        for label, res in reads:
            print(f"{label}:  A {res['rate_a']:.2%}   B {res['rate_b']:.2%}   p-value {res['p_value']:.3f}")
            print(f"  {res['verdict']}")
        print("The early stages give direction. The deepest stage you can read decides.")
    else:
        problems = matrix.validate_file(a.path)
        if problems:
            print("\n".join(problems))
            return 1
        print("Matrix OK")
    return 0


def _money(x):
    return f"${x:,.0f}" if x is not None else "-"


def _funnel(a):
    deff = b2b.design_effect(a.leads_per_account, a.icc)
    rows = b2b.funnel_plan(a.ctr, a.lead_rate, a.mql_rate, a.sql_rate, a.lift, a.cpc, a.weekly_clicks,
                           {"mql": a.mql_lag_weeks, "sql": a.sql_lag_weeks}, deff, a.max_weeks)
    print(f"To detect a {a.lift:.0%} lift, per version:\n")
    print(f"{'Decide on':<10}{'Per click':>10}{'Clicks':>11}{'Impressions':>14}{'Outcomes':>10}{'Cost':>12}{'Read in':>10}")
    for r in rows:
        read = f"wk {r['read_week']}" if r["read_week"] else "-"
        print(f"{b2b.STAGE_LABELS[r['stage']]:<10}{r['rate_per_click']:>10.2%}{r['clicks']:>11,}{r['impressions']:>14,}"
              f"{r['expected_outcomes']:>10,}{_money(r['cost']):>12}{read:>10}")
    if deff > 1:
        print(f"\nSizes include x{deff:.2f} because leads cluster in accounts ({a.leads_per_account:g} per account).")
    if a.weekly_clicks:
        best = b2b.deepest_fit(rows)
        print()
        if best is None:
            print(f"Nothing can be read within {a.max_weeks} weeks. Test a bigger change, pool similar tests, "
                  "or treat results as direction only.")
        else:
            label = b2b.STAGE_LABELS[best["stage"]]
            print(f"Decide on: {label} (readable by week {best['read_week']}).")
            deeper = [b2b.STAGE_LABELS[r["stage"]] for r in rows[rows.index(best) + 1:]]
            if deeper:
                print(f"Track {', '.join(deeper)} as direction only, and judge deeper stages over a quarter or across several tests.")
    if a.audience:
        target = (b2b.deepest_fit(rows) if a.weekly_clicks else None) or rows[0]
        for msg in b2b.audience_check(a.audience, a.platform_min, target["impressions"], a.max_frequency):
            print("Warning: " + msg)
    return 0
