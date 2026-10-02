# Calendar

**The calendar belongs to this world, not to a ruleset.** One shared world keeps one
calendar no matter which game is being played in it this month, which is what lets a
D&D campaign and a Pathfinder campaign sit on the same timeline and read each other's
dates. `python3 tools/rules.py calendars` lists every calendar the tools know.

- **Calendar in use:** **golarion** (Absalom Reckoning)
- **Present day of this world:** 1 Abadius 4725 AR (third-beginnings, session 1)
- **Eras:** Absalom Reckoning (AR) throughout. Thassilon's fall is the only
  earlier horizon this world currently cares about, and nothing is dated to it yet.

## Built-in calendars

- `golarion` — Absalom Reckoning, which maps month for month onto the Gregorian calendar
  and keeps its month lengths: Abadius 31, Calistril 28, Pharast 31, Gozran 30, Desnus 31,
  Sarenith 30, Erastus 31, Arodus 31, Rova 30, Lamashan 31, Neth 30, Kuthona 31, with
  weekdays Moonday, Toilday, Wealday, Oathday, Fireday, Starday, Sunday.
  Source: `python3 tools/pf2e.py sources` (`calendar`).
- `generic` — twelve 30-day months and a seven-day week, with no era. This framework's
  own placeholder, not a published calendar.

SRD 5.2 publishes no calendar, so a D&D campaign uses `generic` unless this world defines
its own below. Leap years are not modelled in any of them.

## This world's own calendar

This world uses the built-in `golarion` calendar and defines none of its own.
If a campaign here ever needs one: To define one:

1. Copy the JSON below and edit it.
2. Put an HTML comment reading `CALENDAR-BEGIN` on the line above the fenced block, and
   one reading `CALENDAR-END` on the line below it — the same `<!--` / `-->` syntax this
   file's other comments use.
3. Check the result with `python3 tools/rules.py calendars`.

The tools read the JSON between those two comments and ignore everything else on this
page, so the prose around it stays yours. The markers are deliberately **not** written in
for you: a live example would quietly give this world a two-month year.

The example, with the shape of every field:

```json
{
  "name": "verdant-reach",
  "era": "VR",
  "months": [
    {"name": "Thawmonth", "days": 31},
    {"name": "Seedfall", "days": 30}
  ],
  "weekdays": ["Firstday", "Seconday", "Thirday", "Fourthday", "Fifthday", "Restday"]
}
```

`name` is what `state.json` stores in `time.calendar`, `era` is appended to every rendered
date (leave it `""` for none), `months` may be any number of any lengths, and `weekdays`
may be any number. Once it reads back correctly, point the campaigns at it:
`python3 tools/state.py --campaign <slug> set time.calendar <name>`.
