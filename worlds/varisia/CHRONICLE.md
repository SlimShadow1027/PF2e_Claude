# Chronicle

The overarching record of this world, ordered by in-world date. **Append-only.** Never
edit or delete an entry; add a correcting entry instead.

Each entry carries a date, the campaign that produced it, the characters involved, what
happened, what it changed, and whether it is public knowledge, rumor, or secret. A later
campaign can only have heard the `public` and `rumor` entries — `secret` ones are the
world's GM-side truth and `tools/world.py as-of` withholds them unless you pass `--gm`.

Written only by `tools/world.py promote`, at a promotion point, with confirmation.
Nothing live is ever promoted: no hit points, coins, inventory, conditions or positions.

<!-- CHRONICLE-ENTRIES-BELOW -->
