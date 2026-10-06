# Gazetteer

Places, regions and settlements. A market is the one place where a world fact and a
ruleset's numbers meet, so each settlement carries **one column per ruleset** and a campaign
reads its own column.

| Place | Type | Region | Item level (PF2e) | Buys up to (D&D) | One line |
|---|---|---|---|---|---|
| **Roderic's Cove** | town | Varisian coast | **3** | common | Dredges the sea caves under its cliff for salvage, and has just started charging admission to a door it should have left alone. |
| **the Sump Door** | site | beneath Roderic's Cove | — | — | A freestanding Thassilonian door seated in bedrock forty feet down, and the seven levels behind it. It gets **drier** as it descends, which is wrong. |
| **Riddleport** | city | Varisian coast, north | 10 | rare | Published Varisian geography. Named here because a city of grey legality on this coast is the obvious candidate for where Roderic's company operates — **not asserted**, and the other campaign decides. |

**Roderic's Cove at level 3** buys and sells common items up to item level 3, with only a
couple of the top-end ones about — run `python3 tools/pf2e.py settlement --level 3`. That is
deliberately low: the Cove is poor, which is the whole reason it cannot afford to close the
door. Anything better than level 3 is a special order, and a special order from Roderic's Cove
means a boat to Riddleport.

**Roderic's Cove for a D&D campaign** sells common magic items and nothing above them —
`python3 tools/dnd5e.py settlement town`. That is the same poverty the item level above
describes, said in the other game's units. **The two columns were picked independently
from the place as described, not derived from each other**: the economies are not the same
shape, and a converted number would be a guess wearing a source's clothes.

- A settlement's **item level** is what governs what can be bought there in Pathfinder
  (GM Core p.168, Marketplaces). The size names in `tools/pf2e.py` are only a suggestion
  for picking one — set the level explicitly here per settlement, then
  `python3 tools/pf2e.py settlement --level N` reads off what is available.
- **Buys up to** is the highest magic item rarity on sale in D&D 2024.
  `python3 tools/dnd5e.py settlement <kind>` gives the published guidance behind it.
