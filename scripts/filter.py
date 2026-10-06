import os
import re
from pathlib import Path

import pandas as pd

# everything personal lives in workdir/rules/, which is not in the repo:
#   retitle.tsv   whole titles to replace
#   rename.tsv    name, alias, kind, after (words that must come before an ambiguous name)
#   keep.txt      public names that stay


def swap_names(title, names, after):
    words = re.split(r"(\w+)", title)

    for index, word in enumerate(words):
        low = word.lower()

        if low not in names:
            continue

        if low in after:
            before = words[index - 2].lower() if index >= 2 else ""

            if before not in after[low]:
                continue

        alias = names[low]

        if word.isupper():
            alias = alias.upper()
        elif word[0].isupper():
            alias = alias.capitalize()

        words[index] = alias

    return "".join(words)


def replace_names(title, names, after, keep):
    # public names stay: split the title at them and swap only the rest
    pattern = "(" + "|".join(re.escape(phrase) for phrase in keep) + ")"
    parts = re.split(pattern, title, flags=re.IGNORECASE)

    return "".join(part if index % 2 else swap_names(part, names, after) for index, part in enumerate(parts))


def filter_events(name, since=None, until=None):
    table = pd.read_csv("workdir/rules/rename.tsv", sep="\t", dtype=str, keep_default_na=False)
    names = dict(zip(table["name"], table["alias"]))
    after = {name: words.split() for name, words in zip(table["name"], table["after"]) if words}
    keep = Path("workdir/rules/keep.txt").read_text().splitlines()
    titles = pd.read_csv("workdir/rules/retitle.tsv", sep="\t", dtype=str, keep_default_na=False)
    titles = dict(zip(titles["title"], titles["new"]))

    def save(events, stage):
        events.to_csv("workdir/stages/" + name + "-" + stage + ".tsv", sep="\t", index=False)

    events = pd.read_csv("workdir/exports/" + name + ".tsv", sep="\t", dtype=str, keep_default_na=False)

    # stage 1: time cut, only events that started after since and had ended by until
    if since is not None:
        events = events[pd.to_datetime(events["start"]) >= pd.Timestamp(since)]

    if until is not None:
        events = events[pd.to_datetime(events["end"]) <= pd.Timestamp(until)]

    save(events, "stage-1")

    # stage 2: drop the notes column
    events = events[["start", "end", "calendar", "title", "allday"]].copy()
    save(events, "stage-2")

    # stage 3: replace whole titles
    events["title"] = [titles.get(title.strip(), title) for title in events["title"]]
    save(events, "stage-3")

    # stage 4: replace names
    events["title"] = [replace_names(title, names, after, keep) for title in events["title"]]
    save(events, "stage-4")

    # stage 5: reorder the columns
    events = events[["title", "calendar", "allday", "start", "end"]]
    save(events, "stage-5")

    # the last stage is the public data
    events.to_csv("data/" + name + "-filtered.tsv", sep="\t", index=False)

    return events


if __name__ == "__main__":
    os.makedirs("workdir/stages", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # the two exports were made at these times
    first = "2026-09-22 12:56"
    second = "2026-10-06 14:11"

    train = filter_events("events-2026-09-22", until=first)
    test = filter_events("events-2026-10-06", since=first, until=second)

    print(len(train), "train events")
    print(len(test), "test events")
