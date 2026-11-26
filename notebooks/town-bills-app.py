# /// script
# requires-python = ">=3.12,<3.15"
# dependencies = [
#     "marimo[sql]",
#     "duckdb",
#     "polars",
#     "pyarrow",
#     "altair",
#     "requests",
# ]
# ///
"""Town bills.
"""

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium", sql_output="polars")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    import altair as alt
    import duckdb
    import requests

    return alt, duckdb, requests


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # What Would This House Pay in Property Tax?

    The same single-family home pays a different tax bill in every Massachusetts town, because each town sets its own rate. Enter a price to compare all 351 towns at their FY2026 residential rates.
    """)
    return


@app.cell
def _(mo, requests):
    # The database. In your own app, point this at your project's database.
    _folder = mo.notebook_dir().parent / "data"
    _folder.mkdir(exist_ok=True)
    towns_database = _folder / "town-taxes.duckdb"
    if not towns_database.exists():
        _reply = requests.get(
            f"https://oim7510.github.io/data/combining/{towns_database.name}", timeout=60
        )
        _reply.raise_for_status()
        towns_database.write_bytes(_reply.content)
    return (towns_database,)


@app.cell
def _(duckdb, towns_database):
    # Every query goes through this function. A value that comes from the user
    # goes into params, one for each ?, and never into the SQL text.
    def ask(sql, params=None):
        with duckdb.connect(towns_database, read_only=True) as _con:
            return _con.sql(sql, params=params).pl()

    return (ask,)


@app.cell
def _():
    # One accent color for what the user picked; gray for everything else.
    ACCENT = "#0f766e"
    MUTED = "#a8b0b8"
    return ACCENT, MUTED


@app.cell
def _(ask, mo):
    # 1. The inputs: a price, and a county whose options come from the database.
    ALL_COUNTIES = "All counties"
    _counties = ask("SELECT DISTINCT county FROM towns ORDER BY county")["county"].to_list()
    price_input = mo.ui.number(
        start=100_000, stop=10_000_000, step=25_000, value=800_000, label="Price of the house ($)"
    )
    county_picker = mo.ui.dropdown(
        options=[ALL_COUNTIES, *_counties], value=ALL_COUNTIES, label="County"
    )
    mo.hstack([price_input, county_picker], justify="start", gap=2)
    return ALL_COUNTIES, county_picker, price_input


@app.cell
def _(ALL_COUNTIES, ask, county_picker, price_input):
    # 2. The query. It joins towns to tax_history to get each town's FY2026 rate,
    # and the price and the county go in as parameters.
    house_price = price_input.value or 800_000
    town_taxes = ask(
        """
        SELECT t.name AS town,
               t.county,
               round(? * h.residential_rate_per_thousand / 1000)::BIGINT AS tax_on_this_house,
               h.residential_rate_per_thousand AS rate_per_thousand,
               h.average_single_family_value_dollars AS typical_home_value,
               t.income_per_capita_dollars AS income_per_person,
               t.dor_code
        FROM towns AS t
        JOIN tax_history AS h ON h.dor_code = t.dor_code
        WHERE h.fiscal_year = 2026
          AND (? = ? OR t.county = ?)
        ORDER BY tax_on_this_house, town
        """,
        [house_price, county_picker.value, ALL_COUNTIES, county_picker.value],
    )
    return house_price, town_taxes


@app.cell
def _(ALL_COUNTIES, county_picker, house_price, mo, town_taxes):
    # 3. The answer first, in three numbers.
    _lowest = town_taxes.row(0, named=True)
    _highest = town_taxes.row(-1, named=True)
    _gap = _highest["tax_on_this_house"] - _lowest["tax_on_this_house"]
    _where = "Massachusetts" if county_picker.value == ALL_COUNTIES else f"{county_picker.value} County"
    mo.vstack([
        mo.md(f"### A \\${house_price:,.0f} house in {_where}"),
        mo.hstack(
            [
                mo.stat(f"${_lowest['tax_on_this_house']:,.0f}", label="Lowest tax a year", caption=_lowest["town"]),
                mo.stat(f"${_highest['tax_on_this_house']:,.0f}", label="Highest tax a year", caption=_highest["town"]),
                mo.stat(f"${_gap:,.0f}", label="Difference a year", caption=f"${10 * _gap:,.0f} over ten years"),
            ],
            widths="equal",
            gap=1,
        ),
    ])
    return


@app.cell
def _(ACCENT, MUTED, alt, chosen, mo, town_taxes):
    # 4. Where the rates come from: one dot for each town, and the chosen town
    # marked. Towns with expensive homes can collect what they need at a lower rate.
    _dots = (
        alt.Chart(town_taxes)
        .mark_circle(size=55, opacity=0.6, color=MUTED)
        .encode(
            x=alt.X("typical_home_value", title="Typical single-family home value", scale=alt.Scale(type="log", nice=False, padding=12), axis=alt.Axis(format="$,.0f", grid=False, values=[200_000, 300_000, 500_000, 1_000_000, 2_000_000, 3_000_000])),
            y=alt.Y("rate_per_thousand", title="Tax rate per $1,000 of value", axis=alt.Axis(gridOpacity=0.3)),
            tooltip=[
                alt.Tooltip("town"),
                alt.Tooltip("county"),
                alt.Tooltip("rate_per_thousand", title="rate per $1,000"),
                alt.Tooltip("typical_home_value", title="typical home", format="$,.0f"),
                alt.Tooltip("tax_on_this_house", title="tax on this house", format="$,.0f"),
            ],
        )
    )
    _picked = alt.Chart(town_taxes.filter(town_taxes["town"] == chosen["town"])).encode(
        x="typical_home_value", y="rate_per_thousand"
    )
    _chart = (
        (_dots + _picked.mark_circle(size=160, color=ACCENT) + _picked.mark_text(align="left", dx=10, fontSize=13, fontWeight=600, color=ACCENT).encode(text="town"))
        .properties(width="container", height=320, title="Each town's rate against what its homes are worth")
        .configure_view(stroke=None)
        .configure_title(anchor="start", fontSize=14, fontWeight=600)
    )
    mo.ui.altair_chart(_chart)
    return


@app.cell
def _(mo, town_taxes):
    # 5. Every town, cheapest first. Click a row to see its history below.
    COLUMN_LABELS = {
        "town": "Town",
        "county": "County",
        "tax_on_this_house": "Tax on this house",
        "rate_per_thousand": "Rate per $1,000",
        "typical_home_value": "Typical home value",
        "income_per_person": "Income per person",
    }
    town_table = mo.ui.table(
        town_taxes.drop("dor_code").rename(COLUMN_LABELS),
        selection="single",
        initial_selection=[0],
        page_size=10,
        format_mapping={
            "Tax on this house": "${:,.0f}",
            "Typical home value": "${:,.0f}",
            "Income per person": "${:,.0f}",
            "Rate per $1,000": "{:.2f}",
        },
        show_column_summaries=False,
        show_data_types=False,
        label="Click a town to see how its tax bill has changed",
    )
    town_table
    return (town_table,)


@app.cell
def _(town_table, town_taxes):
    # The town the user clicked, or the cheapest one before any click.
    _picked = town_table.value
    chosen_name = _picked.row(0, named=True)["Town"] if _picked.height else town_taxes["town"][0]
    chosen = town_taxes.filter(town_taxes["town"] == chosen_name).row(0, named=True)
    return (chosen,)


@app.cell
def _(ask, chosen):
    # 6. The chosen town's average single-family bill each year since FY2006, beside
    # the median town in its county. The second query is the join: tax_history
    # knows the town, towns knows the county.
    town_history = ask(
        """
        SELECT fiscal_year, average_single_family_bill_dollars AS bill, ? AS series
        FROM tax_history
        WHERE dor_code = ? AND fiscal_year BETWEEN 2006 AND 2026
          AND average_single_family_bill_dollars IS NOT NULL
        """,
        [chosen["town"], chosen["dor_code"]],
    )
    county_history = ask(
        """
        SELECT h.fiscal_year,
               round(median(h.average_single_family_bill_dollars))::BIGINT AS bill,
               'Median town in ' || t.county || ' County' AS series
        FROM tax_history AS h
        JOIN towns AS t ON t.dor_code = h.dor_code
        WHERE t.county = ? AND h.fiscal_year BETWEEN 2006 AND 2026
          AND h.average_single_family_bill_dollars IS NOT NULL
        GROUP BY h.fiscal_year, t.county
        """,
        [chosen["county"]],
    )
    return county_history, town_history


@app.cell
def _(ACCENT, MUTED, alt, chosen, county_history, house_price, mo, town_history):
    _both = town_history.vstack(county_history).sort("fiscal_year")
    _chart = (
        alt.Chart(_both)
        .mark_line(point=True, strokeWidth=2.5)
        .encode(
            x=alt.X("fiscal_year:O", title="Fiscal year", axis=alt.Axis(labelAngle=0, values=list(range(2006, 2027, 4)))),
            y=alt.Y("bill", title="Average single-family tax bill", axis=alt.Axis(format="$,.0f", gridOpacity=0.3)),
            color=alt.Color(
                "series",
                title=None,
                scale=alt.Scale(domain=[chosen["town"], county_history["series"][0]], range=[ACCENT, MUTED]),
                legend=alt.Legend(orient="top-left", labelLimit=400),
            ),
            tooltip=["series", "fiscal_year", alt.Tooltip("bill", format="$,.0f")],
        )
        .properties(width="container", height=260)
        .configure_view(stroke=None)
    )
    _first = town_history.row(0, named=True)
    _last = town_history.row(-1, named=True)
    mo.vstack([
        mo.md(f"### {chosen['town']}, {chosen['county']} County"),
        mo.hstack(
            [
                mo.stat(f"${chosen['tax_on_this_house']:,.0f}", label=f"Tax on your ${house_price:,.0f} house"),
                mo.stat(f"{chosen['rate_per_thousand']:.2f}", label="Rate per $1,000"),
                mo.stat(f"${chosen['typical_home_value']:,.0f}", label="Typical home value"),
                mo.stat(f"${chosen['income_per_person']:,.0f}", label="Income per person"),
            ],
            widths="equal",
            gap=1,
        ),
        mo.md(
            f"The average single-family bill in {chosen['town']} went from "
            f"**\\${_first['bill']:,.0f}** in FY{_first['fiscal_year']} to **\\${_last['bill']:,.0f}** in FY{_last['fiscal_year']}."
        ),
        mo.ui.altair_chart(_chart),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <small>Source: Massachusetts Department of Revenue, Division of Local Services, Municipal Databank, through the course API at oim.zhili.dev/ma. The tax on your house is its price times the town's FY2026 residential rate, as if it were assessed at that price. It leaves out exemptions some towns give owner-occupied homes, such as Boston's and Cambridge's residential exemption. Typical home value and bill are the averages for single-family homes; income is per person, for everyone who lives in the town.</small>
    """)
    return


if __name__ == "__main__":
    app.run()
