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

    -- added 2026-09-24 (cloud research run #59), a DIFFERENT word family
    -- (calculator, not tracker/log) that the app's own 09-19 dead-vocabulary
    -- sweep never tested. Same reader, same dual controls:
    stocking rate calculator             depth 10, incl. nz/ireland/australia/
                                         uk geo variants                       SHIP
    cattle per acre calculator           depth 8                               SHIP
    how many cows per acre calculator    depth 5                               SHIP
    xqzplonkfrobnitz nonsensewordzz      0  (junk control, same run)
    planting zone 6                      depth 10 (known-live control, same run)

    -- added 2026-09-25 (cloud research run #60), gated 09-24 (run #59) as
    -- "how many bales of hay for winter", built the next run per the
    -- established pattern (a gated idea sitting unbuilt against a live sale
    -- clock is applying finished work, not producing more of it). Same
    -- reader, same dual controls, re-run fresh rather than trusted stale:
    how many bales of hay per cow per winter  depth 10, incl. texas/alberta/
                                         canada/missouri geo variants + round
                                         vs. square bale sub-intent            SHIP
    how much hay do I need per cow       depth 10, incl. per-day/per-year/
                                         per-month variants                    SHIP
    hay calculator                       depth 10, incl. "for cows/horses/
                                         goats/sheep" and "by weight" variants SHIP
    round bales per cow winter           depth 6                              SHIP
    how many round bales for one cow     depth 10                             SHIP
    zqxwvj plarn frotz mibblenock        0  (junk control, same run)
    Winnability checked before building (the 09-24 lesson): page 1 for
    "how many bales of hay per cow winter calculator" has real competitors
    (FarmingWork.com's Cattle Feed Calculator, ranchr.com) but content
    (Hobby Farms, extension pages) still dominates over dedicated tools --
    contested, not a blue ocean, not saturated by one institutional free
    tool either. Same room shape as the stocking-rate calculator above.

    -- added 2026-09-27 (cloud research run #61), gated 09-25 (run #60) as
    -- "creep-feeding profitability calculator", re-probed fresh rather than
    -- trusted stale per this file's own falsifiability discipline (the
    -- instrument's own --selftest run clean first, positive/negative both
    -- correct in the same session):
    creep feed calculator                depth 6, incl. "for cattle/horses"
                                         sub-intent                          SHIP
    how much creep feed per calf         depth 4                             SHIP
    creep feeding cost calculator        depth 0                             DROPPED (bare
                                         phrase, no exact-match autocomplete)
    creep feed cost per pound of gain    depth 0                             DROPPED
    zqxwvj plarn frotz mibblenock        0  (junk control, same run)
    Winnability checked BEFORE building (the 09-24/09-25 lesson, applied a
    3rd time): WebSearch on "creep feed calculator cost per pound of gain"
    -- page 1 is entirely university extension content (UGA, Alabama, Ohio
    State, Penn State, Oklahoma State, SDSU, Cattlytics) and zero dedicated
    calculator tools -- more open than either calculator already shipped.

HONEST LIMIT: autocomplete measures query SHAPE, never volume -- the same
harvest inverts under a different country code. Page-1 competition is NOT
checked here and remains an open question.

FACTS: the 7 CFR 205.103 wording below is quoted from the regulation text at
govinfo (CFR-2024-title7-vol3-sec205-103). An earlier attempt to verify it
against ecfr.gov returned a bot wall ("your request has been flagged as
potentially automated") which reads exactly like an empty source and produced a
false mismatch. Never quote a regulation from a page that did not actually
fetch.

The stocking-rate calculator's numbers (AU = 1,000 lb cow+calf, AUM = 750 lb
air-dry forage, daily intake = 2.5% of body weight, the Animal Unit Equivalent
table, and "take half - leave half" = 50% utilization) are quoted from
University of Wyoming Extension Bulletin B-1320, "Animal Unit Month (AUM)
Concepts and Applications for Grazing Rangelands"
(https://wyoextension.org/publications/html/B1320/), fetched live 2026-09-24.
This tool does the arithmetic only -- it has no idea what a given acre of
land actually produces. That number has to come from the operator's own NRCS
Ecological Site Description or county extension office; a wrong forage input
gives a confidently wrong answer no matter how correct the math is.

The winter-hay calculator's intake rate (2.6% of body weight in dry matter
per day, consistent across both the 1,000 lb and 1,400 lb examples given) is
quoted from Oklahoma State University Extension's Cow-Calf Corner (Mark Z.
Johnson, Beef Cattle Breeding Specialist), as republished at
https://www.nationalbeefwire.com/cow-calf-corner-estimating-winter-hay-needs,
fetched live 2026-09-25 (the OSU site itself returned no usable content to
the fetch). Bale-weight variance (a 4x5 round bale runs ~700-940 lb by
packing density alone) is quoted from Penn State Extension,
https://extension.psu.edu/how-much-does-that-bale-really-weigh-feeding-and-fertilizer-implications,
fetched live 2026-09-25 -- confirmed via a second, independent fetch attempt
that failed (extension.okstate.edu returned HTTP 403) before this one
succeeded, so the number is not from the first source tried. Feeder-waste
percentages are quoted from University of Nebraska-Lincoln's writeup of an
OSU study (Lalman et al.) and a Michigan State study, plus University of
Missouri Extension publication G4570 for the unrolled-on-the-ground figure
(the UNL/OSU/MSU source explicitly does not cover that method), all fetched
live 2026-09-25 -- see WASTE_TABLE below; the two OSU/MSU studies disagree on
ring-feeder waste (4.5% vs up to 21%) and both numbers are shown, not
averaged into a made-up middle figure. Bale weight and feeding days are the
operator's own numbers to supply, same discipline as the forage number above.

The creep-feed calculator's feed-conversion-by-forage-quality table (4.4:1 on
high-quality forage, 8.4:1 on moderate, 12.5:1 on low) and its value-of-gain
worked example (a 530 lb calf at $1.80/lb vs a 580 lb calf at $1.70/lb, quoted
verbatim including the source's own $950/$986/$36/$0.72 figures -- 530x1.80
actually equals $954, a small rounding in the source's own text, not fixed
here per the CFR-bullets discipline of quoting word for word rather than
correcting a source) are quoted from South Dakota State University Extension,
https://extension.sdstate.edu/considering-creep-feeding, fetched live
2026-09-27. A second source, Ohio State University Extension's BEEF Cattle
Letter (https://u.osu.edu/beef/2000/05/10/is-creep-feed-cost-effective/,
fetched live 2026-09-27), gives a flat 8-to-1 conversion for a creep-fed calf
against 4-to-1 for a weaned-only calf -- a different framing (whole-system
comparison, not by forage quality) shown as a second, disagreeing data point
rather than blended into the SDSU table, same discipline as the winter-hay
calculator's ring-feeder waste range above. This tool does the arithmetic
only -- feed cost per ton, expected sale prices at two weights, and which
forage-quality band your pasture is are the operator's own numbers; a wrong
one gives a confidently wrong profit/loss verdict no matter how correct the
math is.

-- added 2026-09-28 (cloud research run #62). Two candidates in the same
-- calculator word family, same reader, same dual controls, re-run fresh:
rotational grazing calculator        depth 6 (sheep/cattle-per-acre
                                     sub-intent)                            KILLED on winnability
                                     -- WebSearch page 1: Arkansas Extension
                                     PLUS 4 dedicated calculator sites
                                     (FarmCalcs, Farm Planner Online,
                                     AgentCalc, growandstore/
                                     completecalculators) -- saturated,
                                     same shape as the 09-24 cover-crop and
                                     09-25 livestock-water kills.
manure application rate calculator   depth 5 (fertiliser/slurry/liquid
                                     manure sub-intent)                     SHIP
zqxwvj plarn frotz mibblenock        0  (junk control, same run)
Winnability checked before building: WebSearch page 1 for "manure
application rate calculator per acre" is worksheets/PDFs from 5 university
extensions (Oklahoma State, Minnesota, Michigan State, Nebraska-Lincoln,
Missouri/erams) plus ONE generic calculator-farm site (calculatorultra.com)
-- contested by content, not saturated by an institutional free tool, same
room shape as the stocking-rate and winter-hay calculators that shipped.

The manure application calculator's load-area method (spreader load size
divided by the ground area it covered, area = length x width / 43,560) is
quoted from Penn State Extension, "Manure Spreader Calibration"
(https://extension.psu.edu/manure-spreader-calibration, fetched live
2026-09-28). Its tarp/sheet cross-check method and the 21.8 lb-per-sq-ft to
tons-per-acre conversion factor (43,560 sq ft/acre divided by 2,000 lb/ton)
are quoted from North Dakota State University Extension, "Manure Spreader
Calibration For Nutrient Management Planning"
(https://www.ndsu.edu/agriculture/extension/publications/manure-spreader-calibration-nutrient-management-planning,
fetched live 2026-09-28) -- two independent sources for the two methods
shown, not one source stretched to cover both. Load size, travel-path
measurements and field size are the operator's own numbers to supply, same
discipline as every calculator on this site.

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
    "sufficient detail as to be readily understood and audited; records must span the "
    "time of purchase or acquisition, through production, to sale or transport and be "
    "traceable back to the last certified operation;",
    "Include audit trail documentation for agricultural products handled or produced by "
    "the certified operation and identify agricultural products on these records as "
    "“100% organic,” “organic,” or “made with organic (specified "
    "ingredients or food group(s)),” or similar terms, as applicable;",
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
        "desc": "The five things 7 CFR 205.103 requires of your records, quoted in "
                "full, plus what each one means for a small farm keeping records by hand.",
        "h1": "Organic Certification Paperwork",
        "lede": "People picture a mountain of forms. The recordkeeping rule itself is "
                "five short requirements. It is worth reading them once, because they "
                "ask for less than most farms think, and something different.",
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
            ("The audit trail is the one people skip",
             "Item 3 is the requirement most often missed, and the one an inspector is "
             "most likely to ask about. It is not enough that you wrote things down. "
             "The records have to let someone follow a product backwards, from the sale "
             "all the way to the last certified operation it came from. That is what "
             "\"audit trail\" means here, and it is why item 2 says your records must "
             "span purchase, production and sale rather than just the day's work."),
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
    {
        "slug": "stocking-rate-calculator",
        "title": "Stocking Rate Calculator: How Many Cows, Sheep, Goats or Horses Per Acre",
        "desc": "Free stocking rate / AUM calculator. Enter your acres and a forage "
                "estimate, pick your animal, get animal units, AUM/acre, and the "
                "head count your pasture can carry. Sourced, not guessed.",
        "h1": "Stocking Rate Calculator",
        "lede": "How many animals a pasture can carry is one calculation, not a "
                "guess: acres, how much forage they grow, how much of that you're "
                "willing to take, and how much one animal eats. This does the math; "
                "you supply the one number only your land can give you.",
        "calc": True,
        "body": [
            ("What \"stocking rate\" means",
             "Stocking rate is usually written as AUM per acre, or its flip side, "
             "acres per AUM. An AUM (Animal Unit Month) is the forage a 1,000-pound "
             "cow and her unweaned calf eat in a month: 750 pounds of air-dry "
             "forage, built from cattle eating about 2.5% of their body weight a "
             "day. Every other animal is converted to a fraction of that one "
             "reference animal, called its Animal Unit Equivalent (AUE)."),
        ],
        "body_after_calc": [
            ("Animal Unit Equivalents, by species",
             "AUE_TABLE"),
            ("Where the forage number has to come from",
             "The calculator cannot see your land. \"Forage produced per acre\" "
             "swings by 10x or more between arid rangeland and irrigated pasture, "
             "and by season on the same field. The real number for your acres "
             "lives in your county NRCS office's Ecological Site Description, or "
             "a clip-and-weigh sample you take yourself, not a table on "
             "this page. Put in a guess and you get a confident, wrong answer; "
             "put in a real number and the arithmetic above is the same math a "
             "range extension agent would do by hand."),
            ("Why \"take half, leave half\" is the default",
             "The 50% utilization rate is not caution for its own sake. Grazing "
             "past half the standing forage slows the plant's own regrowth, so a "
             "field pushed past that line this year carries less next year. It is "
             "the standard-guideline number, not a hard law: rotational, "
             "short-duration systems can responsibly run higher; season-long "
             "continuous grazing usually needs to run lower."),
            ("If you're feeding hay instead of grazing",
             "STOCKING_TO_HAY_LINK"),
        ],
    },
    {
        "slug": "winter-hay-calculator",
        "title": "Winter Hay Calculator: How Many Bales Per Cow For Winter",
        "desc": "Free winter hay calculator. Enter cow weight, head count and "
                "feeding days, pick a feeder type, get pounds of dry matter, "
                "total hay to buy, and bales needed. Sourced, not guessed.",
        "h1": "Winter Hay Calculator",
        "lede": "How much hay one winter takes is arithmetic, not a guess: how "
                "much a cow eats, how many days you'll feed hay, and how much "
                "your feeder wastes. This does the math; you supply the one "
                "number only your own bales can give you.",
        "calc": "hay",
        "body": [
            ("How much hay one cow actually eats",
             "A cow eats about 2.6% of her body weight in hay dry matter a "
             "day. A 1,000 lb cow eats roughly 26 lb of dry matter a day; a "
             "1,400 lb cow eats roughly 36.4 lb a day, the same "
             "percentage, a bigger cow. That is the whole rule the "
             "calculator below runs on; multiply it by your head count and "
             "your feeding days and you have the herd's real dry-matter "
             "need for the winter. Source: Oklahoma State University "
             "Extension's Cow-Calf Corner (Mark Z. Johnson), "
             "https://www.nationalbeefwire.com/cow-calf-corner-estimating-winter-hay-needs, "
             "fetched 2026-09-25."),
        ],
        "body_after_calc": [
            ("Why bale weight is the number you have to supply",
             "A \"round bale\" is not one weight. A 4-foot by 5-foot round "
             "bale runs from about 700 lb loose to about 940 lb very "
             "tight, purely from how hard it was packed, and bigger "
             "5-foot or 6-foot bales common on many farms run 1,000 to "
             "1,500 lb and up. There is no honest default here: weigh a "
             "bale on a scale, or ask whoever baled or sold it, and put "
             "that real number in above. A guessed bale weight makes every "
             "other number on this page confidently wrong."),
            ("Feeder waste, by feeder type",
             "WASTE_TABLE"),
            ("If you're grazing part of the year too",
             "HAY_TO_STOCKING_LINK"),
        ],
    },
    {
        "slug": "creep-feed-calculator",
        "title": "Creep Feed Calculator: Is Creep Feeding Your Calves Profitable",
        "desc": "Free creep feed calculator. Enter your feed cost, forage "
                "quality, and expected weights/prices, get cost of gain vs "
                "value of gain and a straight profit or loss verdict. "
                "Sourced, not guessed.",
        "h1": "Creep Feed Calculator",
        "lede": "Creep feeding only pays when the value of the extra weight "
                "beats what it cost to put on. This does that math; you "
                "supply the two numbers only your feed bill and your buyer "
                "can give you.",
        "calc": "creep",
        "body": [
            ("The one question creep feeding actually answers",
             "Creep feeding calves extra grain while they're still nursing "
             "puts on weight before weaning. Whether that's worth doing "
             "comes down to one comparison: does the value of the extra "
             "pounds beat what the feed to grow them cost? Everything below "
             "is that one comparison, done with your numbers instead of a "
             "guess."),
        ],
        "body_after_calc": [
            ("Feed conversion, by forage quality",
             "CONVERSION_TABLE"),
            ("Why your sale price per pound isn't the same at both weights",
             "Heavier calves usually sell for a lower price per pound than "
             "lighter ones -- so the value of the extra weight is smaller "
             "than it looks at first. South Dakota State University "
             "Extension gives a worked example: “if a 530 lb. calf "
             "sells for $1.80/lb. and a 580 lb. calf sells for $1.70/lb. "
             "the value of the additional gain is actually less than the "
             "price received per pound. In that, since the 530 lb. calf "
             "sold for $950 and the 580 lb. calf sold for $986 the "
             "difference is $36/head, which when divided by a weight "
             "difference of 50 lb. arrives at a value of $0.72/lb. for "
             "each additional pound of gain.” The calculator above does "
             "that same division on your own two weights and prices."),
            ("The decision rule",
             "South Dakota State University Extension states it plainly: "
             "creep feed should only be offered when the value of gain is "
             "greater than the cost of gain. A second source, Ohio State "
             "University Extension's BEEF Cattle Letter, works the cost "
             "side with a flatter 8-to-1 feed conversion (against roughly "
             "4-to-1 for a weaned-only calf) -- a different framing, not "
             "blended into the table above, shown so the two studies' "
             "numbers stay visible instead of averaged into one made-up "
             "figure."),
            ("The honest gap: your feed cost and your buyer's price are "
             "yours to supply",
             "The calculator cannot see your feed bill or your local market. "
             "Feed cost per ton, the forage-quality band your pasture "
             "actually is, and the two sale prices are real numbers only "
             "you or your buyer can give -- weigh, price-check, and don't "
             "guess, same discipline as the bale weight above."),
            ("More farm-math tools",
             "CALC_CROSS_LINKS"),
        ],
    },
    {
        "slug": "manure-application-calculator",
        "title": "Manure Application Rate Calculator: Tons or Gallons Per Acre",
        "desc": "Free manure application rate calculator. Enter your spreader "
                "load and the ground it covered, get tons or gallons per acre, "
                "loads needed, and total manure for the field. Sourced, not guessed.",
        "h1": "Manure Application Rate Calculator",
        "lede": "How much manure your spreader is putting down per acre is "
                "arithmetic, not a guess: how big the load was and how much "
                "ground it covered. This does the math; you supply the one "
                "number only a tape measure or your spreader's own capacity "
                "can give you.",
        "calc": "manure",
        "body": [
            ("What \"application rate\" means",
             "Application rate is the load divided by the area it covered: "
             "tons per acre for solid manure, gallons per acre for liquid. "
             "Area is travel-path length times spread width, converted from "
             "square feet to acres by dividing by 43,560. Get the rate wrong "
             "and you either waste nutrients and risk runoff on the high "
             "side, or waste the trip on the low side."),
        ],
        "body_after_calc": [
            ("Check it the other way: the tarp method",
             "MANURE_TARP_METHOD"),
            ("The honest gap: this can't see your load or your path",
             "The calculator cannot see how full the spreader really was or "
             "how straight you drove. Weigh a load if you can instead of "
             "trusting the rated capacity, and measure your actual spread "
             "width rather than guessing it -- a wrong load size or path "
             "width gives a confidently wrong rate no matter how correct the "
             "arithmetic is."),
            ("More farm-math tools",
             "MANURE_CROSS_LINKS"),
        ],
    },
]

# Animal Unit Equivalents, University of Wyoming Extension B-1320, Table 1
# (fetched live 2026-09-24). Values are AUE -- a fraction/multiple of one
# 1,000 lb cow-with-calf.
AUE_TABLE = [
    ("Cow (1,000 lb) with calf", 1.00),
    ("Bull, mature", 1.35),
    ("Cattle, 1 year old", 0.60),
    ("Cattle, 2 years old", 0.80),
    ("Horse, mature", 1.25),
    ("Sheep, mature", 0.20),
    ("Lamb, 1 year old", 0.15),
    ("Goat, mature", 0.15),
]

# Hay feeder waste by design, fetched live 2026-09-25 from University of
# Nebraska-Lincoln's writeup (newsroom.unl.edu/announce/beef/2528/14323) of an
# Oklahoma State University study (Dr. Dave Lalman et al.) and a Michigan
# State University feeder-comparison study. Two independent studies gave
# different numbers for the same feeder category (a real disagreement, not a
# reading error) -- shown as the range both studies actually reported, never
# collapsed to a single invented number.
# Feed conversion by forage quality, South Dakota State University Extension
# (extension.sdstate.edu/considering-creep-feeding), fetched live 2026-09-27:
# lb of creep feed per lb of added gain, on high/moderate/low quality forage.
CONVERSION_TABLE = [
    ("High-quality forage (lush pasture)", "4.4 : 1"),
    ("Moderate-quality forage", "8.4 : 1"),
    ("Low-quality forage (dry, dormant)", "12.5 : 1"),
]

WASTE_TABLE = [
    ("Cone / sheeted-bottom feeder", "5–6%", "OSU (Lalman et al.)"),
    ("Ring or ring-cone feeder", "4.5–21%", "MSU / OSU, two studies disagree"),
    ("Trailer feeder", "11.4%", "MSU"),
    ("Cradle feeder", "14.6%", "MSU"),
    ("Open-bottom feeder / no containment", "up to 21%", "OSU"),
    ("Unrolled on the ground, no rack", "up to 40%", "Univ. of Missouri Extension G4570"),
]

CALC_HTML = """
<div class="calcbox">
  <div class="calc-row">
    <label>Pasture size (acres)<input type="number" id="c-acres" min="0.1" step="any" value="40"></label>
    <label>Forage produced (lb/acre for the grazing period)<input type="number" id="c-forage" min="1" step="any" value="2000"></label>
  </div>
  <div class="calc-row">
    <label>Utilization rate
      <select id="c-util">
        <option value="0.25">25% (conservative / arid rangeland)</option>
        <option value="0.5" selected>50% ("take half, leave half", standard)</option>
        <option value="0.6">60% (intensive rotational grazing)</option>
      </select>
    </label>
    <label>Animal
      <select id="c-species">
        <option value="1.00" selected>Cow (1,000 lb) with calf</option>
        <option value="1.35">Bull, mature</option>
        <option value="0.60">Cattle, 1 year old</option>
        <option value="0.80">Cattle, 2 years old</option>
        <option value="1.25">Horse, mature</option>
        <option value="0.20">Sheep, mature</option>
        <option value="0.15">Lamb, 1 year old</option>
        <option value="0.15">Goat, mature</option>
      </select>
    </label>
  </div>
  <div class="calc-row">
    <label>Head count<input type="number" id="c-head" min="1" step="1" value="20"></label>
    <label>Grazing period (days)<input type="number" id="c-days" min="1" step="1" value="90"></label>
  </div>
  <button type="button" id="c-run" class="btn" style="margin-top:4px;">Calculate</button>
  <div id="c-out" class="calc-out" aria-live="polite"></div>
</div>
<script>
(function(){
  var $=function(id){return document.getElementById(id);};
  function fmt(n){return Math.round(n*100)/100;}
  function run(){
    var acres=parseFloat($('c-acres').value)||0;
    var forage=parseFloat($('c-forage').value)||0;
    var util=parseFloat($('c-util').value)||0.5;
    var aue=parseFloat($('c-species').value)||1;
    var head=parseFloat($('c-head').value)||0;
    var days=parseFloat($('c-days').value)||0;
    var out=$('c-out');
    if(acres<=0||forage<=0||head<=0||days<=0){
      out.innerHTML='<p class="warn">Enter a value greater than zero in every field.</p>';
      return;
    }
    var usableLbs=acres*forage*util;
    var aumsAvailable=usableLbs/750;
    var aumsNeeded=head*aue*(days/30.4);
    var ratePerAcre=aumsAvailable/acres;
    var maxHead=Math.floor(aumsAvailable/(aue*(days/30.4)));
    var maxDays=Math.floor((aumsAvailable/(aue*head))*30.4);
    var pct=fmt((aumsNeeded/aumsAvailable)*100);
    var verdict = aumsNeeded<=aumsAvailable
      ? '<p class="ok"><strong>Within capacity.</strong> This herd for this period uses '+pct+'% of the AUMs your entered acreage/forage/utilization make available.</p>'
      : '<p class="warn"><strong>Over capacity.</strong> This herd for this period needs '+pct+'% of the AUMs available, more than the pasture provides at this utilization rate.</p>';
    out.innerHTML =
      verdict +
      '<table class="calc-table"><tbody>'+
      '<tr><td>Stocking rate</td><td>'+fmt(ratePerAcre)+' AUM/acre  ('+fmt(1/ratePerAcre)+' acres/AUM)</td></tr>'+
      '<tr><td>Total AUMs available</td><td>'+fmt(aumsAvailable)+' AUM</td></tr>'+
      '<tr><td>AUMs this herd needs</td><td>'+fmt(aumsNeeded)+' AUM for '+days+' days</td></tr>'+
      '<tr><td>Max head for '+days+' days</td><td>'+(maxHead>0?maxHead:0)+' head</td></tr>'+
      '<tr><td>Max days for '+head+' head</td><td>'+(maxDays>0?maxDays:0)+' days</td></tr>'+
      '</tbody></table>'+
      '<p class="src">AU/AUM/AUE definitions: University of Wyoming Extension B-1320. '+
      'Your forage-per-acre number is yours to supply, see below.</p>';
  }
  $('c-run').addEventListener('click', run);
  run();
})();
</script>
"""

HAY_CALC_HTML = """
<div class="calcbox">
  <div class="calc-row">
    <label>Average cow weight (lb)<input type="number" id="h-weight" min="1" step="any" value="1200"></label>
    <label>Head count<input type="number" id="h-head" min="1" step="1" value="20"></label>
  </div>
  <div class="calc-row">
    <label>Days you'll feed hay<input type="number" id="h-days" min="1" step="1" value="150"></label>
    <label>Feeder / waste type
      <select id="h-waste">
        <option value="0.05">Cone / sheeted-bottom feeder (~5%)</option>
        <option value="0.15" selected>Ring feeder (~15%, studies vary 4.5-21%)</option>
        <option value="0.21">Open-bottom feeder, no containment (~21%)</option>
        <option value="0.40">Unrolled on the ground, no rack (up to 40%)</option>
      </select>
    </label>
  </div>
  <div class="calc-row">
    <label>Your bale weight (lb), weigh it, don't guess<input type="number" id="h-bale" min="1" step="any" value="1250"></label>
  </div>
  <button type="button" id="h-run" class="btn" style="margin-top:4px;">Calculate</button>
  <div id="h-out" class="calc-out" aria-live="polite"></div>
</div>
<script>
(function(){
  var $=function(id){return document.getElementById(id);};
  function fmt(n){return Math.round(n*100)/100;}
  function run(){
    var weight=parseFloat($('h-weight').value)||0;
    var head=parseFloat($('h-head').value)||0;
    var days=parseFloat($('h-days').value)||0;
    var waste=parseFloat($('h-waste').value)||0.15;
    var bale=parseFloat($('h-bale').value)||0;
    var out=$('h-out');
    if(weight<=0||head<=0||days<=0||bale<=0){
      out.innerHTML='<p class="warn">Enter a value greater than zero in every field.</p>';
      return;
    }
    var dailyDmPerHead=weight*0.026;
    var totalDm=dailyDmPerHead*head*days;
    var totalFedOut=totalDm/(1-waste);
    var totalTons=totalFedOut/2000;
    var bales=Math.ceil(totalFedOut/bale);
    var balesPerHead=fmt(bales/head);
    out.innerHTML =
      '<p class="ok"><strong>'+bales+' bales</strong> at '+bale+' lb each covers '+head+' head for '+days+' days, at ~'+Math.round(waste*100)+'% feeder waste.</p>'+
      '<table class="calc-table"><tbody>'+
      '<tr><td>Dry matter per head per day</td><td>'+fmt(dailyDmPerHead)+' lb</td></tr>'+
      '<tr><td>Total dry matter needed</td><td>'+fmt(totalDm)+' lb for '+days+' days</td></tr>'+
      '<tr><td>Hay to feed out (after waste)</td><td>'+fmt(totalFedOut)+' lb ('+fmt(totalTons)+' tons)</td></tr>'+
      '<tr><td>Bales needed</td><td>'+bales+' bales at '+bale+' lb</td></tr>'+
      '<tr><td>Bales per head</td><td>'+balesPerHead+'</td></tr>'+
      '</tbody></table>'+
      '<p class="src">Intake rate: Oklahoma State University Extension (Cow-Calf Corner), '+
      'https://www.nationalbeefwire.com/cow-calf-corner-estimating-winter-hay-needs. '+
      'Your bale weight and feeding days are yours to supply, see below.</p>';
  }
  $('h-run').addEventListener('click', run);
  run();
})();
</script>
"""

CREEP_CALC_HTML = """
<div class="calcbox">
  <div class="calc-row">
    <label>Feed cost ($/ton)<input type="number" id="k-feedcost" min="1" step="any" value="350"></label>
    <label>Forage quality
      <select id="k-quality">
        <option value="4.4">High-quality forage (lush pasture)</option>
        <option value="8.4" selected>Moderate-quality forage</option>
        <option value="12.5">Low-quality forage (dry, dormant)</option>
      </select>
    </label>
  </div>
  <div class="calc-row">
    <label>Base (weaning) weight (lb)<input type="number" id="k-baseweight" min="1" step="any" value="500"></label>
    <label>Sale price at base weight ($/lb)<input type="number" id="k-baseprice" min="0.01" step="any" value="1.80"></label>
  </div>
  <div class="calc-row">
    <label>Expected added gain from creep feeding (lb)<input type="number" id="k-gain" min="1" step="any" value="50"></label>
    <label>Sale price at the heavier weight ($/lb)<input type="number" id="k-heavyprice" min="0.01" step="any" value="1.70"></label>
  </div>
  <button type="button" id="k-run" class="btn" style="margin-top:4px;">Calculate</button>
  <div id="k-out" class="calc-out" aria-live="polite"></div>
</div>
<script>
(function(){
  var $=function(id){return document.getElementById(id);};
  function fmt(n){return Math.round(n*100)/100;}
  function run(){
    var feedcost=parseFloat($('k-feedcost').value)||0;
    var conv=parseFloat($('k-quality').value)||8.4;
    var baseweight=parseFloat($('k-baseweight').value)||0;
    var baseprice=parseFloat($('k-baseprice').value)||0;
    var gain=parseFloat($('k-gain').value)||0;
    var heavyprice=parseFloat($('k-heavyprice').value)||0;
    var out=$('k-out');
    if(feedcost<=0||baseweight<=0||baseprice<=0||gain<=0||heavyprice<=0){
      out.innerHTML='<p class="warn">Enter a value greater than zero in every field.</p>';
      return;
    }
    var feedCostPerLb=feedcost/2000;
    var costOfGainPerLb=feedCostPerLb*conv;
    var totalFeedCost=costOfGainPerLb*gain;
    var heavyweight=baseweight+gain;
    var baseRevenue=baseweight*baseprice;
    var heavyRevenue=heavyweight*heavyprice;
    var valueOfGainTotal=heavyRevenue-baseRevenue;
    var valueOfGainPerLb=valueOfGainTotal/gain;
    var netProfit=valueOfGainTotal-totalFeedCost;
    var verdict = netProfit>0
      ? '<p class="ok"><strong>Profitable.</strong> Value of gain ($'+fmt(valueOfGainPerLb)+'/lb) beats cost of gain ($'+fmt(costOfGainPerLb)+'/lb) on these numbers.</p>'
      : '<p class="warn"><strong>Not profitable.</strong> Cost of gain ($'+fmt(costOfGainPerLb)+'/lb) beats value of gain ($'+fmt(valueOfGainPerLb)+'/lb) on these numbers.</p>';
    out.innerHTML =
      verdict +
      '<table class="calc-table"><tbody>'+
      '<tr><td>Feed cost per lb</td><td>$'+fmt(feedCostPerLb)+'/lb</td></tr>'+
      '<tr><td>Cost of gain</td><td>$'+fmt(costOfGainPerLb)+'/lb ('+conv+' : 1 conversion)</td></tr>'+
      '<tr><td>Total feed cost for '+gain+' lb gain</td><td>$'+fmt(totalFeedCost)+'</td></tr>'+
      '<tr><td>Value of gain</td><td>$'+fmt(valueOfGainPerLb)+'/lb</td></tr>'+
      '<tr><td>Total value of the added weight</td><td>$'+fmt(valueOfGainTotal)+'</td></tr>'+
      '<tr><td>Net profit/loss</td><td>$'+fmt(netProfit)+' per head</td></tr>'+
      '</tbody></table>'+
      '<p class="src">Decision rule + forage-quality conversions: South Dakota '+
      'State University Extension, extension.sdstate.edu/considering-creep-feeding. '+
      'Your feed cost, forage quality, weights and prices are yours to supply.</p>';
  }
  $('k-run').addEventListener('click', run);
  run();
})();
</script>
"""

MANURE_CALC_HTML = """
<div class="calcbox">
  <div class="calc-row">
    <label>Manure type
      <select id="m-unit">
        <option value="tons" selected>Solid (tons)</option>
        <option value="gal">Liquid (gallons)</option>
      </select>
    </label>
    <label>Spreader load size<input type="number" id="m-load" min="0.01" step="any" value="6"></label>
  </div>
  <div class="calc-row">
    <label>Travel path length (ft)<input type="number" id="m-length" min="1" step="any" value="2000"></label>
    <label>Spread width (ft)<input type="number" id="m-width" min="1" step="any" value="30"></label>
  </div>
  <div class="calc-row">
    <label>Field size to cover (acres)<input type="number" id="m-field" min="0.01" step="any" value="40"></label>
  </div>
  <button type="button" id="m-run" class="btn" style="margin-top:4px;">Calculate</button>
  <div id="m-out" class="calc-out" aria-live="polite"></div>
</div>
<script>
(function(){
  var $=function(id){return document.getElementById(id);};
  function fmt(n){return Math.round(n*100)/100;}
  function run(){
    var unit=$('m-unit').value;
    var load=parseFloat($('m-load').value)||0;
    var length=parseFloat($('m-length').value)||0;
    var width=parseFloat($('m-width').value)||0;
    var field=parseFloat($('m-field').value)||0;
    var out=$('m-out');
    if(load<=0||length<=0||width<=0||field<=0){
      out.innerHTML='<p class="warn">Enter a value greater than zero in every field.</p>';
      return;
    }
    var label = unit==='tons' ? 'tons' : 'gallons';
    var acresPerLoad=(length*width)/43560;
    var ratePerAcre=load/acresPerLoad;
    var loadsNeeded=Math.ceil(field/acresPerLoad);
    var totalNeeded=loadsNeeded*load;
    out.innerHTML =
      '<p class="ok"><strong>'+fmt(ratePerAcre)+' '+label+'/acre</strong> at this load size and travel path.</p>'+
      '<table class="calc-table"><tbody>'+
      '<tr><td>Area covered per load</td><td>'+fmt(acresPerLoad)+' acres</td></tr>'+
      '<tr><td>Application rate</td><td>'+fmt(ratePerAcre)+' '+label+'/acre</td></tr>'+
      '<tr><td>Loads needed for '+field+' acres</td><td>'+loadsNeeded+' loads</td></tr>'+
      '<tr><td>Total manure for the field</td><td>'+fmt(totalNeeded)+' '+label+'</td></tr>'+
      '</tbody></table>'+
      '<p class="src">Load-area method: Penn State Extension, '+
      'extension.psu.edu/manure-spreader-calibration. '+
      'Your load size and path measurements are yours to supply.</p>';
  }
  $('m-run').addEventListener('click', run);
  run();
})();
</script>
"""

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
  .calcbox {{ background:var(--surface); border:1px solid var(--border);
              border-radius:10px; padding:16px; margin:20px 0; }}
  .calc-row {{ display:flex; gap:14px; flex-wrap:wrap; margin-bottom:10px; }}
  .calc-row label {{ flex:1 1 220px; display:flex; flex-direction:column;
                      font-size:0.85rem; color:var(--dim); gap:4px; }}
  .calc-row input, .calc-row select {{ font-size:1rem; padding:8px;
        border:1px solid var(--border); border-radius:6px;
        background:var(--bg); color:var(--text); }}
  .calc-out {{ margin-top:14px; }}
  .calc-out .ok {{ color:var(--accent); }}
  .calc-out .warn {{ color:#a14a2a; }}
  @media (prefers-color-scheme: dark) {{ .calc-out .warn {{ color:#e0a082; }} }}
  table.calc-table {{ width:100%; border-collapse:collapse; margin-top:6px; }}
  table.calc-table td {{ padding:6px 4px; border-bottom:1px solid var(--border); font-size:0.95rem; }}
  table.calc-table td:first-child {{ color:var(--dim); }}
  table.aue {{ width:100%; border-collapse:collapse; margin:10px 0; }}
  table.aue th, table.aue td {{ text-align:left; padding:6px 8px; border-bottom:1px solid var(--border); }}
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
  <a class="btn alt" href="https://wealthywellness0.gumroad.com/l/regenfieldlog">Unlock every paddock + audit PDF, $29</a>
</div>
<footer>
  Regen Farm Field Log &middot; <a href="{base}/">the app</a>
  <p class="fine"><a href="https://fscholtesdowd.github.io/privacy/">Privacy policy</a> &middot; <a href="https://fscholtesdowd.github.io/terms/">Terms</a></p>
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
    calc = page.get("calc")
    if calc:
        parts.append(CREEP_CALC_HTML if calc == "creep" else
                     HAY_CALC_HTML if calc == "hay" else
                     MANURE_CALC_HTML if calc == "manure" else CALC_HTML)
        for h2, text in page.get("body_after_calc", []):
            parts.append(f"<h2>{html.escape(h2)}</h2>")
            if text == "AUE_TABLE":
                rows = "\n".join(
                    f"  <tr><td>{html.escape(name)}</td><td>{aue:.2f}</td></tr>"
                    for name, aue in AUE_TABLE)
                parts.append('<table class="aue"><thead><tr><th>Animal</th>'
                             f'<th>AUE</th></tr></thead><tbody>\n{rows}\n</tbody></table>'
                             '<p class="src">Source: University of Wyoming Extension B-1320, '
                             '<a href="https://wyoextension.org/publications/html/B1320/">'
                             '"Animal Unit Month (AUM) Concepts and Applications for Grazing '
                             'Rangelands"</a>, fetched 2026-09-24.</p>')
            elif text == "WASTE_TABLE":
                rows = "\n".join(
                    f"  <tr><td>{html.escape(name)}</td><td>{pct}</td><td>{html.escape(src)}</td></tr>"
                    for name, pct, src in WASTE_TABLE)
                parts.append('<table class="aue"><thead><tr><th>Feeder</th>'
                             f'<th>Waste</th><th>Study</th></tr></thead><tbody>\n{rows}\n</tbody></table>'
                             '<p class="src">Sources: University of Nebraska-Lincoln, '
                             '<a href="https://newsroom.unl.edu/announce/beef/2528/14323">'
                             '"Bale Feeder Choice Can Reduce Waste and Save Money"</a>, '
                             'citing Oklahoma State (Lalman et al.) and Michigan State studies; '
                             'and University of Missouri Extension, '
                             '<a href="https://extension.missouri.edu/publications/g4570">'
                             '"Reducing Losses When Feeding Hay to Beef Cattle"</a> (G4570), '
                             'both fetched 2026-09-25. The ring-feeder range is wide because the '
                             'two studies measured different real feeders under that name, not a '
                             'reading error.</p>')
            elif text == "STOCKING_TO_HAY_LINK":
                parts.append('<p>If part of the year is hay instead of pasture, the '
                             f'<a href="{BASE}/winter-hay-calculator/">Winter Hay '
                             'Calculator</a> does the same kind of math for bales per '
                             'head instead of acres per head. Creep feeding calves on '
                             f'this pasture? The <a href="{BASE}/creep-feed-calculator/">'
                             'Creep Feed Calculator</a> works out whether it pays. '
                             f'Spreading manure on it? The <a href="{BASE}/'
                             'manure-application-calculator/">Manure Application Rate '
                             'Calculator</a> works out tons or gallons per acre.</p>')
            elif text == "HAY_TO_STOCKING_LINK":
                parts.append('<p>If part of the year is pasture instead of hay, the '
                             f'<a href="{BASE}/stocking-rate-calculator/">Stocking Rate '
                             'Calculator</a> does the same kind of math for acres per '
                             'head instead of bales per head. Creep feeding calves too? '
                             f'The <a href="{BASE}/creep-feed-calculator/">Creep Feed '
                             'Calculator</a> works out whether it pays. Spreading the '
                             f'manure? The <a href="{BASE}/manure-application-calculator/">'
                             'Manure Application Rate Calculator</a> works out tons or '
                             'gallons per acre.</p>')
            elif text == "CONVERSION_TABLE":
                rows = "\n".join(
                    f"  <tr><td>{html.escape(name)}</td><td>{ratio}</td></tr>"
                    for name, ratio in CONVERSION_TABLE)
                parts.append('<table class="aue"><thead><tr><th>Forage</th>'
                             f'<th>Feed : gain</th></tr></thead><tbody>\n{rows}\n</tbody></table>'
                             '<p class="src">Source: South Dakota State University Extension, '
                             '<a href="https://extension.sdstate.edu/considering-creep-feeding">'
                             '"Considering Creep Feeding"</a>, fetched 2026-09-27. A second study, '
                             'Ohio State University Extension’s BEEF Cattle Letter, '
                             '<a href="https://u.osu.edu/beef/2000/05/10/is-creep-feed-cost-effective/">'
                             '"Is Creep Feed Cost Effective?"</a>, gives a flatter 8-to-1 conversion '
                             '-- a different framing, shown separately rather than blended in.</p>')
            elif text == "CALC_CROSS_LINKS":
                parts.append('<p>The '
                             f'<a href="{BASE}/stocking-rate-calculator/">Stocking Rate '
                             'Calculator</a> works out how many head your pasture carries; the '
                             f'<a href="{BASE}/winter-hay-calculator/">Winter Hay Calculator</a> '
                             'works out how many bales one winter takes; the '
                             f'<a href="{BASE}/manure-application-calculator/">Manure '
                             'Application Rate Calculator</a> works out tons or gallons '
                             'per acre.</p>')
            elif text == "MANURE_TARP_METHOD":
                parts.append('<p>A second way to check your spreader, using a tarp '
                             'instead of a measured travel path: weigh the manure that '
                             'lands on a tarp of known size, then Rate (tons/acre) = '
                             '(pounds on the tarp &times; 21.8) &divide; tarp area in '
                             'square feet. 21.8 is 43,560 square feet per acre divided '
                             'by 2,000 pounds per ton. Use a tarp sized 4′ 8″ '
                             '&times; 4′ 8″ (21.8 square feet) and the '
                             'pounds you weigh equal tons per acre directly, no further '
                             'math needed.</p>'
                             '<p class="src">Source: North Dakota State University '
                             'Extension, "Manure Spreader Calibration For Nutrient '
                             'Management Planning," ndsu.edu/agriculture/extension/'
                             'publications/manure-spreader-calibration-nutrient-'
                             'management-planning, fetched 2026-09-28.</p>')
            elif text == "MANURE_CROSS_LINKS":
                parts.append('<p>The '
                             f'<a href="{BASE}/stocking-rate-calculator/">Stocking Rate '
                             'Calculator</a> works out how many head your pasture '
                             f'carries; the <a href="{BASE}/winter-hay-calculator/">'
                             'Winter Hay Calculator</a> works out how many bales one '
                             f'winter takes; the <a href="{BASE}/creep-feed-calculator/">'
                             'Creep Feed Calculator</a> works out whether creep feeding '
                             'pays.</p>')
            else:
                parts.append(f"<p>{html.escape(text)}</p>")
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
