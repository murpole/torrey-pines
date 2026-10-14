# CLAUDE.md — project context for Claude

## Who and why
- Owner: murp (GitHub `murpole`), UCSD Math-Econ major. Has taken Econometrics (OLS), Linear Algebra, Calculus.
- Python beginner. Explain every piece of code in plain English.
- Project is for a resume and internship interviews (PGA TOUR, PING), so the owner must be able to explain every step.

## Research question
At Torrey Pines (North + South courses, Farmers Insurance Open), is it more rewarding to hit it farther and miss more fairways, or hit it shorter and find more fairways? How does that trade-off compare with a typical PGA TOUR event?

## Data rules
- Real data from free, public sources only. **Never invent or simulate data.**
- If a source can't be accessed, say so and suggest alternatives.
- Report sources, coverage and a recommendation BEFORE downloading anything.
- Unit of observation: player x event x year, ~8–10 seasons.
- Variables: player, year, event, distance, fairway_pct, sg_total, sg_t2g, sg_ott, is_torrey.
- `is_torrey` = 1 for the Farmers Insurance Open (North + South combined). Add a course indicator only if round-level data allows it.
- Comparison group: all other PGA TOUR events.
- Raw downloads go in `data/raw/` untouched; cleaned output goes in `data/clean/`.

## Method
1. OLS (statsmodels): strokes gained ~ driving distance + fairway %, fit for Torrey events and for all other events.
2. Compare coefficients and convert to a plain-English trade-off, e.g. "at Torrey, 10 yards of distance is worth X% of fairways, vs. Y% on tour" (ratio of the two slopes).
3. Discuss confounding (better players are often both long and accurate); add player-skill controls if feasible.

## Steps (stop after each one for the owner's review)
1. Setup: venv, requirements.txt, folders, README stub, this file.
2. Research data sources; report findings and recommendation before downloading.
3. Collect and clean into one tidy CSV.
4. Explore: summary stats; scatter of distance vs. fairway %, colored by strokes gained, Torrey highlighted.
5. Model: run regressions, compare Torrey vs. tour, interpret.
6. Publish: clean notebook, 3 polished charts, README (question, data, method, 3 findings, limitations), then GitHub.

## Working rules
- Pause at the end of every step for review.
- Ask before creating a GitHub repo or pushing anything.
