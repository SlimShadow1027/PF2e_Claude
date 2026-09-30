# Gazetteer

Places, regions and settlements. Each settlement carries the item level available there,
because that is the number play actually needs.

| Place | Type | Region | Item level | One line |
|---|---|---|---|---|
| | | | | |

A settlement's **level** is what governs what can be bought there (GM Core p.168,
Marketplaces). The size names in `tools/pf2e.py` are only a suggestion for picking one —
set the level explicitly here per settlement, then `python3 tools/pf2e.py settlement
--level N` reads off what is available.
