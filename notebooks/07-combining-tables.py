# /// script
# requires-python = ">=3.12,<3.15"
# dependencies = [
#     "marimo[sql]",
#     "duckdb",
#     "polars",
#     "pyarrow",
#     "requests",
#     "pymssql==2.4.5",
#     "python-dotenv",
# ]
# ///
"""Combining tables with JOIN.
"""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium", sql_output="polars")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    import os

    import duckdb
    import polars as pl
    import requests

    return duckdb, os, pl, requests


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Combining Tables with `JOIN`

    In this notebook we put tables back together to answer questions that no single table can answer. We start with the towns and their counties, then move to the Northwind orders, their lines, their products and their categories. Along the way we count the rows before and after each join, and we find the rows a join leaves out. After class, you will ask the same kind of question of a database on a server.

    | | |
    |---|---|
    | ✏️ | Your turn. Add cells with the **+** button |
    | 🚀 | This week's work |

    For a written answer, add a cell under the question, open the cell's **⋯** menu and choose **Convert to Markdown**.

    Every ✏️ is part of this week's work. The **Going further** at the end of an exercise is optional; try it once the rest is done.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Work with your agent the same way as in notebook 6.** Try it yourself first, or write the steps in words. Then ask your agent, ask it to explain any line you could not have written, and ask which concepts its answer used. Do exercise A by hand.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **The data.** This notebook uses two ready-made databases from the course website. `combining-towns.duckdb` holds the same towns and counties as notebook 6, and `combining-northwind.duckdb` holds the Northwind tables, the warehouse the SQL handbook uses. The tables have no keys. The next cell downloads both files into your `data` folder the first time you run it.
    """)
    return


@app.cell
def _(mo, requests):
    _folder = mo.notebook_dir().parent / "data"
    _folder.mkdir(exist_ok=True)
    towns_database = _folder / "combining-towns.duckdb"
    northwind_database = _folder / "combining-northwind.duckdb"
    for _file in [towns_database, northwind_database]:
        if not _file.exists():
            _reply = requests.get(
                f"https://oim7510.github.io/data/combining/{_file.name}", timeout=60
            )
            _reply.raise_for_status()
            _file.write_bytes(_reply.content)
    towns_database.name, northwind_database.name
    return northwind_database, towns_database


@app.cell
def _(duckdb):
    def ask(database, sql):
        with duckdb.connect(database, read_only=True) as _con:
            return _con.sql(sql).pl()

    return (ask,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **What is in the database.** Before we write a query, it is a good idea to ask the database which tables and columns it has, because an ERD drawn somewhere else can use other names. Both databases you query in this notebook, DuckDB here and SQL Server in section 5, keep that list in `information_schema`, a set of tables we can read with `SELECT`. The following query lists the tables in the Northwind database.
    """)
    return


@app.cell
def _(ask, northwind_database):
    ask(northwind_database, """
        SELECT table_name FROM information_schema.tables ORDER BY table_name
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    There are 11 tables. The next query lists the columns of one of them, `order_details`, with their types.
    """)
    return


@app.cell
def _(ask, northwind_database):
    ask(northwind_database, """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'order_details'
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    These are the names to use in a query. Your agent cannot see the database, so paste them in when you ask it for one.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 1. Putting Tables Back Together

    The `towns` table keeps only the name of each town's county. To see a town beside its county's population, we have to combine `towns` with `counties`. `JOIN` names the second table, and `ON` specifies which rows go together, here a town and the county it names. The following query lists the five largest towns with the population of their counties.
    """)
    return


@app.cell
def _(ask, towns_database):
    ask(towns_database, """
        SELECT t.name, t.county, t.population, c.population AS county_population
        FROM towns AS t
        JOIN counties AS c ON t.county = c.name
        ORDER BY t.population DESC
        LIMIT 5
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Boston has 673,458 people, and Suffolk County, where it is, has 793,144. In this query, `t` and `c` are short names for the two tables, called **table aliases**. They make it clear that `t.population` is a town's population and `c.population` is a county's.

    On TV shows: [The four shows, with `JOIN`](https://oim-shows.zhili.dev/queries#join-inner)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **A column can be computed.** `SELECT` accepts arithmetic on columns, `round(x, 1)` rounds a number to one decimal place, and `AS` gives the result a name. This query computes each town's income per person for one month:
    """)
    return


@app.cell
def _(ask, towns_database):
    ask(towns_database, """
        SELECT name, income_per_capita_dollars,
               round(income_per_capita_dollars / 12, 1) AS monthly_income
        FROM towns
        ORDER BY monthly_income DESC
        LIMIT 3
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Sherborn is first, with an income per person of 352,250 dollars a year, or about 29,354 a month.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ✏️ A · Towns and Their Counties

    **No agent for this one**, and no code completion either. When the editor suggests code in grey as you type, press `Esc` and keep typing your own.

    1. Copy the first query of this section into a cell of your own, remove its `LIMIT`, and count the rows it returns. In a markdown cell under it, explain why the count is the same as the number of rows in `towns`. *Check yourself: 351.*
    2. Add a column with each town's share of its county's population, in percent and rounded to one decimal place, and list the five largest shares. *Check yourself: Nantucket 100.0, Boston 84.9, Pittsfield 33.5, Springfield 33.4, Oak Bluffs 25.7.*
    3. In the same markdown cell, explain why Nantucket's share is exactly 100.

    **Going further.** For each county, find the town with the largest share of its people.
    """)
    return


@app.cell
def _(ask, towns_database):
    towns_with_counties = ask(towns_database, """
        SELECT t.name, t.county, t.population, c.population AS county_population
        FROM towns AS t
        JOIN counties AS c ON t.county = c.name
        ORDER BY t.population DESC
    """)
    print(f"A: The join returns {towns_with_counties.height} towns; no towns are left out.")
    towns_with_counties
    return


@app.cell
def _(ask, towns_database):
    largest_population_shares = ask(towns_database, """
        SELECT t.name, t.county,
               round(100.0 * t.population / c.population, 1) AS population_percent
        FROM towns AS t
        JOIN counties AS c ON t.county = c.name
        ORDER BY population_percent DESC, t.name
        LIMIT 5
    """)
    print("A: Five largest town shares:", largest_population_shares.rows())
    largest_population_shares
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **A — Explanation.** Each of the 351 towns matches exactly one county, so the
    join returns 351 rows. Nantucket is the only town in its county, so its town
    and county populations are equal and its share is 100%.

    `AS t` and `AS c` give the tables short names; `ON` matches each town to its
    county; `round(100.0 * t.population / c.population, 1)` calculates the share
    as a percentage rounded to one decimal place. `LIMIT 5` displays five of
    the 351 towns and leaves 346 out of that display.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 2. What a Join Leaves Out

    `JOIN` keeps only the rows that have a match in the other table. If a county has no matching town, that county is not in the result, and there is no error message or warning.

    To find those counties, we can use `LEFT JOIN`, which keeps every row of the table on the left, here `counties`. If a county has no matching town, the columns from `towns` contain `NULL` in that row, and `WHERE t.name IS NULL` keeps exactly those rows. The following query finds the counties with no town whose average bill is over $15,000.
    """)
    return


@app.cell
def _(ask, towns_database):
    ask(towns_database, """
        SELECT c.name
        FROM counties AS c
        LEFT JOIN towns AS t
            ON t.county = c.name AND t.average_single_family_bill_dollars > 15000
        WHERE t.name IS NULL
        ORDER BY c.name
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The result has 10 of the 14 counties. Each of the other four has at least one town with a bill over $15,000.

    The bill condition is in `ON`, which decides what counts as a match. If we move it to `WHERE`, the query runs without an error, but the result is empty. `WHERE` keeps rows after the join, and for a county with no such town the bill is `NULL`, which is not over $15,000.

    A query like this one, which finds the rows in one table that have no match in another, is called an **anti join**. When you write a `JOIN`, it is a good idea to check which rows it left out, and an anti join is one way to do that.

    `RIGHT JOIN` keeps every row of the table on the right, and `FULL JOIN` keeps every row of both tables. For `towns` and `counties`, `JOIN`, `LEFT JOIN`, `RIGHT JOIN` and `FULL JOIN` all return the same 351 rows, because every town names a county in `counties` and every county has towns. With a few shows from the TV show database, each join returns a different number of rows.

    On TV shows:

    - [The four shows, with `LEFT JOIN`](https://oim-shows.zhili.dev/queries#join-left)
    - [The four shows, with `RIGHT JOIN`](https://oim-shows.zhili.dev/queries#join-right)
    - [The four shows, with `FULL JOIN`](https://oim-shows.zhili.dev/queries#join-full)
    - [The Office shows with no rating](https://oim-shows.zhili.dev/queries#anti-join)
    - [ON and WHERE](https://oim-shows.zhili.dev/queries#on-and-where)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ✏️ B · The Territories Nobody Covers

    In Northwind, `employee_territories` pairs each employee with the territories they cover. Find the territories in `territories` that nobody covers, using `LEFT JOIN` and `IS NULL`.

    *Check yourself: four territories, Columbia, Bentonville, Dallas and Austin.*

    **Going further.** List the employees with the number of territories each covers, and check that the counts add up to the rows of `employee_territories`. Then find the same four territories with `WHERE NOT EXISTS (...)`.
    """)
    return


@app.cell
def _(ask, northwind_database):
    uncovered_territories = ask(northwind_database, """
        SELECT t.TerritoryID, t.TerritoryDescription
        FROM territories AS t
        LEFT JOIN employee_territories AS e ON e.TerritoryID = t.TerritoryID
        WHERE e.TerritoryID IS NULL
        ORDER BY t.TerritoryDescription
    """)
    print(f"B: {uncovered_territories.height} territories have no employee.")
    print("B: Uncovered territories:", uncovered_territories.rows())
    uncovered_territories
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **B — Explanation.** `LEFT JOIN` keeps every territory, and `IS NULL` keeps
    only those with no matching employee assignment; no source rows are changed.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 3. When a Join Repeats Rows

    In Northwind, an order can have many lines, and each line is a row in `order_details`. When we join `orders` to `order_details`, the result has one row for each line. An order with three lines appears three times, and its `Freight` value is repeated in each of those rows. To see the effect, we can count the rows in `orders`, in `order_details`, and in the result of the join.
    """)
    return


@app.cell
def _(ask, northwind_database):
    ask(northwind_database, """
        SELECT
            (SELECT count(*) FROM orders) AS orders,
            (SELECT count(*) FROM order_details) AS order_lines,
            (SELECT count(*)
             FROM orders AS o
             JOIN order_details AS d ON d.OrderID = o.OrderID) AS joined
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    There are 16,282 orders and 609,283 order lines. The join has as many rows as `order_details`, one for each line.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    If we add up `Freight` after the join, each order's freight is counted once for each of its lines, so the total is too big. The following query computes the total from `orders` and the total after the join.
    """)
    return


@app.cell
def _(ask, northwind_database):
    ask(northwind_database, """
        SELECT
            (SELECT sum(Freight) FROM orders) AS freight,
            (SELECT sum(o.Freight)
             FROM orders AS o
             JOIN order_details AS d ON d.OrderID = o.OrderID) AS freight_after_the_join
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The total from `orders` is 4,047,470.50. After the join, it is 206,911,676.00, about 51 times as much.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Check the key before you join.** Before a join, it is a good idea to count the values that appear more than once in the column you join on. The following query does that for `OrderID` in both tables.
    """)
    return


@app.cell
def _(ask, northwind_database):
    ask(northwind_database, """
        SELECT
            (SELECT count(*) FROM (SELECT OrderID FROM orders GROUP BY OrderID HAVING count(*) > 1)) AS repeated_in_orders,
            (SELECT count(*) FROM (SELECT OrderID FROM order_details GROUP BY OrderID HAVING count(*) > 1)) AS repeated_in_order_details
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    In `orders`, no `OrderID` appears more than once. In `order_details`, 15,948 of them do, so a column of `orders` is copied once for each line of its order.

    On TV shows: [Rows before and after a join](https://oim-shows.zhili.dev/queries#rows-before-and-after) and [Checking the key](https://oim-shows.zhili.dev/queries#checking-the-key)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ✏️ C · Freight by Country

    Compute the total freight for each `ShipCountry`, with the largest first, counting each order's freight once.

    *Check yourself: the USA first, with 573,251.00, and the 21 countries add up to 4,047,470.50, the total in `orders`.*

    **Going further.** Build one row per order with its freight and its number of lines, by counting the lines first and joining the counts to `orders`.
    """)
    return


@app.cell
def _(ask, northwind_database):
    freight_by_country = ask(northwind_database, """
        SELECT ShipCountry, count(*) AS orders, sum(Freight) AS total_freight
        FROM orders
        GROUP BY ShipCountry
        ORDER BY total_freight DESC
    """)
    freight_check = ask(northwind_database, "SELECT sum(Freight) AS freight FROM orders")
    print(f"C: {freight_by_country.height} countries; grouped freight = {freight_by_country['total_freight'].sum():,.2f}.")
    print(f"C: Freight from orders alone = {freight_check['freight'][0]:,.2f}.")
    freight_by_country
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **C — Explanation.** `GROUP BY ShipCountry` makes one group per country, and
    `sum(Freight)` adds each order's freight once because this query uses only
    `orders`; all orders are included.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 4. A Chain of Joins

    A line in `order_details` has a `ProductID`, and a product in `products` has a `CategoryID`. So to compute revenue by category, we need three tables: `order_details`, `products` and `categories`. Each `JOIN` adds one table, with its own `ON`.

    On TV shows: [A chain of joins](https://oim-shows.zhili.dev/queries#chain-of-joins)

    ## ✏️ D · Revenue by Category

    A line's revenue is `UnitPrice * Quantity * (1 - Discount)`. Compute the total revenue for each category, for the orders shipped to the USA, with the largest first. `ShipCountry` is in `orders`, so this query needs a fourth table. Then check that the categories add up to the USA's revenue computed from `orders` and `order_details` alone.

    *Check yourself: Beverages first, with about 13,375,939, and all eight, added before rounding, give 63,856,337.63.*

    **Going further.** Compute revenue by category for each year, and find the category that grew the most.
    """)
    return


@app.cell
def _(ask, northwind_database):
    usa_category_revenue = ask(northwind_database, """
        SELECT c.CategoryName,
               sum(d.UnitPrice * d.Quantity * (1 - d.Discount)) AS revenue
        FROM orders AS o
        JOIN order_details AS d ON d.OrderID = o.OrderID
        JOIN products AS p ON p.ProductID = d.ProductID
        JOIN categories AS c ON c.CategoryID = p.CategoryID
        WHERE o.ShipCountry = 'USA'
        GROUP BY c.CategoryName
        ORDER BY revenue DESC
    """)
    usa_revenue_check = ask(northwind_database, """
        SELECT sum(d.UnitPrice * d.Quantity * (1 - d.Discount)) AS revenue
        FROM orders AS o
        JOIN order_details AS d ON d.OrderID = o.OrderID
        WHERE o.ShipCountry = 'USA'
    """)
    usa_order_counts = ask(northwind_database, """
        SELECT count(*) AS all_orders,
               sum(CASE WHEN ShipCountry = 'USA' THEN 1 ELSE 0 END) AS usa_orders
        FROM orders
    """)
    print(f"D: {usa_category_revenue.height} categories; category revenue = {usa_category_revenue['revenue'].sum():,.2f}.")
    print(f"D: Revenue from orders and lines alone = {usa_revenue_check['revenue'][0]:,.2f}.")
    print(f"D: Kept {usa_order_counts['usa_orders'][0]:,} USA orders; excluded {usa_order_counts['all_orders'][0] - usa_order_counts['usa_orders'][0]:,} other orders.")
    usa_category_revenue
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **D — Explanation.** The joins connect each order line to its order, product
    and category; `UnitPrice * Quantity * (1 - Discount)` calculates revenue
    after the discount. The second query checks the total using just orders and
    order lines, and both totals are added before rounding for display.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 5. After Class: The Same Joins on a Server

    So far every database we have used is a file on your computer. Most companies keep theirs on a server, and you connect to it over the network. Babson runs one with **AdventureWorks**, a bicycle company's sales database, on Microsoft SQL Server. The version of SQL that SQL Server uses is called **T-SQL**. It differs from DuckDB's in small ways: tables are inside schemas, as in `Sales.SalesOrderHeader`, and you write `TOP 5` after `SELECT` where DuckDB writes `LIMIT 5` at the end.

    **Set it up once:**

    1. In a Terminal in the root folder of your repository, run `uv add "pymssql==2.4.5" python-dotenv`. Keep the version number: this one also installs on Apple Silicon Macs with macOS 14, where the newest does not. If the install fails on an older Mac, email me.
    2. Open `.gitignore` in the root folder and check that it lists `.env`. If it does not, add the line `.env` and commit that first. Your repository is public, and a password committed once stays in its history. The cell below does not connect until `.gitignore` lists `.env`.
    3. Make a file named exactly `.env` in the root folder, in VS Code. Copy into it the four lines on the **Connecting to SQL Server** page, in the Class Information module on Canvas. If you change `.env` later, run your query cell again: marimo does not notice a change to a file on its own.
    4. Before every commit, look at the list of changed files in GitHub Desktop. If `.env` is in the list, it is not ignored: do not commit.

    The cell below reads the server, the login and the password from `.env`, so they never appear in the notebook. It defines `ask_server`, which works like `ask` but takes only the query.
    """)
    return


@app.cell
def _(mo, os, pl):
    from dotenv import load_dotenv

    def ask_server(sql):
        root = mo.notebook_dir().parent
        gitignore = root / ".gitignore"
        if not gitignore.exists() or ".env" not in [line.strip() for line in gitignore.read_text().splitlines()]:
            return "Add the line .env to .gitignore in the root folder and commit it, as step 2 describes."
        load_dotenv(root / ".env", override=True)
        if not os.environ.get("ATIC_PASSWORD"):
            return "Copy the four lines from the Canvas page into .env first, as step 3 describes."
        try:
            import pymssql
        except ImportError:
            return 'Run uv add "pymssql==2.4.5" python-dotenv before connecting to the server.'
        with pymssql.connect(
            server=os.environ["ATIC_SERVER"],
            user=os.environ["ATIC_USER"],
            password=os.environ["ATIC_PASSWORD"],
            database=os.environ["ATIC_DATABASE"],
            login_timeout=20,
        ) as _con:
            _cursor = _con.cursor()
            _cursor.execute(sql)
            _columns = [_column[0] for _column in _cursor.description]
            return pl.DataFrame(_cursor.fetchall(), schema=_columns, orient="row")

    ask_server("SELECT TOP 5 SalesOrderID, OrderDate, Freight FROM Sales.SalesOrderHeader ORDER BY SalesOrderID")
    return (ask_server,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    If the connection works, the cell shows the first five orders in `Sales.SalesOrderHeader`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ✏️ E · AdventureWorks on the Server

    Use `ask_server`, and write T-SQL.

    1. Count the rows of `Sales.SalesOrderHeader`, of `Sales.SalesOrderDetail`, and of the two joined on `SalesOrderID`. Explain in a markdown cell why the join has exactly as many rows as one of them. *Check yourself: 31,465, 121,317 and 121,317.*
    2. Compute the total `Freight` in `Sales.SalesOrderHeader`, and the same total after the join. *Check yourself: 3,183,430.25, and 78,690,398.20 after the join.*
    3. Find the customers in `Sales.Customer` who never placed an order, and the products in `Production.Product` that never sold. *Check yourself: 701 customers and 238 products.*

    **Going further.** Answer one question of your own about AdventureWorks that needs three tables, and check it against a total you can get from one of them.
    """)
    return


@app.cell
def _(ask_server):
    adventureworks_counts = ask_server("""
        SELECT
            (SELECT count(*) FROM Sales.SalesOrderHeader) AS orders,
            (SELECT count(*) FROM Sales.SalesOrderDetail) AS order_lines,
            (SELECT count(*)
             FROM Sales.SalesOrderHeader AS h
             JOIN Sales.SalesOrderDetail AS d
                 ON d.SalesOrderID = h.SalesOrderID) AS joined_rows
    """)
    print("E: Order and join counts:")
    if isinstance(adventureworks_counts, str):
        print(adventureworks_counts)
    else:
        print(adventureworks_counts.rows())
    adventureworks_counts
    return


@app.cell
def _(ask_server):
    adventureworks_freight = ask_server("""
        SELECT
            (SELECT sum(Freight) FROM Sales.SalesOrderHeader) AS freight_once,
            (SELECT sum(h.Freight)
             FROM Sales.SalesOrderHeader AS h
             JOIN Sales.SalesOrderDetail AS d
                 ON d.SalesOrderID = h.SalesOrderID) AS freight_after_join
    """)
    print("E: Freight before and after joining:")
    if isinstance(adventureworks_freight, str):
        print(adventureworks_freight)
    else:
        print(adventureworks_freight.rows())
    adventureworks_freight
    return


@app.cell
def _(ask_server):
    customers_without_orders = ask_server("""
        SELECT c.CustomerID
        FROM Sales.Customer AS c
        LEFT JOIN Sales.SalesOrderHeader AS h ON h.CustomerID = c.CustomerID
        WHERE h.SalesOrderID IS NULL
        ORDER BY c.CustomerID
    """)
    if isinstance(customers_without_orders, str):
        print(customers_without_orders)
    else:
        print(f"E: {customers_without_orders.height} customers never placed an order.")
    customers_without_orders
    return


@app.cell
def _(ask_server):
    products_without_sales = ask_server("""
        SELECT p.ProductID, p.Name
        FROM Production.Product AS p
        LEFT JOIN Sales.SalesOrderDetail AS d ON d.ProductID = p.ProductID
        WHERE d.SalesOrderDetailID IS NULL
        ORDER BY p.ProductID
    """)
    if isinstance(products_without_sales, str):
        print(products_without_sales)
    else:
        print(f"E: {products_without_sales.height} products never sold.")
    products_without_sales
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **E — Explanation.** Each order line matches one order header, so the join
    has as many rows as the detail table. Adding freight after that join repeats
    each order's freight once for every line, which inflates the total.

    `LEFT JOIN` with `IS NULL` finds customers and products without a match;
    `isinstance(..., str)` checks whether the helper returned setup instructions
    instead of a result table, `.rows()` supplies plain rows for printing, and
    `.height` counts result rows. These queries
    read data and do not change any server rows. Run them after setting up `.env`
    to see the actual counts and freight totals.

    The helper imports `pymssql` only when credentials are present; `try` and
    `except ImportError` show the installation command if that package is missing.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 6. Practice for the Database Project

    The questions in Part B of the [database project](https://oim7510.github.io/assignments/database-project/) use a few patterns that the sections above do not show on their own. The exercises below practice them on Northwind, and each one names the project questions that are like it.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ✏️ F · Every Territory With Its Count

    For each territory, count the employees who cover it, and keep the territories that nobody covers in the result, with 0.

    A common error is to count with `count(*)`. After a `LEFT JOIN`, a territory with no match still has one row, so `count(*)` gives it 1. Count a column from `employee_territories` instead, because `count` skips `NULL`.

    *Check yourself: 53 rows. Four of them have 0, and the counts add up to 49, the number of rows in `employee_territories`.*

    **In the project:** like scenario B's question 2 and scenario D's question 4.

    **Going further.** For each region, the number of territories and the number of them that somebody covers.
    """)
    return


@app.cell
def _(ask, northwind_database):
    territory_employee_counts = ask(northwind_database, """
        SELECT t.TerritoryID, t.TerritoryDescription,
               count(e.EmployeeID) AS employee_count
        FROM territories AS t
        LEFT JOIN employee_territories AS e ON e.TerritoryID = t.TerritoryID
        GROUP BY t.TerritoryID, t.TerritoryDescription
        ORDER BY employee_count, t.TerritoryDescription
    """)
    territory_assignment_check = ask(northwind_database, """
        SELECT count(*) AS assignments FROM employee_territories
    """)
    territories_with_zero = 0
    for territory_row in territory_employee_counts.iter_rows(named=True):
        if territory_row["employee_count"] == 0:
            territories_with_zero += 1
    print(f"F: {territory_employee_counts.height} territories; {territories_with_zero} have 0 employees; no territories excluded.")
    print(f"F: Employee counts add to {territory_employee_counts['employee_count'].sum()}; assignment table has {territory_assignment_check['assignments'][0]} rows.")
    territory_employee_counts
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **F - Explanation.** `LEFT JOIN` keeps all territories, including uncovered
    ones; `count(e.EmployeeID)` counts only matching employee assignments and
    ignores the empty (`NULL`) values, so uncovered territories receive 0.
    `GROUP BY` produces one row per territory, and `ORDER BY` lists the zero
    counts first. `.iter_rows(named=True)` lets the loop read each row by its
    column names; the loop counts how many territories have no employees.
    The separate query counts assignments directly to check the total.
    No source values or types are changed.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ✏️ G · Orders and Territories for Each Employee

    Build one row per employee with their number of orders and their number of territories. Then check each count against counting it on its own, from `orders` alone and from `employee_territories` alone.

    *Check yourself: Robert has 1,789 orders and 10 territories. If you join both tables to `employees` in one query and count the rows, Robert gets 17,890, one row for each pair of an order and a territory.*

    **In the project:** like scenario A's question 6 and scenario D's question 6, and the note under scenario C's questions.

    **Going further.** Add each employee's total freight, and check it against `orders` alone.
    """)
    return


@app.cell
def _(ask, northwind_database):
    employee_activity = ask(northwind_database, """
        SELECT e.EmployeeID, e.FirstName, e.LastName,
               coalesce(o.order_count, 0) AS order_count,
               coalesce(t.territory_count, 0) AS territory_count
        FROM employees AS e
        LEFT JOIN (
            SELECT EmployeeID, count(*) AS order_count
            FROM orders
            GROUP BY EmployeeID
        ) AS o ON o.EmployeeID = e.EmployeeID
        LEFT JOIN (
            SELECT EmployeeID, count(*) AS territory_count
            FROM employee_territories
            GROUP BY EmployeeID
        ) AS t ON t.EmployeeID = e.EmployeeID
        ORDER BY e.EmployeeID
    """)
    orders_by_employee_check = ask(northwind_database, """
        SELECT EmployeeID, count(*) AS order_count
        FROM orders GROUP BY EmployeeID
    """)
    territories_by_employee_check = ask(northwind_database, """
        SELECT EmployeeID, count(*) AS territory_count
        FROM employee_territories GROUP BY EmployeeID
    """)
    employee_order_lookup = {}
    for order_check_row in orders_by_employee_check.iter_rows(named=True):
        employee_order_lookup[order_check_row["EmployeeID"]] = order_check_row["order_count"]
    employee_territory_lookup = {}
    for territory_check_row in territories_by_employee_check.iter_rows(named=True):
        employee_territory_lookup[territory_check_row["EmployeeID"]] = territory_check_row["territory_count"]
    employee_count_mismatches = 0
    employee_zero_order_counts = 0
    employee_zero_territory_counts = 0
    for activity_row in employee_activity.iter_rows(named=True):
        if activity_row["EmployeeID"] not in employee_order_lookup:
            employee_zero_order_counts += 1
        if activity_row["EmployeeID"] not in employee_territory_lookup:
            employee_zero_territory_counts += 1
        if (activity_row["order_count"] != employee_order_lookup.get(activity_row["EmployeeID"], 0)
                or activity_row["territory_count"] != employee_territory_lookup.get(activity_row["EmployeeID"], 0)):
            employee_count_mismatches += 1
        if activity_row["FirstName"] == "Robert":
            print(f"G: Robert has {activity_row['order_count']:,} orders and {activity_row['territory_count']} territories.")
    print(f"G: Checked every count for {employee_activity.height} employees; {employee_count_mismatches} mismatches; no employees excluded.")
    print(f"G: Filled {employee_zero_order_counts} missing order counts and {employee_zero_territory_counts} missing territory counts with 0 in the result.")
    print(f"G: Total orders = {employee_activity['order_count'].sum():,}; total territory assignments = {employee_activity['territory_count'].sum()}.")
    employee_activity
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **G - Explanation.** Each query inside parentheses counts one table by
    employee before the joins, so an employee's orders cannot multiply their
    territory assignments. `coalesce(value, 0)` supplies 0 when an employee has
    no matching count; it does not change the source tables. `LEFT JOIN` keeps
    every employee. The two separate queries check each count without joining
    tables. The loops build dictionaries keyed by employee ID, then compare
    both counts for every employee; `.get(ID, 0)` supplies 0 for a missing ID.
    `!=` means unequal and `or` flags a row if either count differs.
    The Robert line provides the requested spot check.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ✏️ H · The Last 90 Days

    The last order in Northwind was placed on 2023-10-28. For each shipper, compute the number of orders and the total freight in the 90 days before that date, with the most orders first. In `orders`, the shipper is `ShipVia`, which holds a `ShipperID`. To keep the orders of those 90 days, use `WHERE OrderDate >= DATE '2023-10-28' - INTERVAL 90 DAY`. [Chapter B, §12](https://oim7510.github.io/handbooks/sql/02-asking-one-table/#12-dates-truncating-differencing-grouping-by-month) of the SQL handbook has more on dates.

    *Check yourself: 328 orders in all, and United Package first, with 115 orders and 31,827.75 in freight.*

    **In the project:** like scenario A's question 4, scenario B's question 1 and scenario C's question 7.

    **Going further.** The number of orders for each shipper in each month of 2023.
    """)
    return


@app.cell
def _(ask, northwind_database):
    recent_shipper_totals = ask(northwind_database, """
        SELECT s.CompanyName, count(*) AS order_count,
               sum(o.Freight) AS total_freight
        FROM orders AS o
        JOIN shippers AS s ON s.ShipperID = o.ShipVia
        WHERE o.OrderDate >= DATE '2023-10-28' - INTERVAL 90 DAY
        GROUP BY s.ShipperID, s.CompanyName
        ORDER BY order_count DESC, s.CompanyName
    """)
    recent_orders_check = ask(northwind_database, """
        SELECT count(*) AS order_count, sum(Freight) AS total_freight,
               (SELECT count(*) FROM orders) AS all_orders
        FROM orders
        WHERE OrderDate >= DATE '2023-10-28' - INTERVAL 90 DAY
    """)
    print(f"H: Shipper counts add to {recent_shipper_totals['order_count'].sum()} orders; orders alone give {recent_orders_check['order_count'][0]}.")
    print(f"H: Shipper freight = {recent_shipper_totals['total_freight'].sum():,.2f}; orders alone = {recent_orders_check['total_freight'][0]:,.2f}.")
    print(f"H: Date filter excludes {recent_orders_check['all_orders'][0] - recent_orders_check['order_count'][0]:,} orders.")
    print("H: Shipper results:", recent_shipper_totals.rows())
    recent_shipper_totals
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **H - Explanation.** `ShipVia` matches an order to its shipper's ID;
    the date condition keeps orders on or after July 30, 2023, using the
    cutoff specified in the question. `DATE` reads the written cutoff as a date,
    and `INTERVAL 90 DAY` subtracts 90 days; neither changes stored values.
    Each order joins to one shipper, so freight is counted once. The separate
    query checks the order count and freight directly from `orders`; the printed
    exclusion count reports orders outside the date range.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ✏️ I · Categories Above the Average

    Compute the revenue of each category, then keep only the categories whose revenue is above the average of all the category totals. This needs a query inside another query, called a **subquery**, which [chapter C, §21](https://oim7510.github.io/handbooks/sql/03-more-than-one-table/#21-subqueries) of the SQL handbook explains.

    *Check yourself: four categories, Beverages, Confections, Meat/Poultry and Dairy Products. The average is about 56,048,329.*

    **In the project:** like scenario A's question 4 and scenario C's question 3.

    **Going further.** The products whose revenue is above the average of their own category.
    """)
    return


@app.cell
def _(ask, northwind_database):
    above_average_categories = ask(northwind_database, """
        WITH category_totals AS (
            SELECT c.CategoryID, c.CategoryName,
                   sum(d.UnitPrice * d.Quantity * (1 - d.Discount)) AS revenue
            FROM categories AS c
            JOIN products AS p ON p.CategoryID = c.CategoryID
            JOIN order_details AS d ON d.ProductID = p.ProductID
            GROUP BY c.CategoryID, c.CategoryName
        )
        SELECT CategoryName, revenue,
               (SELECT avg(revenue) FROM category_totals) AS average_category_revenue,
               (SELECT count(*) FROM category_totals) AS categories_before_filter
        FROM category_totals
        WHERE revenue > (SELECT avg(revenue) FROM category_totals)
        ORDER BY revenue DESC
    """)
    print(f"I: {above_average_categories.height} categories exceed the average revenue of {above_average_categories['average_category_revenue'][0]:,.2f}.")
    print(f"I: Excluded {above_average_categories['categories_before_filter'][0] - above_average_categories.height} categories at or below the average.")
    print("I: Above-average categories:", above_average_categories['CategoryName'].to_list())
    above_average_categories
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **I - Explanation.** `WITH category_totals AS (...)` gives the first query
    a temporary name for use within this statement; it creates no stored table.
    The joins connect each line to its product and category, and the revenue
    formula subtracts its discount before adding the category's sales.
    `SELECT avg(revenue) FROM category_totals` averages the category totals,
    and the outer `WHERE` keeps only totals greater than that average.
    `.to_list()` supplies the category names as a Python list for printing.
    The output reports the number of categories excluded by the filter;
    no source rows or types are changed.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 🚀 This Week's Work

    1. **What is due is listed under *Before next session* in the post-class notes.** I post them on the session page after each class, with the sections we reached, and the checkpoint on Canvas lists the same items.
    2. **[The database project](https://oim7510.github.io/assignments/database-project/)**, Part B, due Monday 11/16
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Self-check:**

    - [ ] I can join two tables with `JOIN` and `ON`, and explain how many rows come out
    - [ ] I can find the rows a join leaves out, with `LEFT JOIN` and `IS NULL`
    - [ ] I can check a key for repeats before I join on it, and explain why a total grows after a join
    - [ ] I can join three tables and check the result against a total I know
    - [ ] I can connect to a database on a server and ask it the same questions in T-SQL
    """)
    return


if __name__ == "__main__":
    app.run()
