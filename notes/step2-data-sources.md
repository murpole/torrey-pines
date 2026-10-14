# Step 2: Data source research

**Bottom line:** Only one free source has all three numbers we need (driving distance, fairway %, and strokes gained) for each player at each event: PGA TOUR's own stats on pgatour.com. Its Terms of Use allow you to use those stats for personal, non-commercial work, but they **ban downloading them with scripts or scrapers**. So the free, rule-abiding route is to collect the tables by hand from your browser, which means we sample events instead of taking every one. I recommend that route, and I explain why below.

Nothing has been downloaded yet.

---

## What we need

For each player at each event, about 10 seasons: driving distance, driving accuracy (fairway %), SG: Total, and ideally SG: Tee-to-Green and SG: Off-the-Tee. We need this for the Farmers Insurance Open (Torrey Pines) and for other PGA TOUR events.

## Sources checked

| Source | Free? | Distance + fairway %? | Strokes gained? | Per event? | Years | Verdict |
|---|---|---|---|---|---|---|
| **pgatour.com stats** (official, "Tournament Only" view) | Yes | Yes | Yes (Total, T2G, OTT, APP, ARG, Putt) | Yes | 2004 to now | Best data. Terms of Use allow manual collection only |
| **pgatour.com data feed via a script** (the site's internal data feed; unofficial Python/R clients such as `pgatouR` and `pga-tour-unofficial-api` wrap it) | Yes | Yes | Yes | Yes | 2004 to now | Fast and complete, but **breaks Terms §7(C)**. Not recommended |
| **Data Golf Raw Data Archive** | **No**: needs the Scratch PLUS annual plan | Yes | Yes | Yes, round by round, with the course for each round | 2017–2026 | Best quality overall, and the only source that could separate North and South courses. Paid |
| **Kaggle "PGA Tour Golf Data (2015–2022)"** (data originally from Data Golf) | Yes (needs a free Kaggle login) | **No** | Yes (all 6 categories) | Yes | 2015–2022 | Can't answer the question on its own |
| **Shot-level academic data** (ShotLink) | Only by research agreement | – | – | – | – | Not public. The papers that use it can't share it (NDA) |

### Key details

**PGA TOUR Terms of Use** ([pgatour.com/company/terms-of-use](https://www.pgatour.com/company/terms-of-use), Section 7):
- 7(C): "You shall not use … PGATOUR.COM by automated electronic processes, robots, spiders, scrapers … or other computer programs that … download data … including … statistics."
- 7(D): "You may use … statistics and other data (whether current or archival) collected from PGATOUR.COM solely for legitimate news reporting and for personal, non-commercial purposes."

A student portfolio project fits "personal, non-commercial", so using the numbers is fine. The problem is only *how* we collect them: by hand is allowed, by script is not. Since you'll interview with the PGA TOUR, being able to say "I followed your terms" is worth a lot. Being caught out on this would cost you.

**Stat IDs on pgatour.com**, useful for finding the pages: 101 = Driving Distance, 102 = Driving Accuracy %, 02675 = SG: Total, 02674 = SG: Tee-to-Green, 02567 = SG: Off-the-Tee.

**What I could and couldn't test:** I read pgatour.com, Data Golf and Kaggle pages through a web reader and inspected the code of the unofficial clients. I could **not** pull a live table myself, because both my cloud workspace and the sandbox on your Mac block pgatour.com, Kaggle and Data Golf. So the per-event tables are confirmed from documentation and code, not from a test download. Your own browser has no such block.

## Things to watch for in Step 3

- **North vs. South Course:** The first two Farmers rounds are split across the North and South courses. PGA TOUR's tracking system (ShotLink) has historically covered the South Course more fully, so the event's strokes-gained and distance numbers may come only from South Course rounds. We'll check this on the first Torrey table. A North/South indicator would need round-level data, which in practice means Data Golf (paid).
- **Driving Distance (101) is measured on two holes per round**, the same way at every event, so the comparison is fair. There's also an "all drives" version we can check.
- **Missed cuts:** players who miss the cut have only 2 rounds of stats. We'll keep them but flag rounds played.
- **Season naming:** pgatour.com labels seasons by their ending year (2020–21 = "2021"), and 2020 was cut short by COVID.

## Recommendation: manual collection from pgatour.com, sampled design

1. **Torrey (treatment group):** Farmers Insurance Open, **2017–2026 (10 events)**.
2. **Comparison group:** a **random sample of 6 other full-field events per season** (60 events). I pick them with a fixed random seed, so the choice is reproducible and you can't be accused of cherry-picking. A random sample of events is a fair stand-in for "a typical PGA TOUR event".
3. **Per event**, you collect 3 required stats (distance, fairway %, SG: Total) and 2 optional ones (SG: T2G, SG: OTT). I'll give you an exact checklist of pages and a template, and a cleaning script that turns your pasted tables into the tidy CSV. The cleaning script reads only files on your computer, so it's fully within the terms.
4. **Effort:** roughly 70 events × 3–5 tables each. Before you start, I'll check whether the tournament's own "Stats" tab shows all the columns on one page. If it does, that's about 70 copy-pastes. If not, it's 210–350.

**Expected sample:** about 1,200–1,500 Torrey player-events and about 8,000–9,000 comparison player-events. That's plenty for OLS with player controls.

**If you'd rather not do manual collection:**
- Paying for one year of Data Golf Scratch PLUS gives every event plus North/South course detail, with clean downloads. That breaks the "free" rule, so it's your call.
- Scripting the pgatour.com data feed is technically easy but goes against the PGA TOUR terms. I don't recommend it for a project aimed at a PGA TOUR interview.
