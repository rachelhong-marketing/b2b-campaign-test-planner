# B2B Campaign Test Planner

> **B2B Campaign Lifecycle Toolkit**, step 5 of 7
>
> [1. Position](https://github.com/rachelhong-marketing/b2b-product-marketing-agent) → [2. Plan](https://github.com/rachelhong-marketing/b2b-campaign-assistant) → [3. Content](https://github.com/rachelhong-marketing/b2b-content-strategy-assistant) → [4. Set up](https://github.com/rachelhong-marketing/b2b-paid-media-planner) → **5. Test** → [6. Report](https://github.com/rachelhong-marketing/b2b-campaign-reporting-agent) → [7. Prove](https://github.com/rachelhong-marketing/b2b-pipeline-attribution-tool)

Plan, run and learn from B2B paid media tests that a real team can keep up with: a ready-to-use Excel planner for the day to day, plus Python checks for when budgets or audiences are small. Python, standard library only.

All data and examples here are made up. Nothing comes from a real company.

## Start here: the test planner workbook

`templates/test-planner.xlsx` is a working planner for a sample campaign (Fernhill Software, "2026-Q3 Clean Customer Data"). Open it in Excel or Google Sheets. No code needed.

| Tab | What it's for |
|---|---|
| Test Plan | Tests in waves, one row per test and channel, one variable each, with a hypothesis that has a "because" |
| Tracking Links | Builds each version's tagged link from the plan with formulas, plus the Google final URL suffix |
| How Long to Run | Which platform tool to use, what confidence to set, plan 4 weeks, never stop before 2, stop by 8 |
| Results Log | Copy in the platform's numbers and result; CTR, MQL rate and a quality flag calculate |
| Learning Library | One line per finished test: what won, why, what to test next |
| Channel Rules | What keeps a Google Ads or LinkedIn test clean |

### The practical way to run a test

1. **Plan.** Pick the next wave. Change one thing. Write the "because."
2. **Let the platform call the winner.** Use Google Ads Experiments or LinkedIn's A/B test, set the confidence (95% on Google, 90% on LinkedIn), plan 4 weeks, and don't stop before week 2.
3. **Early read:** clicks, CTR and leads.
4. **Quality check:** MQLs in the CRM, by `utm_content`. A version that wins on clicks but loses on MQLs doesn't win; the Results Log flags it.
5. **Log the learning** so the next wave builds on it.

### The sample test waves

The sample company is Fernhill Software, a made-up company that sells the Fernhill Data Quality Platform, which finds and merges duplicate customer records across systems. Its buyers are data and analytics leaders. It is the same company as in the Campaign Assistant, the Product Marketing Agent and the Content Strategy Assistant. Each wave tests one thing, version A vs. version B.

| Wave | What we're testing | Version A (example) | Version B (example) | Where |
|---|---|---|---|---|
| 1 | **Naming the buyer's role in the headline.** Does saying who the ad is for bring in better leads? | General: "Customer Data Cleanup Software" | Role: "For Data Leaders: Clean Customer Data" | Search and social |
| 2 | **Problem-led vs. solution-led headline.** Does naming the pain bring better leads than naming the fix? The keywords stay the same. | Problem-led: "Bad CRM Data Is Costing You Leads" | Solution-led: "One Clean Record for Every Lead" | Search |
| 2 | **Ad format.** A plain image ad vs. an ad that lets people flip through part of the guide in their feed. | Single image: one graphic with the guide cover | Document ad: first 3 pages of the guide, swipeable | Social |
| 3 | **Question vs. statement headline.** Same message, different form. | "Duplicate Records Slowing Sales?" | "Remove Duplicate CRM Records" | Search and social |
| 4 | **Adding a customer proof line.** Does a proof point make people trust a new vendor enough to fill out the form? | With proof: "Used by 300+ data teams" (sample claim) | No proof line | Search and social |
| 5 | **Form length on the landing page.** Fewer fields usually means more leads. More fields can mean better leads. | Short form, 4 fields: name, work email, company, job title | Long form, 7 fields: also asks company size, CRM used, and biggest data problem | Search and social |
| 6 | **How to target the audience on LinkedIn.** A hand-picked list of job titles vs. LinkedIn's job function and seniority filters. | Job titles: VP of Data, Head of Data Engineering, Director of Analytics (25 in all) | Job function + seniority: Data or IT, Director to VP | Social |

Test IDs are wave + channel (`W1-Search`, `W1-Social`). Running one idea on both channels shows whether it holds across them.

## When volume is small: check before you spend

The platforms can only call a winner if there's enough data. In B2B there often isn't, so use the Python planner below before launching a test on a small budget or account list. It tells you which funnel stage you can actually decide on, and when.

### Why B2B tests are different

Most A/B test calculators assume a consumer funnel: lots of traffic, a purchase minutes after the click, one person per buyer. B2B breaks all three.

| B2B reality | What goes wrong | What this tool does |
|---|---|---|
| **The metric that matters is deep in the funnel.** A 1% click rate, 3% lead rate and 20% MQL rate means 6 MQLs per 1,000 clicks. | Teams pick a winner on click-through, which often doesn't predict qualified leads. | `funnel` works back from lead, MQL or SQL to the clicks, impressions, budget and weeks each one needs, and tells you the deepest stage you can actually decide on. |
| **The sales cycle reports late.** MQL and SQL status show up weeks after the click. | Tests are "read" the day they end, before the leads are qualified. | `funnel` adds the lag, so you see the week you can read each stage, not just when the test stops. |
| **Buyers are accounts, not people.** Five people from one company tend to act alike. | Five leads from one account get counted as five independent results, so tests look more certain than they are. | `size` and `funnel` adjust the sample size for leads per account. |
| **Audiences are small.** An account list or job-title audience may be a few thousand people. | The list gets split in two, falls under the ad platform's minimum, or shows the same ad to the same people dozens of times. | `funnel` warns when each version is under your platform's minimum or would need too many views per person. |

### What it does

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

### Use it with Claude Code (no commands to type)

The repo includes a Claude Code skill, `.claude/skills/b2b-test-planner/SKILL.md`. Download the repo, open the folder in Claude Code, and ask in plain English:

- "Can I test two LinkedIn headlines on MQLs? CTR is 0.8%, 3% of clicks become leads, 25% of leads become MQLs, $9 per click, about 1,200 clicks per version a week."
- "Version A got 20 qualified leads from 879 clicks, B got 31 from 880. Did B win?"
- "Read sample-data/fake-results.csv and tell me which version won."
- "Check my test matrix."

The skill picks the right command, asks for any missing numbers instead of guessing, runs the planner and explains the result in plain English. It ends with a suggested next test. The math always comes from the Python code, not the AI.
### Quick start (command line)

```bash
python3 -m planner funnel --ctr 0.01 --lead-rate 0.03 --mql-rate 0.20 --sql-rate 0.25 \
  --lift 0.5 --cpc 8 --weekly-clicks 1500 --mql-lag-weeks 2 --sql-lag-weeks 8 --leads-per-account 3
python3 -m planner report sample-data/fake-results.csv
python3 -m planner validate sample-data/test-matrix.sample.csv
python3 -m unittest discover -s tests
```

#### Example: what does it take to decide on MQLs?

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

#### Example: a small account-based audience

```
python3 -m planner funnel --ctr 0.008 --lead-rate 0.04 --mql-rate 0.25 --lift 0.5 \
  --weekly-clicks 300 --audience 1800 --platform-min 1000

Warning: Each version would reach about 900 people, below the platform minimum of 1,000. ...
Warning: Each person would need to see the ad about 259 times to reach the impressions needed (limit 10). ...
```

Use the matched audience size (after the platform matches your list), not the size of the list you uploaded. Platform minimums change, so look up the current one and pass it in.

#### Example: clicks say B wins, qualified leads don't

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

### All commands

| Command | Use it to |
|---|---|
| `funnel` | Plan a test around lead, MQL or SQL: clicks, impressions, cost and read week per stage, plus audience warnings. |
| `size` | Sample size for one rate. Add `--leads-per-account` to adjust for accounts. |
| `mdl` | The smallest lift you can detect with the volume you have. |
| `read` | Read a finished test from four numbers. |
| `report` | Read a weekly results file stage by stage. Columns: week, variant, what was shown, clicks, then later stages. |
| `validate` | Check a test matrix for missing fields, two-variable tests, identical tracking tags, and a primary metric that is just the early read. |

### The test matrix (CSV)

The same plan as the workbook's Test Plan tab, as a CSV the planner can check: `templates/test-matrix.csv` (blank) and `sample-data/test-matrix.sample.csv` (the sample waves). Columns: test id, wave, channel, funnel stage, variable, hypothesis, variant A and B, what stays constant, primary metric, early-read metric, test tool, planned weeks, tracking tags for each variant, then status, results, decision, learning and next test.

`planner validate` flags missing fields, two-variable tests, identical tracking tags, an early read used as the deciding metric, and run lengths under 2 or over 8 weeks.

`docs/test-taxonomy.md` is a list of paid search and paid social test ideas (headlines, keywords, ad formats, forms, audiences), with what to hold constant and what to watch out for.

`docs/agent-instructions-template.md` is a starting point for an AI assistant that plans and reads tests, with guardrail checks.

### Rebuild the workbook (optional)

`tools/build_workbook.py` writes the workbook and the sample CSV from one plan. It's the only part that needs a library: `pip install openpyxl`, then `python3 tools/build_workbook.py`.

## Assumptions and limits

- Rates are per click, so a test captures everything the ad or page changes further down the funnel.
- The account adjustment uses a simple design effect, 1 + (leads per account − 1) × ICC. The ICC (how alike people in one account behave) defaults to 0.05; set your own with `--icc`.
- Two-version tests on rates only. No revenue per lead and no multi-version tests.
- Peeking before the planned read week inflates false wins.
- Results are not advice for any specific account.

## The B2B Campaign Lifecycle Toolkit

Seven tools, one per step of a B2B campaign, from positioning to proving pipeline. Each works on its own; together they cover the whole cycle. All sample data is made up.

| Step | Tool | What it does |
|---|---|---|
| 1. Position | [B2B Product Marketing Agent](https://github.com/rachelhong-marketing/b2b-product-marketing-agent) | Define who you sell to and what you say: ideal customer profile, positioning, messaging pillars and proof points, checked for gaps before any campaign starts. |
| 2. Plan | [B2B Campaign Assistant](https://github.com/rachelhong-marketing/b2b-campaign-assistant) | Turn the positioning into a campaign theme, write the campaign plan and master brief, then draft channel briefs, keywords, landing page and ad copy, all checked before launch. |
| 3. Content | [B2B Content Strategy Assistant](https://github.com/rachelhong-marketing/b2b-content-strategy-assistant) | Pick content topics inside the campaign theme from audience questions, news, competitors and keyword data, outline and check each piece so search and AI answer tools can quote it, and log whether AI answers cite you. |
| 4. Set up | [B2B Paid Media Planner](https://github.com/rachelhong-marketing/b2b-paid-media-planner) | Plan channels and retargeting, then build and check tracking links before launch. |
| 5. Test | **B2B Campaign Test Planner** (this repo) | Plan tests in waves, let the ad platform call the winner, check MQLs, and size tests when volume is small. |
| 6. Report | [B2B Campaign Reporting Agent](https://github.com/rachelhong-marketing/b2b-campaign-reporting-agent) | Consolidate ad platform and CRM data into one file, check every channel and funnel stage for gaps, and draft insights. |
| 7. Prove | [B2B Pipeline Attribution Tool](https://github.com/rachelhong-marketing/b2b-pipeline-attribution-tool) | Check the CRM data can be trusted, then show sourced and influenced pipeline. |

## License

MIT. Personal project, not affiliated with any employer.
