import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    return


@app.cell
def _():
    for charge in [10, 20, 30]:
        total = 0
        total = total + charge
    print(total)
    return


@app.cell
def _():
    order_lines = ["notebook", "pen"]
    len(order_lines)
    return (order_lines,)


@app.cell
def _(order_lines):
    order_lines.extend(["stapler", "tape"])
    order_lines
    return


@app.cell
def _():
    labels = []
    for score in [95, 72, 55]:
        if score >= 60:
            labels.append("Pass")
        elif score >= 90:
            labels.append("A")
        else:
            labels.append("Fail")
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
