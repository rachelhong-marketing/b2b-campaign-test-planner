"""Build templates/test-planner.xlsx and sample-data/test-matrix.sample.csv from one test plan.

Optional: only needed if you want to rebuild the workbook. Requires openpyxl (pip install openpyxl).
The planner itself stays standard library only.

    python3 tools/build_workbook.py
"""
import csv
import os
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XLSX = os.path.join(ROOT, "templates", "test-planner.xlsx")
CSV = os.path.join(ROOT, "sample-data", "test-matrix.sample.csv")

SEARCH, SOCIAL = "Paid search (Google Ads)", "Paid social (LinkedIn)"
TOOL = {SEARCH: "Google Ads Experiments", SOCIAL: "LinkedIn A/B test"}
EARLY = {SEARCH: "Clicks, CTR, leads (Google Ads conversions)", SOCIAL: "Clicks, CTR, leads (LinkedIn lead forms)"}
PRIMARY = "MQLs (CRM)"

# Made-up plan for the fictional Fernhill Software, campaign "2026-Q3 Clean Customer Data".
# (wave, channel, funnel stage, variable, hypothesis, A, B, kept constant, utm A, utm B)
PLAN = [
    (1, SEARCH, "Consideration", "Role callout in headline",
     "Naming the buyer's role will lift MQLs because it screens out clicks from people outside the target role",
     'General: "Customer Data Cleanup Software"', 'Role: "For RevOps Teams: Clean CRM Data"',
     "Keywords; descriptions; landing page; budget; dates", "w1-general", "w1-role"),
    (1, SOCIAL, "Consideration", "Role callout in headline",
     "Same idea as W1-Search, so we learn whether it holds across channels",
     'General: "Clean customer data in days, not quarters"', 'Role: "RevOps teams: clean your CRM in days"',
     "Audience; image; intro text; landing page; budget; dates", "w1-general", "w1-role"),
    (2, SEARCH, "Consideration", "Keyword theme",
     "Category keywords will bring more MQLs than competitor-alternative keywords because those searchers are earlier and open to options",
     'Category terms ("customer data cleanup software")', 'Alternative terms ("[competitor] alternative")',
     "Ads; landing page; bidding; budget; dates", "w2-kw-category", "w2-kw-alternative"),
    (2, SOCIAL, "Awareness", "Ad format",
     "A document ad that previews the guide will lift leads because people see the value before they fill the form",
     "Single image ad", "Document ad (first 3 pages of the guide)",
     "Audience; headline; intro text; offer; budget; dates", "w2-single-image", "w2-document"),
    (3, SEARCH, "Consideration", "Headline form",
     "A question headline will lift CTR because it mirrors how people search, with no drop in MQLs",
     'Question: "Duplicate Records Slowing Sales?"', 'Statement: "Remove Duplicate CRM Records"',
     "Keywords; descriptions; landing page; budget; dates", "w3-question", "w3-statement"),
    (3, SOCIAL, "Consideration", "Headline form",
     "Same idea as W3-Search",
     'Question: "Are duplicate records slowing your sales team?"', 'Statement: "Remove duplicate CRM records for good"',
     "Audience; image; intro text; landing page; budget; dates", "w3-question", "w3-statement"),
    (4, SEARCH, "Consideration", "Customer proof line",
     "A customer proof line will lift leads because it lowers the risk of trying a new vendor [proof must be approved]",
     'Proof: "Used by 300+ data teams" [sample claim]', "No proof line",
     "Headlines; keywords; landing page; budget; dates", "w4-proof", "w4-no-proof"),
    (4, SOCIAL, "Consideration", "Customer proof line",
     "Same idea as W4-Search",
     'Proof: "Used by 300+ data teams" [sample claim]', "No proof line",
     "Audience; image; headline; landing page; budget; dates", "w4-proof", "w4-no-proof"),
    (5, SEARCH, "Conversion", "Form length",
     "A short form will get more leads, but the long form may get a higher MQL rate; MQLs decide",
     "Short form (4 fields)", "Long form (7 fields)",
     "Ads; keywords; page copy and design; budget; dates", "w5-form-short", "w5-form-long"),
    (5, SOCIAL, "Conversion", "Form length",
     "Same idea as W5-Search",
     "Short form (4 fields)", "Long form (7 fields)",
     "Audience; ad; page copy and design; budget; dates", "w5-form-short", "w5-form-long"),
    (6, SOCIAL, "Awareness", "Audience targeting",
     "Job function plus seniority will reach more of the right buyers than a job title list because titles vary so much",
     "Job titles (list of 25 titles)", "Job function + seniority",
     "Ad; offer; landing page; budget; dates", "w6-aud-title", "w6-aud-function"),
]
SHORT = {SEARCH: "Search", SOCIAL: "Social"}


def tid(wave, channel):
    return f"W{wave}-{SHORT[channel]}"


# ---------- styles ----------
F = "Arial"
HEAD = PatternFill("solid", fgColor="1F3864")
INPUT = PatternFill("solid", fgColor="FFF2CC")
NOTE = PatternFill("solid", fgColor="F2F2F2")
thin = Side(style="thin", color="BFBFBF")
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)


def title(ws, text, sub):
    ws["A1"] = text
    ws["A1"].font = Font(name=F, size=14, bold=True, color="1F3864")
    ws["A2"] = sub
    ws["A2"].font = Font(name=F, size=10, italic=True, color="595959")


def header(ws, row, cols):
    for j, c in enumerate(cols, 1):
        cell = ws.cell(row, j, c)
        cell.font = Font(name=F, bold=True, color="FFFFFF")
        cell.fill = HEAD
        cell.alignment = Alignment(wrap_text=True, vertical="center")
        cell.border = BOX


def body(cell, fill=None, bold=False):
    cell.font = Font(name=F, size=10, bold=bold)
    cell.alignment = Alignment(wrap_text=True, vertical="top")
    cell.border = BOX
    if fill:
        cell.fill = fill


def widths(ws, ws_widths):
    for i, w in enumerate(ws_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


def notes(ws, start, lines, width_cols=6):
    for k, t in enumerate(lines):
        c = ws.cell(start + k, 1, t)
        c.font = Font(name=F, size=10, bold=(k == 0))
        c.alignment = Alignment(wrap_text=True, vertical="top")
        ws.merge_cells(start_row=start + k, start_column=1, end_row=start + k, end_column=width_cols)
        ws.row_dimensions[start + k].height = 16 if k == 0 else 30


def build():
    wb = Workbook()

    # ---------- How to use ----------
    ws = wb.active
    ws.title = "How to use"
    title(ws, "B2B Paid Media Test Planner", "Fernhill Software (fictional) | Campaign: 2026-Q3 Clean Customer Data | All data is made up.")
    rows = [
        ("Tab", "What it's for"),
        ("1. Test Plan", "The tests in order, one row per test and channel. One variable per test. Yellow cells are yours to edit."),
        ("2. Tracking Links", "Builds the tagged link for each version from the plan. Fill in the yellow inputs once."),
        ("3. How Long to Run", "How long to run, what confidence to set, and how the ad platform tells you there's a winner."),
        ("4. Results Log", "Copy the platform's numbers and result in at the end of each test. CTR and MQL rate calculate."),
        ("5. Learning Library", "One line per finished test: what won, why we think so, and what to test next."),
        ("6. Channel Rules", "Rules that keep a test clean on Google Ads and LinkedIn."),
        ("", ""),
        ("How it works", ""),
        ("1. Plan", "Pick the next row in the Test Plan. Check the hypothesis has a 'because' and only one thing changes."),
        ("2. Check volume", "Small budget or small audience? Run `python3 -m planner funnel` (see README) to see which stage you can actually decide on."),
        ("3. Launch", "Set up the platform's own A/B test, with the confidence level from How Long to Run. Use the links from Tracking Links."),
        ("4. Early read", "Clicks, CTR and leads. The platform tells you when one version wins."),
        ("5. Quality check", "MQLs in the CRM, by utm_content. A version that wins on clicks but loses on MQLs doesn't win."),
        ("6. Log and share", "Results Log, then one line in the Learning Library. Read the library before writing new ads."),
        ("", ""),
        ("Test IDs", "W = wave (the order we run tests). The ID is wave + channel: W1-Search and W1-Social run the same idea on both channels, so we learn whether it holds across them."),
    ]
    for i, (a, b) in enumerate(rows, 4):
        ca, cb = ws.cell(i, 1, a), ws.cell(i, 2, b)
        if i == 4 or a in ("How it works", "Test IDs") and not b or a == "How it works":
            pass
        for c in (ca, cb):
            c.font = Font(name=F, size=10, bold=(c is ca and bool(a)))
            c.alignment = Alignment(wrap_text=True, vertical="top")
    for c in ws[4]:
        c.font = Font(name=F, bold=True, color="FFFFFF")
        c.fill = HEAD
    ws.cell(12, 1).font = Font(name=F, size=11, bold=True, color="1F3864")
    widths(ws, [22, 100])

    # ---------- Test Plan ----------
    tp = wb.create_sheet("Test Plan")
    title(tp, "Test Plan", "Run waves in order. Waves 1, 3, 4 and 5 test one idea on both channels; waves 2 and 6 are channel-specific.")
    cols = ["Test ID", "Wave", "Channel", "Funnel stage", "Variable", "Hypothesis (with a because)", "Version A", "Version B",
            "Keep the same", "utm_content A", "utm_content B", "Early read", "Decides the winner", "Test tool", "Run for (weeks)", "Owner", "Status"]
    header(tp, 4, cols)
    for i, p in enumerate(PLAN, 5):
        wave, ch, stage, var, hyp, a, b, keep, ua, ub = p
        vals = [tid(wave, ch), wave, ch, stage, var, hyp, a, b, keep, ua, ub, EARLY[ch], PRIMARY, TOOL[ch], 4, "", "Not started"]
        for j, v in enumerate(vals, 1):
            body(tp.cell(i, j, v), INPUT if j in (6, 7, 8, 9, 10, 11, 15, 16, 17) else None, bold=(j == 1))
    last = 4 + len(PLAN)
    dv = DataValidation(type="list", formula1='"Not started,Running,Done,Skipped"', allow_blank=True)
    tp.add_data_validation(dv)
    dv.add(f"Q5:Q{last + 10}")
    widths(tp, [12, 6, 20, 13, 18, 42, 30, 30, 28, 15, 15, 24, 13, 20, 9, 10, 12])
    tp.freeze_panes = "B5"
    notes(tp, last + 2, [
        "Notes",
        "Wave 4 needs an approved, sourced proof line. The one here is a made-up sample. Skip the wave if you don't have one.",
        "Wave 5 changes the landing page, so build two page versions that differ only in the form. Everything else stays the same.",
        "Wave 6 changes who sees the ad. Check each version's audience is above LinkedIn's minimum before you launch (planner funnel --audience).",
    ], 9)

    # ---------- Tracking Links ----------
    tl = wb.create_sheet("Tracking Links")
    title(tl, "Tracking Links", "Fill in the yellow inputs once. Every link below builds itself from the Test Plan. Naming follows the Set up step of the toolkit.")
    header(tl, 4, ["Input", "", SEARCH, SOCIAL])
    inputs = [("Landing page", "https://www.fernhill.example/clean-customer-data-guide", "https://www.fernhill.example/clean-customer-data-guide"),
              ("utm_campaign", "2026-q3-clean-customer-data", "2026-q3-clean-customer-data"),
              ("utm_source", "google", "linkedin"),
              ("utm_medium", "paid-search", "paid-social"),
              ("utm_term", "{keyword}", "revops-function-senior")]
    for i, (lab, s, l) in enumerate(inputs, 5):
        body(tl.cell(i, 1, lab), bold=True)
        body(tl.cell(i, 2, ""))
        body(tl.cell(i, 3, s), INPUT)
        body(tl.cell(i, 4, l), INPUT)
    notes(tl, 11, ["How the tags work",
                   "utm_content = wave + version (e.g. w1-role) and is the same on both channels; utm_source tells the channels apart. On Google, {keyword} fills in the search keyword automatically. On LinkedIn, use utm_term for the audience name."], 6)
    header(tl, 14, ["Test ID", "Version", "Channel", "utm_content", "Full link", "Google final URL suffix"])
    r = 15
    for k in range(len(PLAN)):
        prow = 5 + k
        for ver, col in (("A", "J"), ("B", "K")):
            tl.cell(r, 1, f"='Test Plan'!A{prow}")
            tl.cell(r, 2, ver)
            tl.cell(r, 3, f"='Test Plan'!C{prow}")
            tl.cell(r, 4, f"='Test Plan'!{col}{prow}")
            r += 1
    for _ in range(10):  # spare rows for your own tests
        dvc = None
        for j in (1, 2, 3, 4):
            tl.cell(r, j).fill = INPUT
        r += 1
    chan = DataValidation(type="list", formula1=f'"{SEARCH},{SOCIAL}"', allow_blank=True)
    tl.add_data_validation(chan)
    chan.add(f"C{r - 10}:C{r - 1}")
    for row in range(15, r):
        pick = lambda s, l: f'IF(C{row}="{SEARCH}",{s},{l})'
        q = (f'"utm_source="&{pick("$C$7", "$D$7")}&"&utm_medium="&{pick("$C$8", "$D$8")}'
             f'&"&utm_campaign="&{pick("$C$6", "$D$6")}&"&utm_content="&D{row}&"&utm_term="&{pick("$C$9", "$D$9")}')
        tl.cell(row, 5, f'=IF(OR(C{row}="",D{row}=""),"",{pick("$C$5", "$D$5")}&"?"&{q})')
        tl.cell(row, 6, f'=IF(C{row}="{SEARCH}",IF(D{row}="","",{q}),"")')
        for j in range(1, 7):
            c = tl.cell(row, j)
            c.font = Font(name=F, size=10)
            c.border = BOX
            c.alignment = Alignment(vertical="top")
    widths(tl, [16, 9, 24, 34, 120, 100])

    # ---------- How Long to Run ----------
    hl = wb.create_sheet("How Long to Run")
    title(hl, "How Long to Run", "Let the ad platform call the winner. Your job: set it up right, don't stop early, then check MQLs.")
    header(hl, 4, ["", SEARCH, SOCIAL])
    rule_rows = [
        ("Test tool to use", "Experiments (ad variations for copy; custom experiment for keywords or landing pages)", "Campaign Manager A/B test"),
        ("Confidence to set", "95% (raise it from the default)", "90% (LinkedIn recommends at least 90%)"),
        ("Metric to judge the winner", "CTR, then leads", "CTR, then leads"),
        ("Plan to run for", "4 weeks", "4 weeks"),
        ("Never stop before", "2 weeks (covers weekday and weekend patterns)", "2 weeks"),
        ("Stop by", "8 weeks", "8 weeks (LinkedIn's limit is 90 days)"),
        ("How you know there's a winner", "The experiment marks the result as statistically significant", "The test shows a winner at your confidence level and can stop on its own"),
        ("If there's no winner by the stop date", "Log 'No winner'. The two versions perform about the same, so test a bigger change next.", "Same"),
        ("Then check quality", "MQLs in the CRM, by utm_content, 2–4 weeks after the test ends", "Same"),
        ("Small budget or audience?", "Run planner funnel first: if the deepest stage you can read is CTR, treat leads and MQLs as direction only", "Same; LinkedIn often needs a big change (new format or audience) to show a winner in 4 weeks"),
    ]
    for i, row in enumerate(rule_rows, 5):
        for j, v in enumerate(row, 1):
            body(hl.cell(i, j, v), bold=(j == 1))
    notes(hl, 17, ["Why this works",
                   "The platforms already run the statistics. Four weeks gives most search tests enough clicks; social tests with small audiences may only show a winner for large differences, which is why the bigger LinkedIn changes (format, audience) are in their own waves.",
                   "Platform settings change. Check the current help pages before you launch."], 3)
    widths(hl, [30, 60, 60])

    # ---------- Results Log ----------
    rl = wb.create_sheet("Results Log")
    title(rl, "Results Log", "One row per test. Copy the numbers and the platform's result in when the test ends. Grey columns calculate.")
    cols = ["Test ID", "Channel", "Test tool", "Start", "End", "A clicks", "A impressions", "A leads", "A MQLs",
            "B clicks", "B impressions", "B leads", "B MQLs", "A CTR", "B CTR", "CTR lift (B vs A)", "A MQL rate", "B MQL rate",
            "Confidence shown by platform", "Platform result", "Quality check", "Decision", "Learning", "Next test"]
    header(rl, 4, cols)
    for k in range(len(PLAN) + 10):
        r = 5 + k
        if k < len(PLAN):
            rl.cell(r, 1, f"='Test Plan'!A{5 + k}")
            rl.cell(r, 2, f"='Test Plan'!C{5 + k}")
            rl.cell(r, 3, f"='Test Plan'!N{5 + k}")
        rl.cell(r, 14, f'=IF(OR(F{r}="",G{r}="",G{r}=0),"",F{r}/G{r})')
        rl.cell(r, 15, f'=IF(OR(J{r}="",K{r}="",K{r}=0),"",J{r}/K{r})')
        rl.cell(r, 16, f'=IF(OR(N{r}="",O{r}="",N{r}=0),"",O{r}/N{r}-1)')
        rl.cell(r, 17, f'=IF(OR(H{r}="",I{r}="",H{r}=0),"",I{r}/H{r})')
        rl.cell(r, 18, f'=IF(OR(L{r}="",M{r}="",L{r}=0),"",M{r}/L{r})')
        rl.cell(r, 21, f'=IF(OR(T{r}="",Q{r}="",R{r}=""),"",IF(T{r}="A wins",IF(Q{r}<R{r}*0.8,"Check: A has a lower MQL rate","OK"),IF(T{r}="B wins",IF(R{r}<Q{r}*0.8,"Check: B has a lower MQL rate","OK"),"")))')
        for j in range(1, 25):
            c = rl.cell(r, j)
            body(c, NOTE if j in (1, 2, 3, 14, 15, 16, 17, 18, 21) else INPUT)
            if j in (14, 15, 16, 17, 18):
                c.number_format = "0.0%"
            if j in (4, 5):
                c.number_format = "m/d/yyyy"
    res = DataValidation(type="list", formula1='"A wins,B wins,No winner yet,No winner (stopped)"', allow_blank=True)
    rl.add_data_validation(res)
    res.add(f"T5:T{5 + len(PLAN) + 9}")
    widths(rl, [11, 20, 20, 10, 10] + [9] * 8 + [8, 8, 10, 9, 9, 12, 16, 22, 16, 30, 26])
    rl.freeze_panes = "B5"

    # ---------- Learning Library ----------
    ll = wb.create_sheet("Learning Library")
    title(ll, "Learning Library", "One line per finished test. Read this before writing new ads or planning the next wave.")
    header(ll, 4, ["Test ID", "Channel", "Variable", "What won", "Confidence", "MQL quality check", "What we learned (and why we think so)", "Next test"])
    ex = ["Example (made up)", SEARCH, "Headline form", "Question headline: +14% CTR", "95%, platform marked significant",
          "Similar MQL rate, no flag", "Questions that mirror the search help. Keep the claim the same and change only the form.", "Try the question form on LinkedIn (W3-Social)"]
    for j, v in enumerate(ex, 1):
        body(ll.cell(5, j, v), NOTE)
    for r in range(6, 26):
        for j in range(1, 9):
            body(ll.cell(r, j), INPUT)
    widths(ll, [16, 20, 18, 26, 22, 22, 50, 30])

    # ---------- Channel Rules ----------
    cr = wb.create_sheet("Channel Rules")
    title(cr, "Channel Rules", "Keep each test clean so the result means something.")
    header(cr, 4, ["Rule", SEARCH, SOCIAL])
    rules = [
        ("Clean A/B test", "Use Experiments so traffic splits evenly. Don't compare two ad groups side by side.", "Use the A/B test tool, not two campaigns with overlapping audiences."),
        ("One variable", "Pin the headline you're testing in responsive search ads, or the ad will rotate it with others.", "Change one thing: copy, image, format or audience. Never two."),
        ("Don't touch it mid-test", "No bid, budget or keyword changes while the test runs.", "No budget or audience edits while the test runs."),
        ("Tag every version", "Same landing page, different utm_content (see Tracking Links).", "Same landing page, different utm_content."),
        ("Leads aren't MQLs", "Platform conversions are form fills. Check MQLs in the CRM before you scale a winner.", "Lead form fills sync to the CRM; check MQLs before you scale a winner."),
        ("Audience size", "n/a", "Each version must stay above the platform minimum. Check with planner funnel --audience."),
        ("Claims", "Proof lines and numbers need an approved source.", "Same."),
    ]
    for i, row in enumerate(rules, 5):
        for j, v in enumerate(row, 1):
            body(cr.cell(i, j, v), bold=(j == 1))
    widths(cr, [22, 60, 60])

    wb.calculation.fullCalcOnLoad = True
    wb.save(XLSX)

    # ---------- matching CSV for `planner validate` ----------
    fields = ["test_id", "wave", "channel", "funnel_stage", "variable", "hypothesis", "variant_a", "variant_b", "kept_constant",
              "primary_metric", "early_read_metric", "test_tool", "planned_weeks", "utm_content_a", "utm_content_b",
              "status", "result_a", "result_b", "decision", "learning", "next_test"]
    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(fields)
        for wave, ch, stage, var, hyp, a, b, keep, ua, ub in PLAN:
            w.writerow([tid(wave, ch), wave, ch, stage, var, hyp, a, b, keep, PRIMARY, EARLY[ch], TOOL[ch], 4, ua, ub,
                        "planned", "", "", "", "", ""])
    print("saved", XLSX, "and", CSV)


if __name__ == "__main__":
    build()
