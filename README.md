# tabcal

predicting calendar blocks with tabpfn 3.5

for [tabpfn-3.5 hackathon](https://platform.priorlabs.ai/hackathon-3.5)

## setup

```sh
uv sync
uv run python -c "from tabpfn_client import interactive_login; interactive_login()"
```

## predict

i give a title, a calendar and a start time 

the start is a time for today or a full date like `"2026-10-07 09:00"`

```sh
uv run python tabcal.py predict "rl" signal 20:00
```

tabpfn 3.5 takes every block i ever logged as context and predicts the end

```
rl · signal · 2026-10-06 20:00

21:00   60 min  ████████████████████████  56%
21:30   90 min  ███                        7%
22:00  120 min  ██████████                22%
23:00  180 min  ██                         5%
00:00  240 min  █                          2%
```

it gives a probability for every number of minutes, i add them up in steps of 15 minutes because that is how i log

## evaluate

train on everything before 22 sep and test on the two weeks after

```sh
uv run python tabcal.py evaluate
```

```
train  5136 events  2024-09-12 to 2026-09-22
test     85 events  2026-09-22 to 2026-10-06

model      mae  rmse
baseline  47.7  66.5
tabpfn    36.7  54.8
```

mae and rmse are in minutes

other evaluations also have been done (not here bc almost out of daily api credits)

## data

every block i logged for two years in my apple calendar

these are noisy estimates of my life 

read the calendar with a swift script and filtered with python

```sh
swiftc scripts/export.swift -o workdir/export
workdir/export 2024-09-01 2027-07-01 > workdir/exports/events-2026-09-22.tsv
workdir/export 2026-09-22 2026-10-07 > workdir/exports/events-2026-10-06.tsv
uv run python scripts/filter.py
# needs workdir/rules which holds private info and is not in the repo
```

filters:
- names of people are replaced for privacy purposes
- names of speakers at public talks are kept
- private titles are replaced with general ones
- planned events that had not happened yet are cut
- notes column is dropped

| file | events | from | to |
|---|---|---|---|
| `data/events-2026-09-22-filtered.tsv` | 5136 | 2024-09-12 | 2026-09-22 |
| `data/events-2026-10-06-filtered.tsv` | 85 | 2026-09-22 | 2026-10-06 |

there are two files because i exported my calendar on 22 sep, before i archived it. the second export is from today and holds the two weeks since. i use those as unseen test data.

small example here:

| title | calendar | allday | start | end |
|---|---|---|---|---|
| tabpfn hackathon | signal | false | 2026-09-16 23:00 | 2026-09-17 00:00 |
| hiwi | hiwi | false | 2026-03-18 00:00 | 2026-03-18 01:00 |
| bananenbrot | noise | false | 2025-10-09 20:30 | 2025-10-09 23:30 |
| lavender 5k | sport | false | 2026-07-05 10:30 | 2026-07-05 12:00 |
| sleep | sleep | false | 2026-07-11 07:00 | 2026-07-11 10:00 |
| tagesschau | archive | false | 2024-12-16 20:00 | 2024-12-16 20:30 |
| xmas break | archive | true | 2025-12-23 00:00 | 2026-01-06 23:59 |

calendars i use:
- `signal` - focused work and study hours
- `hiwi` - my student job hours
- `noise` - everything else
- `sport` - this was noise before then i started tracking it separately
- `sleep`
- `archive` - everything before i changed the way i log my calendar
