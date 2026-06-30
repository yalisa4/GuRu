import marimo

__generated_with = "0.14.17"
app = marimo.App(width="columns")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### File name and content validator""")
    return


@app.cell
def _():
    import marimo as mo

    import re
    import pandas as pd
    from pathlib import Path
    return Path, mo, pd, re


@app.cell
def _(Path, mo, re):
    # ── Constants ────────────────────────────────────────────────────────────────

    INPUT_DIR = Path(__file__).parent.parent / "assets"

    # Get all scrapes (old and recent)
    INPUT_FILES = list(INPUT_DIR.glob("datawiki_scrape_*.csv"))

    if not INPUT_FILES:
        raise FileNotFoundError("No matching datawiki_scrape_*.csv files found.")

    def extract_date(p: Path) -> str:
        m = re.search(r"datawiki_scrape_(\d{4}-?\d{2}-?\d{2})", p.stem)
        return m.group(1) if m else ""

    # Most recent file
    INPUT_FILE = max(INPUT_FILES, key=extract_date)

    mo.md(f"Latest update: **{extract_date(INPUT_FILE)}**")
    return (INPUT_FILE,)


@app.cell
def _(INPUT_FILE, pd):
    df = pd.read_csv(INPUT_FILE)
    df
    return (df,)


@app.cell
def _(df):

    df[df["file_name"].duplicated(keep=False)]
    return


@app.cell
def _(df):
    n_parts = df["file_name"].str.split(" ").str.len()

    # Rows with more than one part (i.e., contains at least one space)
    multi_word = df[n_parts > 1]

    print(f"{len(multi_word)} rows have more than one group")
    multi_word
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
