# Calendar

**The calendar belongs to this world, not to a ruleset.** One shared world keeps one
calendar no matter which game is being played in it this month, which is what lets a
D&D campaign and a Pathfinder campaign sit on the same timeline and read each other's
dates. `python3 tools/rules.py calendars` lists every calendar the tools know.

- **Calendar in use:** `verge` — this world's own, defined below
- **Present day of this world:** _(the latest date any campaign has reached)_
- **Eras:** **VR**, the Verge Reckoning, counted from the first crossing anybody wrote down.
  There is no agreed earlier era: what came before the Reckoning is the deep past, and the
  Verge does not date it.

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

The Verge has no sun, so it does not have a year in the sense the material world means one.
What it has instead is a **drift cycle**: the shards move against one another on a slow,
roughly regular schedule, and the eight named spans below are the positions of that cycle
rather than seasons. Crossing between shards is easy in some of them and impossible in
others, which is why everything here is dated and why nobody argues about the calendar.

Eight spans of forty days, and a five-day week. The year is 320 days long, which is shorter
than Varisia's and is one of the several reasons the two worlds' dates cannot be compared
even where both are written as numbers.

<!-- CALENDAR-BEGIN -->
```json
{
  "name": "verge",
  "era": "VR",
  "months": [
    {"name": "Nearing", "days": 40},
    {"name": "Touching", "days": 40},
    {"name": "Holding", "days": 40},
    {"name": "Parting", "days": 40},
    {"name": "Widening", "days": 40},
    {"name": "Falling", "days": 40},
    {"name": "Stillness", "days": 40},
    {"name": "Turning", "days": 40}
  ],
  "weekdays": ["Crossday", "Shoreday", "Deepday", "Highday", "Lastday"]
}
```
<!-- CALENDAR-END -->

Check it with `python3 tools/rules.py calendars`. `tools/world.py link` adopts it into a
campaign's `state.json` automatically and seats the clock on the start date, so a campaign
linked here does not have to be pointed at it by hand.

**What the spans mean in play**, since a date is also a sentence about whether travel is
possible:

| Span | The shards are | Crossing is |
|---|---|---|
| Nearing | closing | getting easier; everyone is in a hurry |
| Touching | at their closest | easy, and briefly cheap |
| Holding | steady and close | the season of trade and of war |
| Parting | separating | closing; last chance to be on the right shard |
| Widening | far apart | expensive and dangerous |
| Falling | at their furthest | effectively impossible |
| Stillness | furthest, and not moving | impossible, and the reason everything is stored |
| Turning | beginning to close again | rumour season; nothing confirmed yet |

The one thing a newcomer gets wrong is treating Stillness as a bad month to travel in. It is
not a bad month to travel in. It is the month in which you do not travel, and a plan that
needs you to be elsewhere during it is not a plan.
