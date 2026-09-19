#!/usr/bin/env python3
"""build.py -- emits the Regen Farm Field Log's content pages + sitemap.

WHY THESE THREE PAGES AND NO OTHERS. Each candidate keyword was probed for real
search demand with a reader that ships a positive AND a negative control, and
both controls passed on every single run -- so a zero below is a real zero and
not a broken reader:

    grazing records                      4 suggestions, incl. the literal
                                         "grazing records spreadsheet"        SHIP
    organic certification paperwork      6 suggestions (form / documents /
                                         application / requirements)          SHIP
    organic certification recordkeeping  3 suggestions, incl. the literal
                                         "organic certification record keeping" SHIP
    organic farm record keeping          0                                    DROPPED
    usda organic recordkeeping           0                                    DROPPED
    pasture grazing log                  0                                    DROPPED
    zqxwvj plarn frotz mibblenock        0  (junk control)

HONEST LIMIT: autocomplete measures query SHAPE, never volume -- the same
harvest inverts under a different country code. Page-1 competition is NOT
checked here and remains an open question.

FACTS: the 7 CFR 205.103 wording below is quoted from the regulation text at
govinfo (CFR-2024-title7-vol3-sec205-103). An earlier attempt to verify it
against ecfr.gov returned a bot wall ("your request has been flagged as
potentially automated") which reads exactly like an empty source and produced a
false mismatch. Never quote a regulation from a page that did not actually
fetch.

Run: python build.py    (writes into this directory, then run verify.py)
"""
from pathlib import Path
import html

HERE = Path(__file__).resolve().parent
BASE = "https://fscholtesdowd.github.io/regen-farm-log"

# The regulation's own words. Quoted, not paraphrased -- a paraphrase of a rule
# is how a compliance page becomes wrong.
CFR_BULLETS = [
    "Be adapted to the particular business that the certified operation is conducting;",
    "Fully disclose all activities and transactions of the certified operation, in "
    "sufficient detail as to be readily understood and audited;",
    "Be maintained for not less than 5 years beyond their creation; and",
    "Be sufficient to demonstrate compliance with the Act and the regulations in this part.",
]

PAGES = [
    {
        "slug": "grazing-records",
        "title": "Grazing Records: What to Write Down Every Time You Move Stock",
        "desc": "A plain list of what a grazing record needs, why a spreadsheet "
                "loses the photo and the date, and a free app that keeps both.",
        "h1": "Grazing Records",
        "lede": "Most people keep grazing records in a spreadsheet. It works until "
                "an inspector asks when a paddock last rested, and the answer is in "
                "a photo on your phone instead of the sheet.",
        "body": [
            ("What one grazing record needs",
             "A grazing record is really just four things: which paddock, which mob, "
             "the day they went in, and the day they came out. Everything else is "
             "nice to have. If you only ever capture those four, you can still work "
             "out rest days for any paddock in any season."),
            ("Why rest days are the number that matters",
             "Stocking rate tells you how hard you hit a paddock. Rest days tell you "
             "whether it got to recover. A paddock grazed twice in ten days and a "
             "paddock grazed twice in ninety days can look identical in a spreadsheet "
             "of dates, and completely different in the field. Rest days are the "
             "number worth putting on the screen, and it is the one a spreadsheet "
             "makes you compute by hand every time."),
            ("Where the spreadsheet breaks",
             "Two places. First, you are standing at a gate with cold hands and a "
             "phone, not sitting at a laptop, so the row gets written later or not at "
             "all. Second, the proof of what the paddock looked like is a photo, and a "
             "photo does not live in a cell. By the time you need both together, they "
             "are in different places."),
            ("A record you make at the gate",
             "The Field Log is a web app that opens on a phone and works with no "
             "signal. You pick the paddock, tap moved in or moved out, and add a photo "
             "if you want one. It works out rest days for every paddock on its own. "
             "Nothing is uploaded anywhere; the log lives on your phone."),
        ],
    },
    {
        "slug": "organic-certification-paperwork",
        "title": "Organic Certification Paperwork: What the Rule Actually Asks For",
        "desc": "The four things 7 CFR 205.103 requires of your records, quoted, "
                "plus what that means for a small farm keeping them by hand.",
        "h1": "Organic Certification Paperwork",
        "lede": "People picture a mountain of forms. The recordkeeping rule itself is "
                "four sentences long. It is worth reading them once, because they ask "
                "for less than most farms think, and something different.",
        "body": [
            ("What the rule says, word for word",
             "Under 7 CFR 205.103, a certified operation must keep records that:"),
            ("What \"adapted to the particular business\" gets you",
             "This is the part people miss. The rule does not hand you a form. It says "
             "your records have to suit your operation. A market garden and a grazing "
             "operation are allowed to keep completely different records and both be "
             "right. You are not failing because your log does not look like someone "
             "else's."),
            ("What \"readily understood and audited\" really means",
             "It means a stranger has to be able to follow it. That is a higher bar "
             "than \"I know what this means.\" Shorthand only you can read, undated "
             "notes, and a pile of receipts with no link to a field all fail this test "
             "even though the information is technically there."),
            ("Five years is longer than it sounds",
             "Records have to be kept for not less than 5 years beyond their creation. "
             "A phone gets replaced about every three. Whatever you keep records in, "
             "the question to ask is how you get five years of them out of it and onto "
             "something you still control."),
        ],
        "cfr": True,
    },
    {
        "slug": "organic-certification-recordkeeping",
        "title": "Organic Certification Record Keeping Without a Filing Cabinet",
        "desc": "A small-farm system for organic record keeping: log at the moment "
                "it happens, keep the photo with the entry, export when asked.",
        "h1": "Organic Certification Record Keeping",
        "lede": "Record keeping fails for a boring reason. Not because people do not "
                "care, but because the record gets made hours after the work, from "
                "memory, at a kitchen table.",
        "body": [
            ("Log it where it happens, not where the computer is",
             "The single biggest improvement to farm records is shortening the gap "
             "between doing the thing and writing it down. An entry made at the gate "
             "is accurate. The same entry made that evening is a guess with a "
             "confident tone. Any system that requires you to be indoors will quietly "
             "lose the details that make a record worth keeping."),
            ("Keep the photo with the entry, not in the camera roll",
             "A photo of a cover crop stand, an amendment bag label, or a pasture "
             "before and after is worth more than a sentence describing it. But a "
             "photo in a camera roll, separated from the date and the paddock it "
             "belongs to, is not a record. It is a picture. The two have to be stored "
             "as one thing or they drift apart within a week."),
            ("Write down the source, every time",
             "For any input that goes on the ground, the source matters as much as the "
             "amount. Supplier, product name, whether it is listed. This is the field "
             "most people leave blank and the one most likely to be asked about, "
             "because it is what connects what you applied to whether you were allowed "
             "to apply it."),
            ("Export should be one button, once a year",
             "You keep records all year and need them in a readable pile exactly once. "
             "So the export is the part worth getting right: everything grouped by "
             "paddock, in date order, with the photos in line, ready to print or save "
             "as a PDF."),
        ],
    },
]

SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{base}/{slug}/">
<style>
  :root {{ --bg:#faf9f6; --surface:#fff; --text:#22251f; --dim:#5d6157;
           --accent:#3a5a2a; --border:#e0ddd4; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--text);
         font: 16px/1.65 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
  .wrap {{ max-width: 42rem; margin: 0 auto; padding: 24px 16px 64px; }}
  a {{ color: var(--accent); }}
  h1 {{ font-size: 1.6rem; line-height:1.25; margin: 0 0 4px; }}
  h2 {{ font-size: 1.1rem; margin: 32px 0 8px; }}
  .lede {{ font-size: 1.05rem; color: var(--dim); margin: 12px 0 8px; }}
  .cta {{ background: var(--surface); border:1px solid var(--accent);
          border-radius:10px; padding:16px; margin:32px 0; }}
  .cta-title {{ font-weight:600; margin-bottom:6px; }}
  .btn {{ display:block; text-align:center; background:var(--accent); color:#fff;
          text-decoration:none; padding:12px; border-radius:8px; margin-top:10px;
          font-weight:600; }}
  .btn.alt {{ background:var(--surface); color:var(--accent); border:1px solid var(--accent); }}
  ol.cfr {{ background:var(--surface); border:1px solid var(--border);
            border-radius:8px; padding:14px 14px 14px 32px; }}
  ol.cfr li {{ margin-bottom:8px; }}
  .src {{ font-size:0.85rem; color:var(--dim); }}
  nav.crumbs {{ font-size:0.85rem; margin-bottom:16px; }}
  footer {{ margin-top:48px; border-top:1px solid var(--border); padding-top:16px;
            font-size:0.85rem; color:var(--dim); }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --bg:#14161a; --surface:#1c1f24; --text:#e8e6e1; --dim:#9aa090;
             --accent:#8fbf6a; --border:#2a2f36; }}
    .btn {{ color:#14161a; }}
  }}
</style>
</head>
<body>
<div class="wrap">
<nav class="crumbs"><a href="{base}/">&larr; Regen Farm Field Log</a></nav>
<h1>{h1}</h1>
<p class="lede">{lede}</p>
{body}
<div class="cta">
  <div class="cta-title">Keep this log on your phone</div>
  <p>The Field Log is a free web app. It works with no signal, keeps photos with
  the entry, and works out paddock rest days for you. One paddock free, forever.</p>
  <a class="btn" href="{base}/">Open the free Field Log</a>
  <a class="btn alt" href="https://wealthywellness0.gumroad.com/l/regenfieldlog">Unlock every paddock + audit PDF &mdash; $29</a>
</div>
<footer>
  Regen Farm Field Log &middot; <a href="{base}/">the app</a>
  <p>General information about recordkeeping, not legal or certification advice.
  Your certifier is the authority on what your operation must keep.</p>
</footer>
</div>
</body>
</html>
"""


def render(page):
    parts = []
    for i, (h2, text) in enumerate(page["body"]):
        parts.append(f"<h2>{html.escape(h2)}</h2>\n<p>{html.escape(text)}</p>")
        # The quoted rule text sits under its own heading on the paperwork page.
        if page.get("cfr") and i == 0:
            items = "\n".join(f"  <li>{html.escape(b)}</li>" for b in CFR_BULLETS)
            parts.append(f'<ol class="cfr">\n{items}\n</ol>')
            parts.append('<p class="src">Source: 7 CFR 205.103(b), quoted from the '
                         '<a href="https://www.govinfo.gov/content/pkg/CFR-2024-title7-vol3/xml/'
                         'CFR-2024-title7-vol3-sec205-103.xml">Code of Federal Regulations</a>.</p>')
    return SHELL.format(base=BASE, body="\n".join(parts), **{
        k: html.escape(v, quote=True) if k in ("title", "desc") else v
        for k, v in page.items() if k in ("slug", "title", "desc", "h1", "lede")
    })


def main():
    written = []
    for page in PAGES:
        d = HERE / page["slug"]
        d.mkdir(exist_ok=True)
        # Build the whole string first, then write -- open(p,"w") truncates
        # before it fails, and a half-written page is worse than none.
        text = render(page)
        assert "<h1>" in text and len(text) > 2000, f"{page['slug']} rendered short"
        (d / "index.html").write_text(text, encoding="utf-8")
        written.append(page["slug"])

    urls = [f"{BASE}/"] + [f"{BASE}/{s}/" for s in written]
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
               + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls)
               + "</urlset>\n")
    (HERE / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    (HERE / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n", encoding="utf-8")

    print(f"built {len(written)} pages: {', '.join(written)}")
    print(f"sitemap: {len(urls)} urls")


if __name__ == "__main__":
    main()
