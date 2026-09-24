#!/usr/bin/env python3
"""verify.py -- the publish gate for the Regen Farm Field Log.

Two halves:
  OFFLINE  structural invariants + the licence-gate selftest + pseo_gate
  LIVE     --live hits the public GitHub Pages URLs, WITH A 404 CONTROL

The 404 control is the point. A verifier that only ever asks for pages that
exist cannot tell "the site is up" from "every request returns something".
If the nonsense URL also returns 200, every other 200 in this run is worthless
and the whole verdict is withheld.

INVARIANTS, not counts (fix the factory, not the artifact): this asserts that
EVERY paddock write is guarded, not that there happen to be two of them today.

Run:  python verify.py            (offline only)
      python verify.py --live     (offline, then the public URLs)
"""
from pathlib import Path
import argparse
import hashlib
import re
import subprocess
import sys
import urllib.error
import urllib.request

HERE = Path(__file__).resolve().parent
BASE = "https://fscholtesdowd.github.io/regen-farm-log"
# The distinctness gate lives in a shared tooling directory outside this repo.
# Locate it by walking up and testing for the tool ITSELF, never by counting
# directory hops and never by a marker that only exists on one machine.
_REL = Path("02 - Projects") / "Farm Brain"
_ROOT = next((d for d in HERE.parents if (d / _REL / "pseo_gate.py").exists()), None)
TOOLS = (_ROOT / _REL) if _ROOT else HERE / "_tools_not_found"

# The buyer unlock plaintext deliberately lives OUTSIDE this public repo.
_PLAINTEXT_FILE = (_ROOT / "02 - Projects" / "Etsy Digital Products"
                   / "Regen Field Log - Unlock Code.md") if _ROOT else HERE / "_absent"

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(f"{'PASS' if ok else 'FAIL'}  {name}{('  -- ' + detail) if detail else ''}")
    return ok


def offline():
    app = (HERE / "js" / "app.js").read_text(encoding="utf-8")
    index = (HERE / "index.html").read_text(encoding="utf-8")
    sw = (HERE / "sw.js").read_text(encoding="utf-8")

    # --- the licence gate can actually block ---
    r = subprocess.run([sys.executable and "node", "selftest.js"], cwd=HERE,
                       capture_output=True, text=True)
    check("licence selftest exits 0", r.returncode == 0,
          (r.stdout or r.stderr).strip().splitlines()[-1] if (r.stdout or r.stderr) else "")

    # --- every paddock write is guarded ---
    # Walk each DB.put('paddocks' site and demand a limit check in the 12 lines
    # above it. Counting call sites would pass the day someone adds a third.
    lines = app.splitlines()
    writes = [i for i, l in enumerate(lines) if "DB.put('paddocks'" in l]
    check("at least one paddock write exists", len(writes) > 0, f"{len(writes)} sites")
    unguarded = [i + 1 for i in writes
                 if "paddockLimitReached()" not in "\n".join(lines[max(0, i - 12):i])]
    check("EVERY paddock write is gated", not unguarded,
          f"ungated at line(s) {unguarded}" if unguarded else f"{len(writes)}/{len(writes)} gated")

    # --- the pdf export is gated at the function, not only in the markup ---
    gen = app.split("async function generateReport()", 1)
    check("generateReport re-checks the licence",
          len(gen) == 2 and "canExportPdf" in gen[1][:400],
          "hiding the button is UI state, not a gate")

    # --- load order: app.js reads License at render time ---
    check("license.js loads before app.js",
          index.find("js/license.js") != -1
          and index.find("js/license.js") < index.find("js/app.js"))

    # --- the service worker cannot serve the pre-gate app forever ---
    check("sw.js caches license.js", "./js/license.js" in sw)
    m = re.search(r"field-log-v(\d+)", sw)
    check("sw.js cache name bumped past v1", m and int(m.group(1)) >= 2,
          f"CACHE_NAME=field-log-v{m.group(1)}" if m else "no cache name found")

    # --- no secret shipped to the browser ---
    lic = (HERE / "js" / "license.js").read_text(encoding="utf-8")
    check("no gumroad token in client js",
          "gumroad_token" not in lic and not re.search(r"Bearer\s+\w", lic))
    m = re.search(r"UNLOCK_SHA256\s*=\s*'([0-9a-f]{64})'", lic)
    check("unlock code is stored hashed, not in plaintext", m is not None)
    # A 64-hex-char literal is not evidence of anything -- it matches the hash of
    # a string nobody has. The ONLY check that catches a broken unlock path is
    # hashing the real plaintext and comparing. The plaintext lives outside this
    # repo on purpose (non-buyers must not have it), so if it is absent the
    # verdict is WITHHELD, never quietly passed.
    if m and _PLAINTEXT_FILE.exists():
        want = re.search(r"`([A-Z0-9-]{8,})`", _PLAINTEXT_FILE.read_text(encoding="utf-8"))
        got = hashlib.sha256(want.group(1).encode()).hexdigest() if want else None
        check("shipped hash IS the hash of the real unlock code", got == m.group(1),
              "a buyer's code would be rejected" if got != m.group(1) else "end-to-end")
    else:
        check("unlock plaintext on file to verify against", False,
              f"WITHHELD -- no plaintext at {_PLAINTEXT_FILE.name}, cannot prove buyers can unlock")

    # --- repo carries no local editor/agent config ---
    check(".gitignore carries .claude/", ".claude/" in
          (HERE / ".gitignore").read_text(encoding="utf-8"))
    tracked = subprocess.run(["git", "ls-files"], cwd=HERE, capture_output=True, text=True).stdout
    check("no .claude file tracked", ".claude/" not in tracked)
    check("no .secrets file tracked", ".secrets" not in tracked)

    # --- content pages ---
    for slug in ("grazing-records", "organic-certification-paperwork",
                 "organic-certification-recordkeeping", "stocking-rate-calculator"):
        p = HERE / slug / "index.html"
        check(f"page built: {slug}", p.exists() and p.stat().st_size > 2000)

    # --- stocking-rate calculator: the AUE table and the sourced formula ---
    calc = (HERE / "stocking-rate-calculator" / "index.html").read_text(encoding="utf-8")
    check("calculator cites its AUM/AUE source",
          "wyoextension.org/publications/html/B1320" in calc)
    check("calculator ships real inputs, not just prose",
          'id="c-run"' in calc and 'id="c-acres"' in calc and 'id="c-species"' in calc)
    check("calculator AUE table lists all 8 sourced animal types",
          calc.count('<td>') >= 8 * 2)
    check("calculator names the honest gap (forage number is the operator's, not ours)",
          "cannot see your land" in calc)
    # --- the compliance page quotes the regulation COMPLETELY ---
    # The page is headed "word for word". An omitted requirement is invisible to
    # a reader and to a cross-check, because a cross-check tests what you SAID,
    # never what you left out. So the count and each item are asserted here.
    paper = (HERE / "organic-certification-paperwork" / "index.html").read_text(encoding="utf-8")
    items = re.findall(r"<li>(.*?)</li>", paper, re.S)
    check("all 5 of 7 CFR 205.103(b) are quoted", len(items) == 5, f"{len(items)} items rendered")
    for frag in ("adapted to the particular business",
                 "traceable back to the last certified operation",
                 "Include audit trail documentation",
                 "not less than 5 years",
                 "demonstrate compliance with the Act"):
        check(f"205.103(b) fragment present: {frag[:38]}", frag in paper)
    check("page does not promise the wrong count", "four things" not in paper.lower()
          and "four sentences" not in paper.lower())

    check("sitemap lists 5 urls",
          (HERE / "sitemap.xml").read_text(encoding="utf-8").count("<loc>") == 5)

    # --- programmatic-seo gate (BLOCK if the gate file is missing) ---
    gate = TOOLS / "pseo_gate.py"
    if not gate.exists():
        check("pseo_gate.py present", False, f"missing at {gate}")
    else:
        g = subprocess.run([sys.executable, str(gate), str(HERE)],
                           capture_output=True, text=True)
        check("pseo_gate PASS/WARN", "VERDICT: PASS" in g.stdout or "VERDICT: WARN" in g.stdout,
              next((l.strip() for l in g.stdout.splitlines() if "VERDICT" in l), "no verdict line"))


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "regen-farm-log-verify"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return None, str(e)


def live():
    print("\n--- live (public surface) ---")
    # THE CONTROL FIRST. If a URL that must not exist returns 200, this host is
    # answering everything and no 200 below means anything.
    ctrl, _ = fetch(f"{BASE}/zqxwvj-plarn-frotz-mibblenock/")
    if not check("404 control returns 404", ctrl == 404, f"got {ctrl}"):
        print("\nWITHHELD: the control did not 404, so live 200s prove nothing.")
        return

    status, body = fetch(f"{BASE}/")
    check("app / returns 200", status == 200, f"got {status}")
    check("live app ships the licence gate", "js/license.js" in body)
    check("live app shows the Unlock tab", 'data-view="unlock"' in body)

    s, b = fetch(f"{BASE}/js/license.js")
    check("license.js served", s == 200 and "canAddPaddock" in b, f"got {s}")

    for slug in ("grazing-records", "organic-certification-paperwork",
                 "organic-certification-recordkeeping", "stocking-rate-calculator"):
        s, b = fetch(f"{BASE}/{slug}/")
        check(f"live {slug} 200 + gumroad link",
              s == 200 and "gumroad.com/l/regenfieldlog" in b, f"got {s}")

    s, b = fetch(f"{BASE}/sitemap.xml")
    check("sitemap served", s == 200 and b.count("<loc>") == 5, f"got {s}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true")
    a = ap.parse_args()
    offline()
    if a.live:
        live()
    bad = [n for n, ok, _ in results if not ok]
    print(f"\n{'VERIFY PASS' if not bad else 'VERIFY FAIL'} -- "
          f"{len(results) - len(bad)}/{len(results)} checks passed")
    if bad:
        for n in bad:
            print(f"  FAILED: {n}")
    sys.exit(0 if not bad else 1)


if __name__ == "__main__":
    main()
