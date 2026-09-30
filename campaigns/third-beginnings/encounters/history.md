# Encounter history — Third Beginnings

One entry per fight. **Every entry names its objective** — `tools/validate.py` fails an entry
without an `Objective:` field. The difficulty note at the end of each entry is what the
periodic difficulty check-in reads, so fill it in honestly rather than kindly.

## How to write an entry

Copy the block below. Do not delete this section; `validate.py` skips headings that begin
with "How to", "Template" or "Format".

```
## NNN — <what it was> (<in-world date>)

- **Objective:** <the win condition other than "everything hostile is dead", or state that it
  was a straight fight>
- **Telegraphed:** yes / no — <how the player learned the objective>
- **Party level / size:** N / M
- **Budget:** <threat> (<XP>), spent <XP> — `tools/pf2e.py encounter ...`
- **Opposition:** <creature xN at level L, with any Elite/Weak adjustment>
- **Rounds:** N
- **Outcome:** <what actually happened>
- **Lowest HP reached:** <name at N/M> · **Dying reached:** <no / dying N>
- **Resources spent:** <Hero Points, slots, consumables>
- **XP awarded:** N
- **Treasure:** <value, and what>
- **Conditions that persisted afterward:**
- **Difficulty landed as:** trivial / appropriate / brutal — <one sentence on why>
```

---
