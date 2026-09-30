# Design notes

Written by the session that built this framework, for the person who has to run with it.

---

## Verification: what happened, and what it means

The spec requires every rules table to be checked against a source before it is committed, and
names Archives of Nethys (`2e.aonprd.com`) as the preferred lookup. This happened in two passes,
and the second one matters more than the first.

### Pass 1 — AoN unreachable, Foundry used as a labelled secondary source

**Archives of Nethys was unreachable from the container that built this.** The egress policy at the
time allowed GitHub and the package registries and denied everything else — not AoN specifically;
`example.com` and Wikipedia failed identically:

```
$ curl -sS -o /dev/null -w "%{http_code}\n" https://2e.aonprd.com/
000   (CONNECT tunnel failed, 403 — connect_rejected by the egress proxy)
$ curl -sS -o /dev/null -w "%{http_code}\n" https://raw.githubusercontent.com/...
200
```

So rather than either guessing or marking every table unverified, the numeric tables were checked
against the **Foundry VTT Pathfinder 2e system source** — an open-source, ORC-licensed
implementation of the same rules, which cites Archives of Nethys rule IDs inline in its own
comments — at version **8.5.1**, commit **`06b904d6ced9795c4c07af085e6f61a56f845c60`**
(<https://github.com/foundryvtt/pf2e>). That pass left **5 of 17 tables `⚠ UNVERIFIED`**.

### Pass 2 — AoN reachable, and eight real errors found

The network policy later allowed `2e.aonprd.com`, so every table was re-read from the published
text. An index of **518 rule pages** was built and the values read page by page. `pf2e.py` now
reports **0 of 23 tables unverified**, and each `Source:` note cites the AoN page ID it was read
from.

**Re-verification was not a formality. It found eight errors in `tools/pf2e.py` and six more in
the `system/` docs**, every one of which had previously read as either confident or merely
"unverified but almost certainly right". They are listed below because a framework that claims
numbers get verified rather than remembered should show what remembering cost.

#### Errors found in `tools/pf2e.py`

| # | What was wrong | What the book says |
|---|---|---|
| 1 | `treasure_mix` — a ~50% permanent / 25% consumable / 25% currency **percentage split** | There is no percentage split. GM Core Table 6-1 names **how many** permanent items and consumables, **at which item levels**, plus a currency figure and a per-additional-PC column. The table was replaced by `TREASURE_DETAIL`. |
| 2 | XP awards were being scaled with party size | GM Core p.76: *"the XP awards for the encounter don't change—you'll always award the amount of XP listed for a group of four characters."* This is how a small party keeps pace with the 1,000-XP curve, and getting it wrong would have starved this campaign of levels. |
| 3 | The Low encounter budget at small party sizes was smoothed silently | The published Low and Moderate Character Adjustments are **both 20**, so the published rule really does send Low to **0 XP** at a party of one. `encounter_budgets` now reports that honestly and offers `--smoothed` as a labelled alternative. |
| 4 | `settlement_item_levels` was presented as an unverified **published** table | There is no such published table. The real rule is GM Core p.168, Marketplaces: a settlement has a **level**. Relabelled as this framework's own convention, with the actual rule implemented alongside as `settlement_availability`. |
| 5 | Elite/Weak HP bands shared their boundaries | They do not. Elite: +10 / +15 / +20 / +30 at levels ≤1 / 2–4 / 5–19 / 20+. Weak: −10 / −15 / −20 / −30 at 1–2 / 3–5 / 6–20 / 21+. |
| 6 | `travel_speed` had 7 rows (Speed 10–40) and its mph / miles-per-day columns were derived | Player Core p.438 publishes **nine** rows, Speed 10 through 60. All nine now read from the table. |
| 7 | The treasure party-size rule was treated as linear division | GM Core p.61 explicitly invites giving a small party **more** than its linear share. `treasure_for` now returns three readings and refuses to pick. |
| 8 | Immunity → doubling/halving → **resistance → weakness** | Player Core p.408, under Resistance: *"After any weaknesses, apply resistances."* Weakness comes **first**. The order changes the answer whenever resistance would take the total below zero: 5 damage against weakness 5 and resistance 10 is 0, not 5. |

#### Errors found in the `system/` docs

| # | Where | What was wrong | What the book says |
|---|---|---|---|
| 9 | `12-rules-quick-reference.md` | Persistent damage: assisted flat check **DC 11** | **DC 10** — Player Core p.445, Assisted Recovery: *"Reduce the DC of the flat check to 10 for a particularly appropriate type of help."* |
| 10 | `10-downtime-travel-and-rest.md` | A night's rest "requires 8 hours, **of which at least 6 must be sleep**" | The 6-hour figure is **invented**. Player Core p.439: *"Once every 24 hours, you can take a period of rest (typically 8 hours)."* The published penalties are sleeping in armour and going 16 hours without rest. |
| 11 | `09-loot-and-economy.md` | Transferring a rune costs **half** the rune's Price | **10%** of the rune's Price, and it takes **1 day** rather than the usual 4. Free from a runestone. GM Core p.225. |
| 12 | `09-loot-and-economy.md` | Selling is at half Price, full stop | Player Core p.267: *"coins, gems, art objects, and raw materials ... can be exchanged for their full Price."* |
| 13 | `10-downtime-travel-and-rest.md` | Treat Wounds, missing the toolkit requirement and the 1-hour option | A healer's toolkit is required, and spending **1 hour** instead of 10 minutes **doubles** the healing. Critical success also removes **wounded**. |
| 14 | `11-leveling-up.md` | Skill-increase and class-feat levels stated as universal | Player Core p.225: *"Your class lists the levels at which you gain each of these improvements."* The common pattern holds for the Player Core classes, but the class advancement table is the authority. |

Errors 1, 2, 3 and 7 are all specific to a small table, and 2 and 3 are the two that would have
been felt first: the first would have stalled advancement, the second would have made every "low"
encounter unbuildable.

### What is still only verified against Foundry

AoN does not present these as tables, so the Foundry source remains the check. Each is labelled as
such in `pf2e.py sources`.

| Table | Verified against |
|---|---|
| Degrees of success, and the natural-20/1 one-step shift | `src/module/system/degree-of-success.ts` |
| Multiple attack penalty −5/−10, agile −4/−8 | `src/module/actor/helpers.ts` `calculateMAPs` |
| Item-bonus expectations by level (from Automatic Bonus Progression) | `src/module/actor/character/automatic-bonus-progression.ts` |
| Dying maximum of 4, recovery DC of 10 + dying value | `src/module/actor/creature/document.ts` |
| All 43 conditions, verbatim | `packs/pf2e/conditions/*.json` |
| Earn Income by level and proficiency, including the failure row | `src/scripts/macros/earn-income.ts` `REWARDS_BY_LEVEL` |
| Treat Wounds healing: 2d8 / 4d8, +0/+0/+10/+30/+50 by rank | `src/module/system/action-macros/medicine/` |
| Initiative cross-side tie-break: the adversary acts first | `src/module/encounter/document.ts` `_sortCombatants` |
| Golarion month names and lengths, and the weekday names | `static/lang/en.json` `PF2E.WorldClock.AR`, `src/module/apps/world-clock/app.ts` |
| The Proficiency Without Level columns (creature XP, simple DCs) | `src/module/dc.ts`, `src/scripts/macros/xp/index.ts` |
| The level −1 DC row (13), which the published table does not include | `src/module/dc.ts` `dcByLevel` |

`python3 tools/pf2e.py sources` prints the provenance of all 23 tables.

---

## To verify before first play

**This list is now empty of published tables.** Every table in `tools/pf2e.py` has been read from
Archives of Nethys or is labelled as this framework's own convention, and the inline values in
`system/` have been checked too.

What remains is not unverified so much as **not published**, and each says so in place:

| Where | What | Status |
|---|---|---|
| `tools/pf2e.py` `settlement_item_levels` | Village 2 / town 6 / city 10 / metropolis 14 / capital 20 | This framework's convention for picking a settlement **level**. The published rule (GM Core p.168) is implemented beside it. Set the level per settlement in `WORLD.md`. |
| `tools/pf2e.py` `level_dcs`, the level −1 row (DC 13) | The published table starts at level 0 | Extrapolated by Foundry for level −1 creatures. Marked `⚠ UNVERIFIED` in place. |
| `tools/pf2e.py` `encounter_budgets(smoothed=True)` | 20 XP per character at every threat | A deliberate house alternative to the published adjustment, offered because the published Low collapses to 0 at a party of one. Never the default. |
| `10-downtime-travel-and-rest.md` | "Hot or cold climate without protection → fewer travel hours per day" | This framework's note, not a published multiplier. |
| `system/03-difficulty-and-solo-levers.md` | Every solo preset and lever | All of it is this framework's design, built **on** verified tables. Labelled throughout. |

### Not modelled at all

- **Leap years** in the Golarion calendar. `tools/pf2e.py` advances time through fixed month
  lengths (Calistril is always 28 days). A campaign that runs for decades of in-world time will
  drift by a day per four years against the published calendar. Fixing it means deciding whether
  Absalom Reckoning has leap years, which is a setting question this framework declined to answer.

---

## Decisions made without the user

This framework was built by an unattended session. The spec says to ask clarifying questions only
where a choice would change the architecture; instead of asking, each of these picked a default.
**Each entry names the alternative it rejected and why**, so any of them can be reversed knowingly.

### 1. Verification source: the Foundry VTT PF2e system, not "unverified everything"

- **Chosen:** check every table that Foundry implements against Foundry's source, cite the file
  and symbol, and mark only what it does not implement.
- **Rejected:** marking every single table `⚠ UNVERIFIED` because Archives of Nethys was blocked.
  That would have been literal compliance and worse in practice: it would put the verified tables
  (DCs, XP budgets, conditions, MAP, degrees of success) on the same footing as the genuinely
  unchecked ones, and the whole point of the marker is to distinguish them.
- **Cost, as it turned out:** a secondary source can carry an error that Foundry and this
  framework would share — and more to the point, the tables Foundry does *not* implement were the
  dangerous ones. **When AoN became reachable, re-verification found eight errors in `pf2e.py`**,
  and six of the eight were in tables Foundry had no opinion about. The decision was right for the
  constraint it was made under; the lesson is that "unverified but almost certainly right" was
  wrong roughly half the time.

### 2. A roll with no `--campaign` is not logged, and says so

- **Chosen:** if no `--campaign` or `--log` is given, `roll.py` does not log and prints
  `(not logged: pass --campaign <slug>...)` to stderr.
- **Rejected:** inferring the campaign when exactly one exists. That is a surprising implicit write
  into a live campaign's audit trail, and the audit trail is the thing this framework is most
  careful with. Also rejected: a repo-root `logs/rolls.jsonl`, which would put campaign data
  outside `campaigns/`.
- **Consequence:** the GM must pass `--campaign` during play. `CLAUDE.md` and every example do.

### 3. Party combatants reference their `pcs` entry rather than copying HP

- **Chosen:** an encounter combatant on the party side carries `ref: "kaelen"` and has `hp: null`;
  its hit points and conditions are read out of `state["pcs"]["kaelen"]`.
- **Rejected:** copying HP into the combatant and syncing it back at the end of the fight. Two
  copies of the number that decides a death is exactly the drift this framework exists to prevent,
  and a mid-combat checkpoint would then be able to restore two disagreeing values.
- **Cost:** one more indirection in the code, and `combatant_hp()` has to exist.

### 4. Gaining coins keeps the denominations received; spending breaks them only when it must

- **Chosen:** `gold add 42gp` leaves 42 gp in the purse. `gold spend` pays from matching
  denominations first and breaks larger coins only when it has to, saying when it did.
- **Rejected:** normalising the purse to the tidiest equivalent on every change (42 gp becomes
  4 pp 2 gp). Same total value, but the purse then reads as something the party never picked up.
- **Rejected:** a single `cp` integer. Simpler, and loses the composition entirely.

### 5. Files beginning with `_` are not copied into a new campaign

- **Chosen:** `templates/characters/_CHARACTER_TEMPLATE.md` and its siblings stay in `templates/`
  with their `{{PLACEHOLDER}}` fields intact. `new_campaign.py` skips them and tells the GM where
  they are.
- **Rejected:** copying them in and filling their placeholders with neutral values, which destroys
  their usefulness as forms.
- **Rejected:** copying them in and exempting `_`-prefixed files from the placeholder check. That
  puts a hole in the check that proves the scaffold is clean.

### 6. A restore never rewinds the checkpoint counter

- **Chosen:** `restore` sets `checkpoint_counter` to the higher of the snapshot's value and the
  highest number on disk. The next checkpoint after restoring 001 is 009, not 002.
- **Rejected:** taking the counter from the snapshot, which is what the first implementation did.
  It produced two different snapshots both numbered `002`, making `restore 002` ambiguous. The
  acceptance run caught it.
- **Rationale:** a restore is history, not an erasure.

### 7. `promote` inserts into the chronicle in date order

- **Chosen:** a promoted event goes where its date puts it, not at the end of the file.
- **Rejected:** strict append-at-end. "Append-only" is about never editing or removing an entry,
  and the chronicle is *read* in date order — a prequel campaign promoting an event from 4710
  after a 4715 entry already exists would leave the file unreadable and fail validation. The
  acceptance run caught this too.

### 8. World slugs drop a leading article

- **Chosen:** `world.py init "The Verdant Reach"` creates `worlds/verdant-reach/`.
- **Rejected:** `worlds/the-verdant-reach/`, which reads badly in every path that mentions it.
  `--slug` overrides either way.

### 9. Four documents are generated from the tools, not written beside them

`07-encounter-building.md`, `12-rules-quick-reference.md`, the travel table in
`10-downtime-travel-and-rest.md`, and the ladder and thresholds in `19-solo-oracle.md` were
generated by scripts that import `tools/pf2e.py` and `tools/oracle.py`.

- **Rationale:** a table written twice drifts. Now the document and the tool cannot disagree, and
  the `Source:` lines in the document are the same strings the tool prints.
- **Cost:** editing one of those tables means editing the tool and regenerating, not editing the
  Markdown. Nothing enforces that; it is a convention, and it is written here so it is known.

### 10. Conventions this framework invented, and labelled as its own

Each of these is stated inline as the framework's own design rather than a published rule:

- **Wounded descriptors** — unhurt / lightly hurt / hurt / badly hurt / barely standing / down, at
  100% / 75% / 50% / 25% / >0 / 0.
- **The scene-check ladder** — 1–2 interrupted, 3–7 altered, 8–20 as expected.
- **The oracle's "no, and" rung** — the symmetric completion of the published "yes, and".
- **The four difficulty presets** — `Story`, `Standard`, `Gritty`, `Nightmare`, each a concrete
  list of toggle values.
- **Everything in `03-difficulty-and-solo-levers.md`** beyond the official variant table: bonus
  reactions, per-scene Hero Point refresh, Hero-Point-converts-a-critical-failure, auto-stabilise
  at dying 3, enemy-count caps, "no death without consent".
- **The settlement size → level suggestion** (village 2 / town 6 / city 10 / metropolis 14 /
  capital 20). The published rule gives a settlement a level and says what that level buys; it
  does not say what level a village is.
- **The smoothed encounter budget** (`--smoothed`, 20 XP per character at every threat), offered
  because the published Low adjustment sends the Low budget to 0 XP at a party of one.
- **Splitting the difference on treasure for a small party**, which GM Core p.61 invites without
  quantifying.
- **Squad batching** — a speed change, not a math change. Each member keeps its own hit points.

### 11. The acceptance transcript is committed as `ACCEPTANCE.md`

- **Chosen:** write the full transcript of the section-26 acceptance run to `ACCEPTANCE.md` at the
  repository root, including the three checks that failed first and what was changed to fix them.
- **Rejected:** reporting the evidence only in the chat message that finished the build. A chat
  message does not survive the session; the question "was this actually tested, and how" is one the
  person running this will ask again in six months.
- **Note:** `ACCEPTANCE.md` is not in the file list the spec asked for. It was added anyway, and
  this line records that.

### 12. Other smaller calls

| Decision | Alternative rejected |
|---|---|
| Dying / wounded / doomed are their own fields, not condition-list entries | Keeping them in the list, which allows two disagreeing copies |
| `validate.py` warnings do not fail the run unless `--strict` | Failing on warnings, which makes a fresh campaign fail for having no characters yet |
| The fairness histogram counts dice a keep-highest discarded | Counting only kept dice; the question is whether the source is straight, and a discarded die still came out of it |
| Healing above maximum is capped, and says how much it discarded | Refusing it. Healing over max is legal in PF2e; the excess is wasted, and silence about it would be the problem |
| Flat checks get no degrees of success | Giving them degrees, which would make a natural 20 on a DC 15 flat check a "critical success" |
| The dashboard has no JavaScript at all | A small script for collapsing sections; not worth the offline risk |
| Same-side initiative ties are settled by a logged d20 roll-off | Sorting on the name, which is what Foundry does and is arbitrary |
| `pf2e.py` offers three readings of a treasure row for a small party and refuses to pick one | Picking the strict subtraction. GM Core p.61 declines to pick too, and at a party of one the two readings are a whole permanent item apart |
| The chronicle's `secret` visibility is withheld from a normal `as-of` read | Showing everything and trusting the reader |

---

## What was deliberately left simple

- **No encumbrance automation beyond the report.** `state.py bulk` and `validate.py` say when a
  carrier is encumbered or over the limit. They do not apply clumsy 1 and the Speed penalty
  automatically, because doing so would mean writing a condition the GM did not ask for.
- **No spell list, feat list or item database.** Those are lookups, not reminders, and putting them
  here would make the repository a bad copy of the books. `12-rules-quick-reference.md` is
  explicit that anything needing a lookup is not in it.
- **`analyze.py`'s "damage taken per encounter" is damage *rolled*, not damage taken per fight.**
  Damage arrives through `state.py damage`, which does not write to the roll log — so the log can
  report what was rolled and cannot attribute it to an encounter. Tagging damage rolls with the
  encounter name would fix it; see the suggestions below.
- **Hero Point *spends* are in `state.json` and the commits, not in the roll log.** Only rerolls
  leave a die behind. `analyze.py` says so rather than reporting zero.
- **No pre-commit dice hashing.** `EXTRAS.md` says to skip it and the reasoning holds: the
  append-only log committed alongside the state it produced is already tamper-evident, and a
  commit-reveal scheme adds real friction for a marginal gain.
- **No Pathbuilder round-trip.** Importing a pasted sheet is supported; maintaining a
  bidirectional exporter against an undocumented format is not.
- **`state.py set` can write any path.** It is the escape hatch for the fields without a dedicated
  verb, and it validates the *shape* of the path but not the *meaning* of the value.
  `validate.py` is the backstop.
- **The Golarion calendar has no leap years, no moon phases and no holidays.**
- **`encounters/active.md` is not auto-generated.** `state.py encounter status` prints the tracker;
  the Markdown copy is the GM's to rewrite each round, which `06-encounter-runner.md` asks for when
  a fight is going badly.

---

## What would make this better to run

These are the GM's own suggestions, from having built it.

### The three worth doing first

1. **Tag rolls with the live encounter automatically.** `roll.py` should read
   `state.json`'s `encounter.name` when `--campaign` is given and add it as a tag. That one change
   unlocks real per-encounter analytics in `analyze.py`: damage taken per fight, rounds per fight,
   how often a fight ended below a quarter HP, and how many fights the third attack actually paid
   for. Right now those have to be reconstructed by hand from `encounters/history.md`.

2. **A `state.py turn` command that does the whole end-of-turn sequence.** Tick durations, roll
   persistent damage and its flat check, prompt for sustained spells, then advance. The sequence is
   specified in `06-encounter-runner.md` and executed by hand, which means it is the thing most
   likely to get skipped in a long fight. Making it one call would make skipping it visible.

3. **Make `roll.py` read modifiers out of `state.json`.**
   `roll.py check --actor kaelen --skill athletics --dc 20` beats retyping `1d20+11` and getting it
   wrong once every twenty rolls. It would also let the tool apply condition penalties
   automatically — frightened 2 is a −2 the GM currently has to remember — which is the single
   largest remaining source of quiet arithmetic error in the system.

### Worth doing

4. **An `options` implementation, not just a procedure.** `14-player-commands.md` specifies what
   `options` should print. A tool that reads the sheet and the tracker and produces it would be
   more reliable than the GM assembling it each turn, and it is the command that makes a full PF2e
   character playable solo.

5. **A reaction prompt the tracker can enforce.** The obligation is stated and has a tracker column
   behind it, but nothing *checks* it. A `state.py encounter trigger <description>` that lists every
   party member with an available reaction and refuses to advance the turn until each is answered
   would turn a duty into a mechanism.

6. **`analyze.py --compare <session-range>` for the difficulty check-in.** The check-in asks the GM
   to read a pattern across sessions. The data is all in the log; the tool should draw the
   comparison rather than leaving the GM to eyeball it, because a GM eyeballing its own difficulty
   trend is precisely the thing the check-in exists to distrust.

7. **Persist a per-campaign default for `--transparency`.** It is in `state.json` already, but
   `roll.py` takes it as a flag and defaults to `standard`. A mismatch silently changes what gets
   redacted. `roll.py` should read it from the campaign when `--campaign` is given.

### Speculative

8. **A `checkpoints` diff view.** `git diff` between two checkpoints works and is verbose.
   `state.py diff 007 014` reporting "Kaelen −11 HP, −1 Hero Point, +80 XP, Cult's Ritual +2, three
   days passed" would make the time machine legible.

9. **Publish the dashboard as an Artifact.** The spec floats this as optional. The local file is
   the mechanism; a URL that updates at every checkpoint would be genuinely better on a phone. Only
   worth it once the local file has been lived with.

10. **A bestiary fetcher.** With network access to Archives of Nethys, `pf2e.py creature "ghoul"`
    could write a `bestiary/` file with a real source line. Without it, the `Source:` requirement
    is enforced by the validator and satisfied by hand — which works, and is slower.

---

## Two honest caveats

- **The verification the acceptance run signed off on was wrong eight times.** Every table in
  `pf2e.py` passed its own provenance check in the first build, and `sources` reported honestly
  which five were unverified. Then AoN became reachable, and re-reading the published text found
  **eight errors in `pf2e.py` and six more in `system/`** — most of them in tables that had *not*
  been flagged. The marker did its job; the confidence around the unmarked values did not. Read
  the table in "Pass 2" above before trusting any number here that a session has not yet used in
  anger.
- **A sixth defect was found after the run, not by it** (commit `26d52eb`): `world.py as-of`
  printed the title of every entry the date gate withheld, so the gate leaked the thing it
  existed to hide. The acceptance checks confirmed the gate *filtered* correctly and never asked
  whether the filtering itself leaked. Worth remembering when reading the other 32 checks: they
  test what they were written to test.
- **The mid-combat restore is tested, not played.** The acceptance run takes a checkpoint in the
  middle of round 3 of a four-combatant fight and restores every tracker field identically,
  including actions spent, MAP step, the reaction that was used and on what, positions, persistent
  damage, and the conditions on the `pcs` side of the reference. That is a real test. It is not the
  same as having lost a session to it and got it back. Run one real fight, checkpoint in the
  middle, and restore, before trusting a long one to it.
