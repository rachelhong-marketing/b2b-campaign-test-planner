# Paid Media Test & Learn Framework for B2B

A/B testing paid media in B2B is harder than B2C because the volumes are small. Most B2B teams don't have enough MQL or SQL volume to run a statistically clean test on lead quality within a single quarter. That doesn't mean you can't test — it means you have to be deliberate about what you test and what metric you use at each stage.

---

## The Core Problem with B2B Testing

| Metric | Why it's hard to test |
|---|---|
| Click-through rate (CTR) | High enough volume to test on most channels — but CTR doesn't tell you about lead quality |
| Click-to-lead rate | Requires 4,000+ clicks per variant for a typical B2B conversion rate — takes many weeks |
| Lead-to-MQL rate | Requires 3,000+ leads per variant — not achievable in a single test |
| MQL-to-SAL rate | Even harder. Almost never testable per individual test at typical B2B volumes |

**The practical implication:** At most B2B organizations, you can test CTR on Google Search quickly. Everything downstream — lead quality, MQL rate, SQL rate — needs to be treated as a quality check, not a primary decision metric for a single test.

---

## The Six-Step Process

| Step | What happens | Who owns it |
|---|---|---|
| **1. Plan** | Pick one variable, write a hypothesis with a "because," list what stays constant, check whether volume allows a winner | Campaign manager + channel owner |
| **2. Launch** | Tag each variant with UTM parameters; keep all other variables identical (same audience, budget, landing page, dates) | Channel owner |
| **3. Early read** | Clicks, CTR and leads. The platform's experiment tool marks the winner at your confidence level | Channel owner |
| **4. Quality check** | 2–4 weeks after the test ends, check MQLs in the CRM by `utm_content`, to flag if the "winning" variant produces clearly worse leads | Channel owner + marketing ops |
| **5. Log the learning** | One line in the Learning Library: what won, why you think so, confidence level, what to test next | Campaign manager |
| **6. Share** | Copywriters and channel planners use the Learning Library before writing new copy or planning new tests | Shared by whole team |

---

## Step 1: Feasibility Check Before You Launch

Before designing a test, check whether your volume allows a winner.

**Rule of thumb** (25% target lift, 95% confidence, 80% power):

| Channel + Metric | Typical baseline | Needed per variant | Approximate weeks |
|---|---|---|---|
| Google Search CTR | 2–3% | ~10,000 impressions | 2–4 weeks |
| LinkedIn CTR | 0.2–0.4% | ~100,000+ impressions | 10–20 weeks |
| Google click-to-lead | 5–8% | ~3,500 clicks | 30+ weeks |
| LinkedIn click-to-lead | 2–4% | ~7,000 clicks | 30+ weeks |

**What this means in practice:**
- Google Search headline tests: readable in ~3 weeks. Test these first.
- LinkedIn CTR tests: only worthwhile for a substantial change (new image type, completely different message angle). Small tweaks won't read.
- Lead quality tests: pool results across multiple tests of the same type rather than trying to call a winner per test.

---

## Step 2: What to Test (Variable Hierarchy)

Test one variable at a time. Priority order for B2B paid media:

**High impact, faster to read:**
1. Headline / value proposition angle (problem-led vs. outcome-led vs. proof-led)
2. Call-to-action (content offer type: guide vs. report vs. demo vs. calculator)
3. Audience segment (job title targeting variation, company size filter)

**Higher impact, slower to read:**
4. Ad format (image vs. video vs. carousel on LinkedIn)
5. Landing page (layout, headline, form length)
6. Bidding strategy (manual CPC vs. automated bidding — only testable once you have conversion data flowing back)

---

## Step 3: Writing a Hypothesis

Every test needs a hypothesis written as: **"If [change], then [metric] will [direction] because [reason]."**

Good:
> "If we lead with a problem statement ('Your leads aren't converting to pipeline') instead of an outcome statement ('Drive more qualified pipeline'), then Google Search CTR will increase because searchers with active pain are more likely to click problem-led copy."

Bad:
> "Let's test a new headline to see if it performs better."

The "because" matters. It's what you're learning — not just which variant won, but why.

---

## Step 4: UTM Tagging for Test Variants

Use `utm_content` to tag each variant so you can separate performance in analytics and in Salesforce:

```
Variant A (control):   utm_content=hl-problem
Variant B (test):      utm_content=hl-outcome
```

For Google Search, also set `utm_term={keyword}` at the account level so keyword data populates automatically on every click.

**Important:** Keep the same landing page URL for both variants. Different landing pages introduce a second variable and invalidate the test.

---

## Step 5: Let the Platform Call the Winner

Google Ads and LinkedIn already run the statistics. Use their built-in tools instead of comparing two ad groups or campaigns by hand.

| | Google Ads | LinkedIn |
|---|---|---|
| Tool | Experiments (ad variations for copy; custom experiment for keywords or landing pages) | Campaign Manager A/B test |
| Confidence to set | 95% | 90% (LinkedIn recommends at least 90%) |
| Plan to run | 4 weeks | 4 weeks |
| Never stop before | 2 weeks | 2 weeks |
| Stop by | 8 weeks | 8 weeks |

Working rules:

1. **Pre-set the end date and the confidence level.** No stopping early because one variant looks good in week one.
2. **The platform calls the early-read winner** (CTR, then leads). Copy its result and confidence into the Results Log.
3. **MQLs are the quality check.** If the winning variant produces a clearly lower MQL rate, flag it and don't scale it.
4. **No winner by the stop date means the versions perform about the same.** Log it and test a bigger change next.
5. **Small budget or audience?** Run `planner funnel` first. If it says only CTR can be read, treat leads and MQLs as direction only, and pool learnings across similar tests.

Platform settings change, so check the current help pages before you launch.

---

## Step 6: The Learning Library

A shared log that every test feeds into. Minimum fields per entry:

| Field | Example |
|---|---|
| Test ID | PM-002 |
| Channel | Google Search |
| Variable tested | Headline: problem-led vs. outcome-led |
| Hypothesis | Problem-led will increase CTR because... |
| Result | Variant A (problem-led) won: +18% CTR |
| Confidence | High (significant at 95%) |
| MQL quality check | Similar MQL rate — no quality flag |
| Learning | Problem-led headlines outperform outcome-led for this audience segment |
| Next test | Test problem-led vs. proof-led (social proof / customer stat) |

This library is what makes compounding improvement possible. Without it, you re-test the same things and lose institutional knowledge when team members change.

---

## Connection to Smart Bidding

Once you have enough conversion data flowing from Salesforce back to Google Ads (via GCLID + Offline Conversion Import), you can test bidding strategy as a variable:

- Manual CPC (baseline) vs. Target CPA optimizing for MQL conversions
- This requires at least 30+ MQL conversions in a 30-day window for Google's algorithm to have enough signal

For the GCLID setup, see the [B2B Paid Media Playbook](https://github.com/rachelhong2012-dev/b2b-paid-media-playbook/blob/main/tracking/google-ads-to-salesforce.md).

---

## Related

- [Google Ads to Salesforce](https://github.com/rachelhong2012-dev/b2b-paid-media-playbook/blob/main/tracking/google-ads-to-salesforce.md) — how to get keyword and ad data into Salesforce for quality checks
- [UTM Naming Convention](https://github.com/rachelhong2012-dev/b2b-paid-media-playbook/blob/main/tracking/utm-naming-convention.md) — tagging variants correctly so test data flows into reports
- [Channel & Content Guide](https://github.com/rachelhong2012-dev/b2b-paid-media-playbook/blob/main/retargeting/channel-and-content-guide.md) — where each channel sits in the funnel (affects which metric you can test)
