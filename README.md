# b2b-campaign-test-planner

Plan B2B campaign tests around the metric that actually matters: leads, MQLs (marketing qualified leads) and SQLs (sales qualified leads), not clicks. Python, standard library only.

All data and examples here are made up. Nothing comes from a real company.

## Why B2B tests are different

Most A/B test calculators assume a consumer funnel: lots of traffic, a purchase minutes after the click, one person per buyer. B2B breaks all three.

| B2B reality | What goes wrong | What this tool does |
|---|---|---|
| **The metric that matters is deep in the funnel.** A 1% click rate, 3% lead rate and 20% MQL rate means 6 MQLs per 1,000 clicks. | Teams pick a winner on click-through, which often doesn't predict qualified leads. | `funnel` works back from lead, MQL or SQL to the clicks, impressions, budget and weeks each one needs, and tells you the deepest stage you can actually decide on. |
| **The sales cycle reports late.** MQL and SQL status show up weeks after the click. | Tests are "read" the day they end, before the leads are qualified. | `funnel` adds the lag, so you see the week you can read each stage, not just when the test stops. |
| **Buyers are accounts, not people.** Five people from one company tend to act alike. | Five leads from one account get counted as five independent results, so tests look more certain than they are. | `size` and `funnel` adjust the sample size for leads per account. |
| **Audiences are small.** An account list or job-title audience may be a few thousand people. | The list gets split in two, falls under the ad platform's minimum, or shows the same ad to the same people dozens of times. | `funnel` warns when each version is under your platform's minimum or would need too many views per person. |

## What it does

```
your funnel rates + budget + lag
            |
         funnel  --->  per stage: clicks, impressions, cost, read week
            |          + "decide on MQL; track SQL as direction only"
            |
     size / mdl  --->  sample size for any single rate, adjusted for accounts
            |
 read / report   --->  real difference, or noise? stage by stage
            |
       validate  --->  one clean, one-variable test per row
```

## Quick start

```bash
python3 -m planner funnel --ctr 0.01 --lead-rate 0.03 --mql-rate 0.20 --sql-rate 0.25 \
  --lift 0.5 --cpc 8 --weekly-clicks 1500 --mql-lag-weeks 2 --sql-lag-weeks 8 --leads-per-account 3
python3 -m planner report sample-data/fake-results.csv
python3 -m planner validate sample-data/test-matrix.sample.csv
python3 -m unittest discover -s tests
```

### Example: what does it take to decide on MQLs?

```
To detect a 50% lift, per version:

Decide on  Per click     Clicks   Impressions  Outcomes        Cost   Read in
Lead           3.00%      2,770       277,000        83     $22,160      wk 2
MQL            0.60%     14,282     1,428,200        86    $114,256     wk 12
SQL            0.15%     57,450     5,745,000        86    $459,600     wk 47

Sizes include x1.10 because leads cluster in accounts (3 per account).

Decide on: MQL (readable by week 12).
Track SQL as direction only, and judge deeper stages over a quarter or across several tests.
```

Reading it: each stage needs about the same number of outcomes (~85 per version), but the deeper the stage, the more clicks and money it takes to get them. SQL would take 47 weeks and $460K per version, so it can't decide a single test.

### Example: a small account-based audience

```
python3 -m planner funnel --ctr 0.008 --lead-rate 0.04 --mql-rate 0.25 --lift 0.5 \
  --weekly-clicks 300 --audience 1800 --platform-min 1000

Warning: Each version would reach about 900 people, below the platform minimum of 1,000. ...
Warning: Each person would need to see the ad about 259 times to reach the impressions needed (limit 10). ...
```

Use the matched audience size (after the platform matches your list), not the size of the list you uploaded. Platform minimums change, so look up the current one and pass it in.

### Example: clicks say B wins, qualified leads don't

`sample-data/fake-results.csv` is four weeks of made-up results.

```
clicks / impressions:  A 1.86%   B 2.03%   p-value 0.014
  Significant: B differs from A
leads / clicks:  A 4.60%   B 4.63%   p-value 0.971
  No evidence of a difference. ...
qualified_leads / clicks:  A 0.35%   B 0.50%   p-value 0.541
  No evidence of a difference. The test was too small to see a lift smaller than about 271%; ...
```

B got more clicks. It did not get more leads or more qualified leads. That is the most common B2B testing mistake, caught.

## All commands

| Command | Use it to |
|---|---|
| `funnel` | Plan a test around lead, MQL or SQL: clicks, impressions, cost and read week per stage, plus audience warnings. |
| `size` | Sample size for one rate. Add `--leads-per-account` to adjust for accounts. |
| `mdl` | The smallest lift you can detect with the volume you have. |
| `read` | Read a finished test from four numbers. |
| `report` | Read a weekly results file stage by stage. Columns: week, variant, what was shown, clicks, then later stages. |
| `validate` | Check a test matrix for missing fields, two-variable tests, identical tracking tags, and a primary metric that is just the early read. |

## The test matrix

One row per test. See `templates/test-matrix.csv` and `sample-data/test-matrix.sample.csv`. Columns: test id, channel, funnel stage, variable, hypothesis, variant A and B, what stays constant, primary metric, early-read metric, planned weeks, tracking tags for each variant, then status, results, decision, learning and next test.

`docs/test-taxonomy.md` maps familiar email tests (subject lines, urgency, personalization, tone) to paid search and paid social.

`docs/agent-instructions-template.md` is a starting point for an AI assistant that plans and reads tests, with guardrail checks.

## Assumptions and limits

- Rates are per click, so a test captures everything the ad or page changes further down the funnel.
- The account adjustment uses a simple design effect, 1 + (leads per account − 1) × ICC. The ICC (how alike people in one account behave) defaults to 0.05; set your own with `--icc`.
- Two-version tests on rates only. No revenue per lead and no multi-version tests.
- Peeking before the planned read week inflates false wins.
- Results are not advice for any specific account.

## License

MIT. Personal project, not affiliated with any employer.
