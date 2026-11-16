"""BabsonAI Labs Part B -- join prediction only; commit before writing answers."""
import marimo
__generated_with = "0.24.2"
app = marimo.App(width="medium")

@app.cell

def _():
    import marimo as mo
    return (mo,)

@app.cell(hide_code=True)
def _(mo):
    mo.md("""# BabsonAI Labs: Part B — The Questions

## 3. Reading It Back (prediction written before querying)

**Chosen question:** Question 6, one row per project with its task count and total expenses. This requires projects, tasks, and expenses.

**My prediction:** A raw `projects LEFT JOIN tasks LEFT JOIN expenses` will produce **6,164 joined rows before grouping**. For the first ten projects, each task matches every expense within the project: `48×30 + 42×26 + 37×24 + 35×22 + 32×20 + 28×18 + 24×14 + 22×12 + 18×8 + 14×6 = 6,162` rows. Projects 11 and 12 have neither tasks nor expenses, adding one NULL-extended row each, for a total of **6,164**. I derived this prediction from the fixed data counts in `make_data.py` before running a join.

After committing this prediction, I will execute and inspect the SQL and explain what each final result row means.
""")
    return

if __name__ == "__main__":
    app.run()