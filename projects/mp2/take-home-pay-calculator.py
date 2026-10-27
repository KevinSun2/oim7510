import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import requests
    import json
    from pathlib import Path

    return Path, json, mo, requests


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Take-Home Pay Calculator

    ## 1. The Question

    Who would use this, and what decision does it help them make?

    For people that will be taking a job in a different state and trying to find out their income after state taxes. This tool should help them plan and budget as needed together with the financial planning tool created for mp1.

    ## 2. My Plan Before AI

    Fetching state tax rates, federal tax rates, social security, and medicare is a must. Then fetching the paycheck. We then apply social security and medicare withholdings, subtract the pretax deductibles from the gross salary, then apply the federal and state tax brackets, , and finally subtract any post-tax deductions to arrive at the net take-home pay.

    **To complete yourself:** the assignment also requests at least five lines of steps,
    function inputs and outputs, API addresses, record completeness, and two numbers to check.
    Keep your original plan and describe later additions honestly.

    ## 3. Inputs

    Money inputs are annual dollars except the 401(k) percentage.
    These are fictional examples, not personal financial information.
    This version covers a full year working and living in Virginia, one wage earner
    under 50, standard deductions, no dependents or special credits.
    Filing status can be `single`, `married` (joint), or `head` (head of household).
    Health insurance and HSA contributions must be eligible pretax payroll deductions.
    A move during the year can require a separate part-year state calculation.
    """)
    return


@app.cell
def _():
    salary = 125000
    filing_status = "single"
    tax_year = 2026
    state_name = "Virginia"
    retirement_percent = 8
    health_insurance = 0
    hsa_contribution = 0
    post_tax_deductions = 0
    monthly_expenses = 3000  # Going further: a fictional monthly budget.
    api_base = "https://paysums.com/api/v1"
    return (
        api_base,
        filing_status,
        health_insurance,
        hsa_contribution,
        monthly_expenses,
        post_tax_deductions,
        retirement_percent,
        salary,
        state_name,
        tax_year,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. The Work

    Source: [PaySums API](https://paysums.com/api/).
    The tables contain one federal record and all supplied state records; there is no pagination.
    The selected state record supplies the code used in the paycheck request.
    """)
    return


@app.cell
def _(requests):
    def fetch_tax_tables(base_url, requested_year):
        response = requests.get(base_url + "/tables/us", timeout=30)
        response.raise_for_status()
        data = response.json()
        if data["year"] != requested_year:
            raise ValueError("Choose the year supplied by the current tables: " + str(data["year"]))
        records = [{"kind": "federal", "code": "US", "year": data["year"], "rules": data["federal"]}]
        for code, rules in data["states"].items():
            records.append({"kind": "state", "code": code, "year": data["year"], "rules": rules})
        print(f"Tax records fetched: {len(records)}; expected: {1 + len(data['states'])}.")
        assert len(records) == 1 + len(data["states"]), "Missing tax records."
        return records

    def fetch_paycheck(base_url, code, annual_salary, status, year, retirement_pct, health, hsa):
        parameters = {
            "country": "US", "state": code, "amount": annual_salary,
            "period": "annual", "filing": status, "taxYear": year,
            "k401Pct": retirement_pct, "health": health, "hsa": hsa,
            "dependents": 0,
        }
        response = requests.get(base_url + "/paycheck", params=parameters, timeout=30)
        response.raise_for_status()
        result = response.json()["result"]
        if result["stateCode"] != code or result["year"] != year:
            raise ValueError("The API returned a different state or year.")
        return [result]

    return fetch_paycheck, fetch_tax_tables


@app.cell
def _(api_base, fetch_tax_tables, state_name, tax_year):
    tax_records = fetch_tax_tables(api_base, tax_year)
    federal_rules = None
    state_rules = None
    selected_state_code = None
    for _record in tax_records:
        if _record["kind"] == "federal":
            federal_rules = _record["rules"]
        elif _record["rules"]["name"] == state_name:
            state_rules = _record["rules"]
            selected_state_code = _record["code"]
    if federal_rules is None or state_rules is None:
        raise ValueError("Federal rules or the selected state were not found.")
    if selected_state_code != "VA":
        raise ValueError("This first version calculates Virginia only; other states need additional rules.")
    if state_rules["asof"] != tax_year:
        raise ValueError("Virginia's rules do not match the requested year.")
    return federal_rules, selected_state_code, state_rules, tax_records


@app.function
def calculate_bracket_tax(taxable_income, brackets):
    tax = 0
    lower_limit = 0
    for upper_limit, rate in brackets:
        if taxable_income <= lower_limit:
            break
        if upper_limit is None:
            amount_in_bracket = taxable_income - lower_limit
        else:
            amount_in_bracket = min(taxable_income, upper_limit) - lower_limit
        tax = tax + amount_in_bracket * rate
        if upper_limit is None:
            break
        lower_limit = upper_limit
    return tax


@app.cell
def _(
    federal_rules,
    filing_status,
    health_insurance,
    hsa_contribution,
    post_tax_deductions,
    retirement_percent,
    salary,
    state_rules,
):
    if filing_status not in ["single", "married", "head"]:
        raise ValueError("Use single, married, or head for filing_status.")
    if salary <= 0 or retirement_percent < 0 or retirement_percent > 100:
        raise ValueError("Salary must be positive; retirement percentage must be from 0 to 100.")
    for _amount in [health_insurance, hsa_contribution, post_tax_deductions]:
        if _amount < 0:
            raise ValueError("Deduction amounts cannot be negative.")
    retirement_contribution = salary * retirement_percent / 100
    if retirement_contribution > federal_rules["k401Limit"]:
        raise ValueError("The 401(k) contribution exceeds the fetched under-50 annual limit.")
    if hsa_contribution > federal_rules["hsaLimit"]["single"]:
        raise ValueError("This version supports only the fetched self-only HSA limit.")
    pretax_total = retirement_contribution + health_insurance + hsa_contribution
    if pretax_total > salary:
        raise ValueError("Pretax contributions cannot exceed salary.")
    income_tax_wages = salary - pretax_total
    payroll_tax_wages = salary - health_insurance - hsa_contribution
    federal_taxable_income = max(0, income_tax_wages - federal_rules["std"][filing_status])
    state_taxable_income = max(
        0, income_tax_wages - state_rules["std"][filing_status] - state_rules["exemption"][filing_status]
    )
    federal_tax = calculate_bracket_tax(federal_taxable_income, federal_rules["brackets"][filing_status])
    # Virginia uses the same bracket schedule for these filing statuses.
    state_tax = calculate_bracket_tax(state_taxable_income, state_rules["brackets"]["single"])
    social_security_tax = min(payroll_tax_wages, federal_rules["ss"]["wageBase"]) * federal_rules["ss"]["rate"]
    medicare_tax = payroll_tax_wages * federal_rules["medicare"]["rate"]
    # Employer withholding starts at the fetched $200,000 threshold for every status.
    medicare_tax = medicare_tax + max(
        0, payroll_tax_wages - federal_rules["medicare"]["addlThreshold"]
    ) * federal_rules["medicare"]["addlRate"]
    total_taxes = federal_tax + state_tax + social_security_tax + medicare_tax
    annual_take_home = salary - pretax_total - total_taxes - post_tax_deductions
    return (
        annual_take_home,
        federal_tax,
        federal_taxable_income,
        medicare_tax,
        retirement_contribution,
        social_security_tax,
        state_tax,
        state_taxable_income,
    )


@app.cell
def _(
    api_base,
    fetch_paycheck,
    filing_status,
    health_insurance,
    hsa_contribution,
    retirement_percent,
    salary,
    selected_state_code,
    tax_year,
):
    paycheck_records = fetch_paycheck(
        api_base, selected_state_code, salary, filing_status, tax_year,
        retirement_percent, health_insurance, hsa_contribution,
    )
    return (paycheck_records,)


@app.cell
def _(Path, json, paycheck_records, tax_records):
    # __file__ identifies this notebook, so saving works from any starting folder.
    data_folder = Path(__file__).resolve().parent / "data"
    data_folder.mkdir(parents=True, exist_ok=True)
    for _filename, _records in [
        ("tax-records.json", tax_records), ("paycheck-records.json", paycheck_records)
    ]:
        with (data_folder / _filename).open("w", encoding="utf-8") as _file:
            json.dump(_records, _file, indent=2)
        print(f"Saved {len(_records)} records to {_filename}.")
    print("No fetched records were discarded; all monetary values stay numeric.")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    `Path` builds file locations; `mkdir(..., exist_ok=True)` creates the data folder if needed.
    `with ... open(...)` closes a file automatically, and `json.dump()` saves readable JSON.

    ## 5. The Answer

    This is a standard-deduction payroll estimate, not a complete tax return.
    Additional Medicare withholding can differ from a household's final tax liability.
    `:,.2f` displays dollars with commas and two decimals; `<30` and `>16` line up columns.
    Display rounding changes no saved records.
    """)
    return


@app.cell
def _(
    annual_take_home,
    federal_tax,
    federal_taxable_income,
    health_insurance,
    hsa_contribution,
    medicare_tax,
    post_tax_deductions,
    retirement_contribution,
    salary,
    social_security_tax,
    state_name,
    state_tax,
    state_taxable_income,
    tax_year,
):
    answer_rows = [
        {"item": "Gross salary", "annual": salary},
        {"item": "Traditional 401(k)", "annual": retirement_contribution},
        {"item": "Pretax health insurance", "annual": health_insurance},
        {"item": "Payroll HSA contribution", "annual": hsa_contribution},
        {"item": "Federal income tax", "annual": federal_tax},
        {"item": "Virginia income tax", "annual": state_tax},
        {"item": "Social Security", "annual": social_security_tax},
        {"item": "Medicare", "annual": medicare_tax},
        {"item": "Post-tax deductions", "annual": post_tax_deductions},
        {"item": "Take-home pay", "annual": annual_take_home},
    ]
    print(f"{state_name} paycheck estimate, {tax_year}")
    print(f"Federal taxable income: ${federal_taxable_income:,.2f}")
    print(f"Virginia taxable income: ${state_taxable_income:,.2f}")
    print(f"{'Item':<30}{'Annual dollars':>16}{'Monthly dollars':>18}")
    for _row in answer_rows:
        print(f"{_row['item']:<30}{_row['annual']:>16,.2f}{_row['annual'] / 12:>18,.2f}")
    print(
        f"With a ${salary:,.2f} salary in {state_name}, estimated take-home pay is "
        f"${annual_take_home:,.2f} a year, or ${annual_take_home / 12:,.2f} a month, "
        f"after the listed taxes and deductions."
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. How I Know These Numbers Are Right

    Compare our calculation from the tax tables with the separate paycheck endpoint.
    Post-tax deductions are subtracted from the API's net here because we did not send them.
    `abs()` measures the size of a difference; a difference below one cent passes.
    `assert` stops the notebook if a check fails.
    """)
    return


@app.cell
def _(
    annual_take_home,
    federal_tax,
    medicare_tax,
    paycheck_records,
    post_tax_deductions,
    social_security_tax,
    state_tax,
):
    api_paycheck = paycheck_records[0]
    our_taxes = {
        "federal": federal_tax, "state": state_tax,
        "ss": social_security_tax, "medicare": medicare_tax,
    }
    checked_tax_count = 0
    for _item in api_paycheck["items"]:
        if _item["key"] in our_taxes:
            _our_tax = our_taxes[_item["key"]]
            print(f"{_item['label']}: ours ${_our_tax:,.2f}; API ${_item['amount']:,.2f}")
            assert abs(_our_tax - _item["amount"]) < 0.01, "Tax calculation differs from API."
            checked_tax_count = checked_tax_count + 1
    assert checked_tax_count == 4, "Expected four tax components to check."
    api_take_home = api_paycheck["net"] - post_tax_deductions
    print(f"Annual take-home check: ours ${annual_take_home:,.2f}; API ${api_take_home:,.2f}")
    assert abs(annual_take_home - api_take_home) < 0.01, "Net pay differs from API."
    print("PASS: all four taxes and annual take-home pay agree within one cent.")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Working With the Agent
    The calculation for this table is overall simple, both here and the API has returned with the same endpoint. I did add the pre-tax deductible, in cell 2, back into the calculation.

    ## 8. Reading It Back

    One very important one is having the fetch_tax_tables, we put in the API base address and requested year, it comes out with a list of federal and state tax records. This just tells you how the taxes are calculated, rather than calculating the taxes.

    The other one is calculate_bracket_tax, we put in the taxable income and the list of tax brackets. This is where the calculation comes out, and it applies how much marginal taxis owed at each bracket level, summing up the total tax owed based on the taxable income provided.

    ## 9. Going Further

    This calculation should connect well with MP1; you can add charitable contributions and list potential deductions to see which onessave you the most money.Should the person itemize deductions or take the standard deduction?
    """)
    return


@app.cell
def _(annual_take_home, monthly_expenses):
    if monthly_expenses < 0:
        raise ValueError("Monthly expenses cannot be negative.")
    monthly_remaining = annual_take_home / 12 - monthly_expenses
    print(f"Monthly take-home pay: ${annual_take_home / 12:,.2f}")
    print(f"Monthly expense budget: ${monthly_expenses:,.2f}")
    print(f"Money remaining each month: ${monthly_remaining:,.2f}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 10. Time Spent

    **Complete yourself:** enter the approximate number of hours spent outside class.
    """)
    return


if __name__ == "__main__":
    app.run()
