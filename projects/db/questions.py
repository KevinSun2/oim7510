"""BabsonAI Labs -- Part B of the OIM7510 database project.

IMPORTANT: Commit the join prediction in questions_prediction_first.py as
`db: prediction` BEFORE copying this completed file into projects/db/questions.py.
Run Part A's build.py to create database.duckdb before opening this notebook.
"""
import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")

@app.cell
def _():
    import marimo as mo
    import duckdb
    import polars as pl
    from datetime import date, timedelta
    import matplotlib.pyplot as plt
    return mo, duckdb, pl, date, timedelta, plt

@app.cell
def _(mo, duckdb, date):
    as_of = date(2026, 11, 8)
    database = mo.notebook_dir() / "database.duckdb"
    def ask(sql):
        with duckdb.connect(database, read_only=True) as _con:
            return _con.sql(sql).pl()
    mo.md(f"""# BabsonAI Labs — Part B: The Questions
    **Scenario A | Database reference date: {as_of:%B %d, %Y}**
    
    All dates in this notebook use the fixed `as_of` date, not the computer's date.
    Run `build.py` to create `database.duckdb` before running this notebook.
    The query results and the numerical conclusion for each question appear together below.""")
    return as_of, database, ask

@app.cell(hide_code=True)
def _(mo):
    mo.md('## Question 1. How much of each project’s budget has been spent?')
    return 

@app.cell
def _(ask, as_of):
    sql_1 = f'SELECT project_id, name, status, budget, total_expenses,\n       remaining_budget, budget_spent_pct\nFROM project_spending\nORDER BY budget_spent_pct DESC, project_id'
    q1 = ask(sql_1)
    print("SQL:")
    print(sql_1)
    print("\nResult:")
    print(q1)
    _top = q1.row(0, named=True)
    print(f"Answer: {_top['name']} has the highest budget share spent, at {_top['budget_spent_pct']:.2f}% (${_top['total_expenses']:,.2f} of ${_top['budget']:,.2f}).")
    return q1, sql_1

@app.cell(hide_code=True)
def _(mo):
    mo.md('## Question 2. Which tasks are overdue and still unfinished?')
    return 

@app.cell
def _(ask, as_of):
    sql_2 = f"SELECT t.task_id, p.name AS project_name,\n       COALESCE(pe.first_name || ' ' || pe.last_name, 'Unassigned') AS assignee,\n       t.due_date\nFROM tasks AS t\nJOIN projects AS p ON t.project_id = p.project_id\nLEFT JOIN people AS pe ON t.assigned_person_id = pe.person_id\nWHERE t.completed_date IS NULL\n  AND t.due_date < DATE '{as_of}'\nORDER BY t.due_date, t.task_id"
    q2 = ask(sql_2)
    print("SQL:")
    print(sql_2)
    print("\nResult:")
    print(q2)
    print(f"Answer: {q2.height} tasks were unfinished and past due on {as_of} (the due date must be earlier than the reference date).")
    return q2, sql_2

@app.cell(hide_code=True)
def _(mo):
    mo.md('## Question 3. Who has more than 40 weekly hours across active projects?')
    return 

@app.cell
def _(ask, as_of, pl):
    sql_3 = f"WITH hours AS (\n    SELECT pe.person_id, pe.first_name, pe.last_name,\n           COALESCE(SUM(CASE WHEN pr.status = 'active'\n                              THEN pa.weekly_hours ELSE 0 END), 0) AS active_hours\n    FROM people AS pe\n    LEFT JOIN project_assignments AS pa ON pe.person_id = pa.person_id\n    LEFT JOIN projects AS pr ON pa.project_id = pr.project_id\n    GROUP BY pe.person_id, pe.first_name, pe.last_name\n)\nSELECT *, active_hours > 40 AS above_40\nFROM hours ORDER BY active_hours DESC, person_id"
    q3 = ask(sql_3)
    print("SQL:")
    print(sql_3)
    print("\nResult:")
    print(q3)
    _over = q3.filter(pl.col('above_40'))
    print(f"Answer: {_over.height} employees have more than 40 committed hours per week across active projects; the maximum is {q3['active_hours'].max():.2f} hours.")
    return q3, sql_3

@app.cell(hide_code=True)
def _(mo):
    mo.md('## Question 4. Which expense categories exceed average category spending over the last 90 days?')
    return 

@app.cell
def _(ask, as_of):
    sql_4 = f"WITH category_totals AS (\n    SELECT category, SUM(amount) AS total_spent\n    FROM expenses\n    WHERE expense_date BETWEEN DATE '{as_of}' - INTERVAL 89 DAY\n                           AND DATE '{as_of}'\n    GROUP BY category\n)\nSELECT category, total_spent\nFROM category_totals\nWHERE total_spent > (SELECT AVG(total_spent) FROM category_totals)\nORDER BY total_spent DESC"
    q4 = ask(sql_4)
    print("SQL:")
    print(sql_4)
    print("\nResult:")
    print(q4)
    print(f"Answer: {q4.height} categories exceed the average category total over the 90 days ending {as_of}; their combined spending is ${q4['total_spent'].sum():,.2f}.")
    return q4, sql_4

@app.cell(hide_code=True)
def _(mo):
    mo.md('## Question 5. Which projects have never recorded an expense?')
    return 

@app.cell
def _(ask, as_of):
    sql_5 = f'SELECT p.project_id, p.name, p.status\nFROM projects AS p\nWHERE NOT EXISTS (\n    SELECT 1 FROM expenses AS e WHERE e.project_id = p.project_id\n)\nORDER BY p.project_id'
    q5 = ask(sql_5)
    print("SQL:")
    print(sql_5)
    print("\nResult:")
    print(q5)
    print(f"Answer: {q5.height} projects have no recorded expenses: {', '.join(q5['name'].to_list())}.")
    return q5, sql_5

@app.cell(hide_code=True)
def _(mo):
    mo.md('## Question 6. How many tasks and how much spending does each project have?')
    return 

@app.cell
def _(ask, as_of):
    sql_6 = f'WITH task_totals AS (\n    SELECT project_id, COUNT(*) AS task_count\n    FROM tasks GROUP BY project_id\n), expense_totals AS (\n    SELECT project_id, SUM(amount) AS expenses_total\n    FROM expenses GROUP BY project_id\n)\nSELECT p.project_id, p.name,\n       COALESCE(t.task_count, 0) AS task_count,\n       COALESCE(e.expenses_total, 0) AS expenses_total\nFROM projects AS p\nLEFT JOIN task_totals AS t ON p.project_id = t.project_id\nLEFT JOIN expense_totals AS e ON p.project_id = e.project_id\nORDER BY p.project_id'
    q6 = ask(sql_6)
    print("SQL:")
    print(sql_6)
    print("\nResult:")
    print(q6)
    print(f"Answer: Across {q6.height} projects, there are {q6['task_count'].sum()} tasks and ${q6['expenses_total'].sum():,.2f} in expenses. Tasks and expenses are aggregated separately to avoid multiplying amounts.")
    return q6, sql_6

@app.cell(hide_code=True)
def _(mo):
    mo.md('## Question 7. Which tasks violate the project-team membership rule?')
    return 

@app.cell
def _(ask, as_of):
    sql_7 = f"SELECT t.task_id, t.project_id, t.assigned_person_id,\n       pe.first_name || ' ' || pe.last_name AS assignee_name\nFROM tasks AS t\nJOIN people AS pe ON t.assigned_person_id = pe.person_id\nLEFT JOIN project_assignments AS a\n    ON t.project_id = a.project_id AND t.assigned_person_id = a.person_id\nWHERE a.person_id IS NULL\nORDER BY t.task_id"
    q7 = ask(sql_7)
    print("SQL:")
    print(sql_7)
    print("\nResult:")
    print(q7)
    _ids = q7['task_id'].to_list()
    print(f"Answer: {q7.height} tasks violate the project membership rule: IDs {_ids}. Part A deliberately created violations for task IDs 1 and 2.")
    return q7, sql_7

@app.cell(hide_code=True)
def _(mo):
    mo.md('## Question 8. Which projects have the lowest task completion rates? (Our own business question)')
    return 

@app.cell
def _(ask, as_of, pl):
    sql_8 = f'SELECT p.project_id, p.name, COUNT(t.task_id) AS total_tasks,\n       COUNT(t.completed_date) AS completed_tasks,\n       ROUND(100.0 * COUNT(t.completed_date) / NULLIF(COUNT(t.task_id), 0), 2)\n           AS completion_rate_pct\nFROM projects AS p\nLEFT JOIN tasks AS t ON p.project_id = t.project_id\nGROUP BY p.project_id, p.name\nORDER BY completion_rate_pct ASC NULLS LAST, p.project_id'
    q8 = ask(sql_8)
    print("SQL:")
    print(sql_8)
    print("\nResult:")
    print(q8)
    _tracked = q8.filter(pl.col('total_tasks') > 0)
    _worst = _tracked.row(0, named=True)
    print(f"Answer: Among { _tracked.height } projects with tasks, {_worst['name']} has the lowest completion rate, at {_worst['completion_rate_pct']:.2f}% ({_worst['completed_tasks']} of {_worst['total_tasks']} tasks). Projects with zero tasks have an undefined rate and are listed last.")
    return q8, sql_8

@app.cell(hide_code=True)
def _(mo):
    mo.md('## 1. How I Know These Numbers Are Right\n\nThe following two checks calculate earlier answers in a separate way and assert that the numbers agree.')
    return 

@app.cell
def _(ask, q1, q5, q6, pl):
    # Check A: spending in the saved project_spending view (Question 1)
    # versus a direct sum from the original expenses table.
    check_a = ask("SELECT COALESCE(SUM(amount), 0) AS total FROM expenses")
    _view_amount = float(q1["total_expenses"].sum())
    _raw_amount = float(check_a["total"][0])
    assert abs(_view_amount - _raw_amount) < 0.01
    print(f"Check A PASS: view sums to ${_view_amount:,.2f}; source expenses sum to ${_raw_amount:,.2f}.")
    
    # Check B: Question 6's project task counts and expense amounts are
    # independently recomputed with correlated subqueries, one project at a time.
    check_b = ask("""
        SELECT p.project_id,
          (SELECT COUNT(*) FROM tasks t WHERE t.project_id = p.project_id) AS direct_tasks,
          COALESCE((SELECT SUM(amount) FROM expenses e
                    WHERE e.project_id = p.project_id), 0) AS direct_expenses
        FROM projects p ORDER BY p.project_id
    """)
    _compare = q6.join(check_b, on="project_id")
    _count_ok = bool((_compare["task_count"] == _compare["direct_tasks"]).all())
    _expense_ok = all(abs(float(a) - float(b)) < 0.01 for a, b in
                      zip(_compare["expenses_total"], _compare["direct_expenses"]))
    assert _count_ok and _expense_ok
    print(f"Check B PASS: all {_compare.height} project task counts and expense totals match independent subqueries.")
    print(check_b)
    return check_a, check_b

@app.cell(hide_code=True)
def _(mo):
    mo.md('## 2. Working With the Agent\n\nI inspected the SQL for **Question 6** before accepting it. A tempting approach is to join `projects`, `tasks`, and `expenses` directly and then `COUNT` tasks and `SUM` expenses. That is incorrect because each task pairs with every expense in the same project, multiplying both counts and dollar amounts. I used separate task and expense aggregates before joining them to projects. The independent per-project check in the **How I Know These Numbers Are Right** cell verifies the corrected approach. The relevant cells are **Question 6** and **Check B**.')
    return 

@app.cell(hide_code=True)
def _(mo):
    mo.md('## 3. Reading It Back\n\n**Question chosen:** Question 6, one row per project showing its number of tasks and total spending.\n\n**Prediction recorded before executing the join:** A direct `projects LEFT JOIN tasks LEFT JOIN expenses` without grouping should yield **6,164 rows**. In projects 1–10, every task joins to every expense within its project, yielding `48×30 + 42×26 + 37×24 + 35×22 + 32×20 + 28×18 + 24×14 + 22×12 + 18×8 + 14×6 = 6,162` rows. Projects 11 and 12 each contribute one NULL-extended row because they have no tasks or expenses. This prediction comes from the fixed counts in `make_data.py`, not a count query.\n\n**Important:** To satisfy the professor’s commit-order rule, commit this prediction as `db: prediction` before running the queries in the completed notebook.')
    return 

@app.cell
def _(ask):
    join_count = ask("""
    SELECT COUNT(*) AS joined_rows
    FROM projects AS p
    LEFT JOIN tasks AS t ON p.project_id = t.project_id
    LEFT JOIN expenses AS e ON p.project_id = e.project_id
    """)
    _actual = int(join_count["joined_rows"][0])
    print(f"Predicted 6,164 join rows; observed {_actual:,} rows; match: {_actual == 6164}.")
    assert _actual == 6164
    print("One row of the final Question 6 result represents one project, its total distinct tasks, and its total spending.")
    return join_count

@app.cell(hide_code=True)
def _(mo):
    mo.md('## 4. Going Further\n\nI plotted total expenses by project to make the budget-analysis results easier for a manager to compare. The chart below goes beyond the required SQL table, and both axes are labeled.')
    return 

@app.cell
def _(q1, plt):
    _plot_data = q1.sort('total_expenses', descending=True)
    figure, _ax = plt.subplots(figsize=(10, 5))
    _ax.barh(_plot_data['name'].to_list()[::-1], [float(x) for x in _plot_data['total_expenses']][::-1])
    _ax.set_xlabel('Total expenses (USD)')
    _ax.set_ylabel('Project')
    _ax.set_title('BabsonAI Labs: Project expenses through November 8, 2026')
    figure.tight_layout()
    figure
    return figure

@app.cell(hide_code=True)
def _(mo):
    mo.md('## 5. Time Spent\n\n**Fill in your actual total number of hours spent outside class on both parts before submission.**')
    return 

if __name__ == "__main__":
    app.run()