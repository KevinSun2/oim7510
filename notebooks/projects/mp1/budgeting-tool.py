# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
# ]
# ///
"""Mini Project 1.
"""

import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium", sql_output="polars")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Mini Project 1

    Your choice of option, what each one asks for, the due date and how it is graded are on the Mini Project 1 page of the course site, linked from the calendar. This notebook is the shape to build it in. Keep the headings, and replace each line in italics with your own.

    Save it in your course repository as `projects/mp1/<your-tool>.py`, named for what it does, such as `loan-schedule.py`, and open it with `uv run marimo edit`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. The Question

    *Who would use this, and what decision does it help them make? Two or three sentences, in words somebody outside this course would understand.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This simple personal budgeting tool helps users track income, expenses, bills, and financial goals. Users can enter details such as each bill's amount and category. When the user changes any input value, the tool automatically updates the results to show total expenses, remaining income, and progress toward financial goals.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. My Plan Before AI

    *Before you ask your agent anything, write how you would solve it: the steps, in order, in plain words, in five lines or more. Then answer these two questions:*

    - *What does your loop carry from one step to the next, the way a running total carries its sum?*
    - *Which check will you use in section 6, and which two numbers should agree?*

    *Commit this notebook with the message `mp1: plan before AI`.*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The loops will carry running totals for income and expenses from one entry to the next. Each income source will be added to total income, while each bill or expense will be added to total expenses. The program can then subtract total expenses from total income to determine how much money is left.
    In Section 6, I will separately add the individual income entries and expense entries and compare them with the totals calculated by the loops. The independently calculated totals and the program's totals should agree.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Inputs

    Every number the project starts from goes in the cell below, and nowhere else, so that changing one input changes every result after it.

    Copy in the default inputs for your option from the Mini Project 1 page. If you chose D, your own option, type your data in here, or ask your agent to generate it with `faker`. The required part reads no file.
    """)
    return


@app.cell
def _():
    # Income inputs
    income_sources = [
        ("Take Home Pay", 8267.00, "Post-Tax Income"),
        ("VA Disability", 2102.50, "Non-Taxable Income"),
    ]
    # Expense inputs
    expenses = [
        ("Mortgage", 2402.00, "Housing"),
        ("Home Insurance",160.00, "Housing"),
        ("Property Tax", 300.00, "Housing"),
        ("HoA", 157.00, "Housing"),
        ("Car Insurance", 250.00, "Transportation"),
        ("Food", 1000.00, "Food"),
        ("Utilities", 250.00, "Utilities"),
        ("Gas", 180.00, "Transportation"),
        ("Entertainment", 400.00, "Entertainment"),
        ("Dental Insurance", 40.00, "Insurance"),
        ("Vision Insurance", 13.00, "Insurance"),
    ]
    #Alternative Accounts Inputs
    alternative_accounts = [
        ("Savings", 2000.00, "Savings"),
        ("Emergency Fund", 1500.00, "Savings"),
    ]

    # Goal Inputs
    goal_name = "New Car"
    goal_target = 50000.00

    return (
        alternative_accounts,
        expenses,
        goal_name,
        goal_target,
        income_sources,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. The Work

    Add as many cells as you need. Try each step yourself before you ask your agent, and commit as you go.
    """)
    return


@app.cell
def _(income_sources):
    total_income = 0

    for name, amount, category in income_sources:
        total_income = total_income + amount

    print(f"Total monthly income: ${total_income:,.2f}")
    return (total_income,)


@app.cell
def _(expenses):
    def _():
        total = 0
        for name, amount, category in expenses:
            total = total + amount
        return total

    total_expenses = _()
    print(f"Total monthly expenses: ${total_expenses:,.2f}")
    return (total_expenses,)


@app.cell
def _(total_expenses, total_income):
    net_income = total_income - total_expenses
    print(f"Net income after expenses: ${net_income:,.2f}")
    return (net_income,)


@app.cell
def _(alternative_accounts):
    total_alternative = 0

    for account_name, account_amount, account_category in alternative_accounts:
        total_alternative = total_alternative + account_amount

    print(f"Total alternative accounts: ${total_alternative:,.2f}")
    return (total_alternative,)


@app.cell
def _(net_income, total_alternative):
    leftover_income = net_income - total_alternative

    print(f"Goal Savings: ${leftover_income:,.2f}")
    return (leftover_income,)


@app.cell
def _(goal_name, goal_target, leftover_income):
    months_to_goal = goal_target / leftover_income
    print(f"Months to reach '{goal_name}' goal of ${goal_target:,.2f}: {months_to_goal:,.1f} months")
    return


@app.cell
def _(total_alternative):
    alternative_balance = 0

    for month in range(1, 30):
        alternative_balance = alternative_balance + total_alternative

    print(f"Alternative accounts balance after {month} months: ${alternative_balance:,.2f}")
    return


@app.cell
def _():
    months_input = 18
    return (months_input,)


@app.cell
def _(goal_target, leftover_income, months_input, total_alternative):
    leftover_balance = leftover_income * months_input
    alternative_balance_projected = total_alternative * months_input
    combined_balance = leftover_balance + alternative_balance_projected
    percent_of_goal = (combined_balance / goal_target) * 100

    print(f"In {months_input} months:")
    print(f"  Goal Savings: ${leftover_balance:,.2f}")
    print(f"  Alternative accounts: ${alternative_balance_projected:,.2f}")
    print(f"  Combined total: ${combined_balance:,.2f}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. The Answer

    *A table of your results in the cell below, printed with `print` and f-strings, then one sentence here that answers the question in section 1, with the number in it.*
    """)
    return


@app.cell
def _(
    leftover_income,
    net_income,
    total_alternative,
    total_expenses,
    total_income,
):
    print(f"{'Budget Summary Monthly':<30} {'Amount':>12}")
    print("-" * 43)

    print(f"{'Total Income':<30} ${total_income:>11,.2f}")
    print(f"{'Total Expenses':<30} ${total_expenses:>11,.2f}")
    print(f"{'Net Income':<30} ${net_income:>11,.2f}")
    print(f"{'Alternative Accounts':<30} ${total_alternative:>11,.2f}")
    print(f"{'Leftover Income':<30} ${leftover_income:>11,.2f}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    After monthly expenses and planned contributions to alternative accounts, this budget leaves $1,717.50 in leftover income each month that can be applied toward the New Car goal.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. How I Know These Numbers Are Right

    *At least one check that reaches a result a second, independent way. Name what you compared and what came out.*
    """)
    return


@app.cell
def _(
    leftover_income,
    net_income,
    total_alternative,
    total_expenses,
    total_income,
):
    check_income = (
        8267.00
        + 2102.50
    )

    check_expenses = (
        2402.00
        + 160.00
        + 300.00
        + 157.00
        + 250.00
        + 1000.00
        + 250.00
        + 180.00
        + 400.00
        + 40.00
        + 13.00
    )
    alternative_check = 2000.00 + 1500.00

    net_income_check = check_income - check_expenses

    leftover_income_check = net_income_check - alternative_check

    print(f"Income check: ${check_income:,.2f}")
    print(f"Program income total: ${total_income:,.2f}")

    print(f"Expense check: ${check_expenses:,.2f}")
    print(f"Program expense total: ${total_expenses:,.2f}")

    print(f"Alternative accounts check: ${alternative_check:,.2f}")
    print(f"Program alternative accounts total: ${total_alternative:,.2f}")

    print(f"Net income check: ${net_income_check:,.2f}")
    print(f"Program net income: ${net_income:,.2f}")

    print(f"Leftover income check: ${leftover_income_check:,.2f}")
    print(f"Program leftover income: ${leftover_income:,.2f}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    I compared all the incomes, expenses, net income, and what is left over after despositing into alternative accounts and they came out equal
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Working With the Agent

    *Pick one piece of AI output you did not accept as-is. What did it give you, what did you change, and how did you know? Point to the commit or the cell.*

    *If the agent got it right the first time: what did you do to verify that?*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8. Going Further

    *Take at least one step past the main task, in any direction, and use your agent as much as you like. It does not have to work. State what you tried, what you found, and where it is in this notebook.*
    """)
    return


if __name__ == "__main__":
    app.run()
