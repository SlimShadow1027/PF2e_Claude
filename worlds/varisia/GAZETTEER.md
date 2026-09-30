# Gazetteer

Places, regions and settlements. Each settlement carries the item level available there,
because that is the number play actually needs.

| Place | Type | Region | Level | One line |
|---|---|---|---|---|
| **Roderic's Cove** | town | Varisian coast | **3** | Dredges the sea caves under its cliff for salvage, and has just started charging admission to a door it should have left alone. |
| **the Sump Door** | site | beneath Roderic's Cove | — | A freestanding Thassilonian door seated in bedrock forty feet down, and the seven levels behind it. It gets **drier** as it descends, which is wrong. |
| **Riddleport** | city | Varisian coast, north | 10 | Published Varisian geography. Named here because a city of grey legality on this coast is the obvious candidate for where Roderic's company operates — **not asserted**, and the other campaign decides. |

**Roderic's Cove at level 3** buys and sells common items up to item level 3, with only a
couple of the top-end ones about — run `python3 tools/pf2e.py settlement --level 3`. That is
deliberately low: the Cove is poor, which is the whole reason it cannot afford to close the
door. Anything better than level 3 is a special order, and a special order from Roderic's Cove
means a boat to Riddleport.

A settlement's **level** is what governs what can be bought there (GM Core p.168,
Marketplaces). The size names in `tools/pf2e.py` are only a suggestion for picking one —
set the level explicitly here per settlement, then `python3 tools/pf2e.py settlement
--level N` reads off what is available.
