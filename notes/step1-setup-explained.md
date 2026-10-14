# Step 1 explained: project setup

Everything lives in `torrey-pines/`. Here is what each piece is and why it exists.

## The folders

```
torrey-pines/
├── data/raw/      data exactly as downloaded, never edited by hand
├── data/clean/    the one tidy CSV we build from the raw data
├── notebooks/     Jupyter notebooks for exploring and modeling
├── figures/       saved charts (PNG) for the README
├── requirements.txt
├── README.md
├── CLAUDE.md
└── .gitignore
```

Keeping raw and clean data apart is a habit interviewers like to hear about: if a cleaning step ever looks wrong, you can rerun it from the untouched originals. Each empty folder has a tiny `.gitkeep` file only because Git won't save an empty folder.

## requirements.txt

A shopping list of the Python libraries the project uses, one per line. Anyone (you on a new laptop, a recruiter cloning your repo) runs one command and gets the same tools:

| Library | What we use it for |
|---|---|
| pandas | Tables of data (like Excel in code): loading, filtering, merging |
| numpy | Fast math on columns of numbers; pandas is built on it |
| statsmodels | The OLS regressions, with standard errors and p-values like in Econometrics |
| matplotlib | Drawing charts |
| seaborn | Nicer-looking charts on top of matplotlib with less code |
| jupyter | Notebooks: code, charts and written explanation in one document |
| requests | Downloading data from websites |

I tested the list: all seven install cleanly on Python 3.13 (pandas 3.0, statsmodels 0.15).

## The virtual environment (`.venv`)

A virtual environment is a private copy of Python just for this project. Libraries installed into it don't touch other projects or your system Python, so version clashes can't break anything. It's a folder of installed files that you rebuild from `requirements.txt` whenever needed, which is why `.gitignore` keeps it off GitHub.

It has to be created on the computer where you'll run the code. Run these in a terminal inside the `torrey-pines` folder:

```bash
python3 -m venv .venv
```
"Python, use your built-in `venv` tool to create a virtual environment in a folder called `.venv`." (The dot makes it a hidden folder.)

```bash
source .venv/bin/activate        # Mac/Linux
.venv\Scripts\activate           # Windows
```
"Switch this terminal to use the project's private Python." Your prompt will start showing `(.venv)`. You do this each time you open a new terminal for the project.

```bash
pip install -r requirements.txt
```
"pip (Python's installer), install everything listed (`-r`) in requirements.txt."

```bash
jupyter notebook
```
Opens Jupyter in your browser so you can create and run notebooks.

## README.md

The front page of the project on GitHub. Right now it's a stub with the question, empty sections (Data, Method, Findings, Limitations) that we fill as we go, and the run instructions above. In Step 6 it becomes the polished write-up.

## CLAUDE.md

A memory file for Claude. It records the question, the data rules (real, free, public data only; never simulate; report sources before downloading), the variables we want, the regression method, the six steps, and the rule to pause after each step. Any future Claude session working in this folder reads it first, so the context never gets lost.

## .gitignore

Tells Git which files never to upload: the `.venv` folder, Python's cache files, and Jupyter's autosave checkpoints.
