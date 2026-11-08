"""Build the BabsonAI Labs database from its generated CSV files."""

import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import duckdb
    import polars as pl
    import matplotlib.pyplot as plt
    from datetime import date

    return date, duckdb, mo, pl, plt


@app.cell
def _(date, mo):
    as_of = date(2026, 11, 8)
    first_date = date(2025, 11, 9)
    mo.md(f"""
    # BabsonAI Labs: Building the Database

    **Scenario A.** Sample data covers **{first_date} through {as_of}**, inclusive.
    All people, clients, and transactions are fictional.

    Run `uv run python projects/db/make_data.py` to recreate the CSV files.
    Run `uv run python projects/db/build.py` to rebuild the database.
    """)
    return as_of, first_date


@app.cell
def _(duckdb, mo):
    # notebook_dir locates this notebook even when it is run from the repository root.
    database = mo.notebook_dir() / "database.duckdb"

    def ask(sql):
        # with closes the read-only connection as soon as the result is returned.
        with duckdb.connect(database, read_only=True) as _con:
            # pl() returns the query result as a Polars table.
            return _con.sql(sql).pl()

    return ask, database


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## The Tables

    The five tables follow the README diagram. `PRIMARY KEY` identifies a row;
    `REFERENCES` declares a foreign key; `NOT NULL` requires a value;
    `UNIQUE` prevents duplicates; and `CHECK` rejects values that break a rule.
    `DEFAULT 'planned'` supplies a project's status when an insert omits it.

    `DECIMAL(12, 2)` stores money with two decimal places, and `DECIMAL(5, 2)`
    allows fractional weekly hours. Optional fields allow `NULL`.

    This one cell deletes the old database, creates all five tables, loads the
    CSV files, and saves a view. Its connection closes before later cells run.
    """)
    return


@app.cell
def _(database, duckdb, mo, pl):
    _data_folder = mo.notebook_dir() / "data"
    # try_parse_dates reads the CSV date strings as dates rather than text.
    _people_rows = pl.read_csv(_data_folder / "people.csv", try_parse_dates=True)
    _project_rows = pl.read_csv(_data_folder / "projects.csv", try_parse_dates=True)
    _assignment_rows = pl.read_csv(_data_folder / "project_assignments.csv", try_parse_dates=True)
    _task_rows = pl.read_csv(_data_folder / "tasks.csv", try_parse_dates=True)
    _expense_rows = pl.read_csv(_data_folder / "expenses.csv", try_parse_dates=True)

    # unlink removes only this generated database; missing_ok allows the first build.
    database.unlink(missing_ok=True)
    with duckdb.connect(database) as _con:
        _con.execute("""
            CREATE TABLE people (
                person_id INTEGER PRIMARY KEY,
                first_name VARCHAR NOT NULL,
                last_name VARCHAR NOT NULL,
                email VARCHAR NOT NULL UNIQUE,
                title VARCHAR NOT NULL,
                start_date DATE NOT NULL,
                manager_id INTEGER REFERENCES people(person_id),
                CHECK (manager_id IS NULL OR manager_id <> person_id)
            )
        """)
        _con.execute("""
            CREATE TABLE projects (
                project_id INTEGER PRIMARY KEY,
                name VARCHAR NOT NULL,
                client_name VARCHAR,
                category VARCHAR NOT NULL
                    CHECK (category IN ('LLM app', 'data pipeline', 'internal tool')),
                budget DECIMAL(12, 2) NOT NULL CHECK (budget > 0),
                start_date DATE NOT NULL,
                status VARCHAR NOT NULL DEFAULT 'planned'
                    CHECK (status IN ('planned', 'active', 'paused', 'done'))
            )
        """)
        _con.execute("""
            CREATE TABLE project_assignments (
                person_id INTEGER NOT NULL REFERENCES people(person_id),
                project_id INTEGER NOT NULL REFERENCES projects(project_id),
                role VARCHAR NOT NULL,
                weekly_hours DECIMAL(5, 2) NOT NULL
                    CHECK (weekly_hours BETWEEN 1 AND 40),
                joined_date DATE NOT NULL,
                PRIMARY KEY (person_id, project_id)
            )
        """)
        _con.execute("""
            CREATE TABLE tasks (
                task_id INTEGER PRIMARY KEY,
                project_id INTEGER NOT NULL REFERENCES projects(project_id),
                description VARCHAR NOT NULL,
                created_date DATE NOT NULL,
                assigned_person_id INTEGER REFERENCES people(person_id),
                assigned_date DATE,
                due_date DATE NOT NULL,
                completed_date DATE,
                CHECK (due_date >= created_date),
                CHECK (completed_date IS NULL OR completed_date >= created_date),
                CHECK (assigned_date IS NULL OR assigned_date >= created_date),
                CHECK (
                    (assigned_person_id IS NULL AND assigned_date IS NULL)
                    OR (assigned_person_id IS NOT NULL AND assigned_date IS NOT NULL)
                )
            )
        """)
        _con.execute("""
            CREATE TABLE expenses (
                expense_id INTEGER PRIMARY KEY,
                project_id INTEGER NOT NULL REFERENCES projects(project_id),
                expense_date DATE NOT NULL,
                amount DECIMAL(12, 2) NOT NULL CHECK (amount > 0),
                category VARCHAR NOT NULL
                    CHECK (category IN ('GPU cloud', 'data labeling', 'software', 'travel')),
                note VARCHAR
            )
        """)

        # Managers occur before their reports in people.csv, so insert one person at a time.
        # select fixes the column order, and iter_rows supplies one tuple of values at a time.
        for _person in _people_rows.select(
            "person_id", "first_name", "last_name", "email", "title", "start_date", "manager_id"
        ).iter_rows():
            # Each ? is filled from the matching value in _person without building SQL text.
            _con.execute("INSERT INTO people VALUES (?, ?, ?, ?, ?, ?, ?)", _person)

        # register gives each Polars table a name DuckDB can use in SELECT statements.
        _con.register("_project_rows", _project_rows)
        _con.register("_assignment_rows", _assignment_rows)
        _con.register("_task_rows", _task_rows)
        _con.register("_expense_rows", _expense_rows)
        # Explicit column names keep loading correct even if CSV column order changes.
        _con.execute("""
            INSERT INTO projects
            SELECT project_id, name, client_name, category, budget, start_date, status
            FROM _project_rows
        """)
        _con.execute("""
            INSERT INTO project_assignments
            SELECT person_id, project_id, role, weekly_hours, joined_date
            FROM _assignment_rows
        """)
        _con.execute("""
            INSERT INTO tasks
            SELECT task_id, project_id, description, created_date, assigned_person_id,
                   assigned_date, due_date, completed_date
            FROM _task_rows
        """)
        _con.execute("""
            INSERT INTO expenses
            SELECT expense_id, project_id, expense_date, amount, category, note
            FROM _expense_rows
        """)

        # A view saves a query, so it uses the current data whenever somebody reads it.
        _con.execute("""
            CREATE VIEW project_spending AS
            SELECT
                p.project_id,
                p.name,
                p.status,
                p.budget,
                COALESCE(SUM(e.amount), 0) AS total_expenses,
                p.budget - COALESCE(SUM(e.amount), 0) AS remaining_budget,
                ROUND(100.0 * COALESCE(SUM(e.amount), 0) / p.budget, 2) AS budget_spent_pct
            FROM projects AS p
            LEFT JOIN expenses AS e ON p.project_id = e.project_id
            GROUP BY p.project_id, p.name, p.status, p.budget
        """)

        _source_counts = {
            "people": _people_rows.height,
            "projects": _project_rows.height,
            "project_assignments": _assignment_rows.height,
            "tasks": _task_rows.height,
            "expenses": _expense_rows.height,
        }
        _loaded_total = 0
        for _table, _source_count in _source_counts.items():
            # The table names come from the fixed dictionary above, not from user input.
            # fetchone()[0] takes the first value from a one-row SQL result.
            _actual = _con.execute(f"SELECT COUNT(*) FROM {_table}").fetchone()[0]
            if _actual != _source_count:
                raise ValueError(f"Row count mismatch for {_table}")
            print(f"{_table}: {_actual} rows")
            _loaded_total += _actual

    print(f"Loaded and typed {_loaded_total} CSV rows; rows skipped: 0.")
    print("Built database: database.duckdb")
    # Later query cells depend on this marker so marimo finishes the build first.
    build_ready = True
    return (build_ready,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## The Data

    `make_data.py` uses the fixed seed **7510** to generate five CSV files covering
    **November 9, 2025 through November 8, 2026**. Numeric and date columns are
    loaded into the declared SQL types; blank optional fields become `NULL`.
    All **573 rows** are loaded; none are skipped. Money and weekly hours retain
    their generated values when stored as decimals.

    **Exactly two intentional rule violations:** task IDs **1 and 2**, both in
    project **1**, are assigned to employee **25**, who is not on that project's
    team. The employee exists and was hired before both assignments. The rule
    about project membership will be checked with a query in Part B.

    Projects **11 and 12** are planned and have no tasks or expenses. Employee
    **25** has no project assignments. Some tasks are unassigned or unfinished;
    these empty relationships are allowed by the scenario.

    The checks below cover additional rules that compare dates across tables.
    The two membership violations above are deliberately kept for Part B.
    """)
    return


@app.cell
def _(as_of, ask, build_ready, first_date):
    # assert stops the notebook with an explanation if a required condition fails.
    assert build_ready
    data_checks = ask(f"""
        SELECT 'Project assignment before employee start' AS rule, COUNT(*) AS violations
        FROM project_assignments AS a
        JOIN people AS p ON a.person_id = p.person_id
        WHERE a.joined_date < p.start_date
        UNION ALL
        SELECT 'Project assignment before project start', COUNT(*)
        FROM project_assignments AS a
        JOIN projects AS p ON a.project_id = p.project_id
        WHERE a.joined_date < p.start_date
        UNION ALL
        SELECT 'Task assigned before employee start', COUNT(*)
        FROM tasks AS t
        JOIN people AS p ON t.assigned_person_id = p.person_id
        WHERE t.assigned_date < p.start_date
        UNION ALL
        SELECT 'Task created before project start', COUNT(*)
        FROM tasks AS t
        JOIN projects AS p ON t.project_id = p.project_id
        WHERE t.created_date < p.start_date
        UNION ALL
        SELECT 'Expense before project start', COUNT(*)
        FROM expenses AS e
        JOIN projects AS p ON e.project_id = p.project_id
        WHERE e.expense_date < p.start_date
        UNION ALL
        SELECT 'Project without any team member', COUNT(*)
        FROM projects AS p
        WHERE NOT EXISTS (
            SELECT 1 FROM project_assignments AS a WHERE a.project_id = p.project_id
        )
        UNION ALL
        SELECT 'Task created outside the sample period', COUNT(*)
        FROM tasks
        WHERE created_date < DATE '{first_date}' OR created_date > DATE '{as_of}'
        UNION ALL
        SELECT 'Expense outside the sample period', COUNT(*)
        FROM expenses
        WHERE expense_date < DATE '{first_date}' OR expense_date > DATE '{as_of}'
    """)
    if data_checks["violations"].sum() != 0:
        raise ValueError("An unexpected data rule was broken; inspect data_checks.")
    print("Additional data-rule violations: 0")
    data_checks
    return (data_checks,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## A Look at the Data

    Read `expenses.csv` with Polars and chart the amounts before using them.
    """)
    return


@app.cell
def _(mo, pl, plt):
    expense_csv = pl.read_csv(mo.notebook_dir() / "data" / "expenses.csv")
    # subplots creates a figure and its plotting area; hist groups amounts into ranges.
    expense_figure, _axes = plt.subplots(figsize=(8, 4))
    _axes.hist(expense_csv["amount"], bins=15, color="#356b8c", edgecolor="white")
    _axes.set_xlabel("Expense amount ($)")
    _axes.set_ylabel("Number of expenses")
    _axes.set_title("BabsonAI Labs: Sample Expense Amounts")
    # tight_layout leaves room for the title and axis labels.
    expense_figure.tight_layout()
    expense_figure
    return (expense_figure,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    Smaller charges are more common than large charges, which is plausible for
    frequent software and labeling costs mixed with occasional larger cloud bills;
    these remain simplified sample expenses rather than actual business records.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Row Counts

    Each table's count is shown below; the build also compares it with its CSV.
    `UNION ALL` places the five counts in one result table.
    """)
    return


@app.cell
def _(ask, build_ready):
    assert build_ready
    row_counts = ask("""
        SELECT 'people' AS table_name, COUNT(*) AS rows FROM people
        UNION ALL SELECT 'projects', COUNT(*) FROM projects
        UNION ALL SELECT 'project_assignments', COUNT(*) FROM project_assignments
        UNION ALL SELECT 'tasks', COUNT(*) FROM tasks
        UNION ALL SELECT 'expenses', COUNT(*) FROM expenses
    """)
    row_counts
    return (row_counts,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## A Row It Refuses

    Try inserting an expense of **-10 dollars**. The database must reject it
    because `amount` must be greater than zero. `try` and `except` display the
    expected error while allowing the notebook to continue. A transaction is
    rolled back afterward so this demonstration cannot add a row.
    """)
    return


@app.cell
def _(as_of, build_ready, database, duckdb, mo):
    assert build_ready
    with duckdb.connect(database) as _con:
        _con.execute("BEGIN TRANSACTION")
        try:
            _con.execute("""
                INSERT INTO expenses
                    (expense_id, project_id, expense_date, amount, category, note)
                VALUES (?, ?, ?, ?, ?, ?)
            """, [9999, 1, as_of, -10, "software", "Deliberately invalid expense"])
        except duckdb.ConstraintException as _error:
            refused_message = str(_error)
        else:
            raise AssertionError("The database unexpectedly accepted a negative expense.")
        finally:
            # finally runs even after an error, and ROLLBACK discards the test insert.
            _con.execute("ROLLBACK")

    print("Negative expense refused:", refused_message)
    mo.md("```text\n" + refused_message + "\n```")
    refusal_checked = True
    return (refusal_checked,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Answers You Already Knew

    Before running these queries, the generator tells us to expect:

    - **25 employees**, because it creates 25 fictional people.
    - **300 tasks**, because its ten task counts add up to 300.
    - **2 planned projects**, because projects 11 and 12 are marked planned.

    The SQL and the comparison appear together in the table below.
    """)
    return


@app.cell
def _(ask, build_ready, pl, refusal_checked):
    assert build_ready and refusal_checked
    _checks = [
        ("Employees", 25, "SELECT COUNT(*) FROM people"),
        ("Tasks", 300, "SELECT COUNT(*) FROM tasks"),
        ("Planned projects", 2, "SELECT COUNT(*) FROM projects WHERE status = 'planned'"),
    ]
    _results = []
    for _label, _expected, _sql in _checks:
        # item() reads the single value returned by a one-cell Polars table.
        _actual = ask(_sql).item()
        if _actual != _expected:
            raise ValueError(f"{_label}: expected {_expected}, got {_actual}")
        print(f"{_label}: expected {_expected}, actual {_actual}")
        _results.append({"check": _label, "sql": _sql, "expected": _expected, "actual": _actual})
    known_answers = pl.DataFrame(_results)
    known_answers
    return (known_answers,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## A View

    **Weekly question:** How much of each project's budget has been spent?

    The build cell saves the query as `project_spending`. It keeps projects with
    no expenses using `LEFT JOIN`; `COALESCE` replaces an empty spending total
    with zero. Its columns include total expenses, remaining budget, and the
    percentage spent. Part B will use this view for the project-budget question.

    The check below confirms that the view exists. The business answers belong
    in `questions.py` after its required prediction commit.
    """)
    return


@app.cell
def _(ask, build_ready):
    assert build_ready
    saved_view = ask("""
        SELECT view_name FROM duckdb_views()
        WHERE schema_name = 'main' AND view_name = 'project_spending'
    """)
    if saved_view.height != 1:
        raise ValueError("The project_spending view was not created.")
    print("Saved view: project_spending")
    saved_view
    return (saved_view,)


if __name__ == "__main__":
    app.run()
