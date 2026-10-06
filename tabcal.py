from datetime import timedelta

import pandas as pd
import typer
from scipy.special import softmax
from sklearn.metrics import mean_absolute_error, root_mean_squared_error
from tabpfn_client import TabPFNRegressor


class Config:
    past = "data/events-2026-09-22-filtered.tsv"
    recent = "data/events-2026-10-06-filtered.tsv"
    features = ["title", "calendar", "allday", "start"]
    dtypes = {"title": "string", "calendar": "string"}
    target = "minutes"
    version = "v3.5"
    seed = 42
    step = 15
    top = 5
    format = "%Y-%m-%d %H:%M"
    time = "%H:%M"
    decimals = 1
    gap = "  "
    bar = 24


c = Config()

app = typer.Typer(add_completion=False)


def read_events(path):
    events = pd.read_csv(path, sep="\t", dtype=c.dtypes, parse_dates=["start", "end"], keep_default_na=False)
    events[c.target] = (events["end"] - events["start"]) / timedelta(minutes=1)
    return events


def fit_model(train):
    model = TabPFNRegressor.create_default_for_version(c.version, random_state=c.seed)
    model.fit(train[c.features], train[c.target])
    return model


def show(rows):
    widths = [max(len(cell) for cell in column) for column in zip(*rows)]

    for row in rows:
        first = row[0].ljust(widths[0])
        rest = [cell.rjust(width) for cell, width in zip(row[1:], widths[1:])]
        print(c.gap.join([first, *rest]))


def baseline(train, test):
    by_calendar = train.groupby("calendar")[c.target]
    median = test["calendar"].map(by_calendar.median())
    mean = test["calendar"].map(by_calendar.mean())
    return pd.DataFrame({"median": median, "mean": mean}, index=test.index)


def tabpfn(train, test):
    model = fit_model(train)
    output = model.predict(test[c.features], output_type="main")
    return pd.DataFrame({"median": output["median"], "mean": output["mean"]}, index=test.index)


@app.command()
def evaluate():
    train = read_events(c.past)
    test = read_events(c.recent)

    summary = []

    for name, events in [("train", train), ("test", test)]:
        dates = events["start"].dt.date
        summary.append([name, f"{len(events)} events", f"{dates.min()} to {dates.max()}"])

    scores = [["model", "mae", "rmse"]]

    for model in [baseline, tabpfn]:
        predicted = model(train, test)
        mae = mean_absolute_error(test[c.target], predicted["median"])
        rmse = root_mean_squared_error(test[c.target], predicted["mean"])
        scores.append([model.__name__, str(round(mae, c.decimals)), str(round(rmse, c.decimals))])

    print()
    show(summary)
    print()
    show(scores)
    print()


@app.command()
def predict(title: str, calendar: str, start: str):
    start_time = pd.Timestamp(start)

    train = pd.concat([read_events(c.past), read_events(c.recent)])
    block = pd.DataFrame([{"title": title, "calendar": calendar, "allday": False, "start": start_time}])
    block = block.astype(c.dtypes)

    model = fit_model(train)
    output = model.predict(block[c.features], output_type="full")

    logits = output["logits"][0]
    borders = output["borders"]

    weights = softmax(logits)

    centers = (borders[:-1] + borders[1:]) / 2
    lengths = (centers / c.step).round() * c.step

    chances = pd.Series(weights).groupby(lengths).sum()
    likeliest = chances.sort_values(ascending=False).head(c.top).sort_index()

    rows = []

    for length, chance in likeliest.items():
        end_time = start_time + timedelta(minutes=length)
        bar = "█" * round(chance / likeliest.max() * c.bar)
        rows.append([end_time.strftime(c.time), f"{int(length)} min", bar.ljust(c.bar), f"{chance:.0%}"])

    print()
    print(" · ".join([title, calendar, start_time.strftime(c.format)]))
    print()
    show(rows)
    print()


app()
