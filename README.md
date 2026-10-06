# tabpfn35hackathon

predicting calendar blocks with tabpfn 3.5

for [tabpfn-3.5 hackathon](https://platform.priorlabs.ai/hackathon-3.5)

## data

every block i logged for two years in my apple calendar

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
| `data/events-2026-10-06-filtered.tsv` | 83 | 2026-09-22 | 2026-10-06 |

there are two files because i exported my calendar on 22 sep, before i archived it. the second export is from today and holds the two weeks since. i use those as unseen test data.

columns: `title` `calendar` `allday` `start` `end`

calendars:
- `signal` - focused work and study hours
- `hiwi` - my student job hours
- `noise` - everything else
- `sport` - this was noise before then i started tracking it separately
- `sleep`
- `archive` - everything before i changed the way i log my calendar

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
