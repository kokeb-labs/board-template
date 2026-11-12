---
name: bom-cost-review
description: Review a bill of materials for cost, supply, lifecycle and risk, and compare variants. Use before a design review, before a release, and when a variant or channel count is being chosen.
---

# Review a BOM and its cost

Cost and supply are requirements too: they decide whether the board can be built and sold.

## Steps

1. Take the BOM from the release package or `kicad-cli` (`bom.csv`), never from memory. Note the revision and commit.
2. Check each line has: reference, value, manufacturer, manufacturer part number, footprint, lifecycle status, at
   least one alternate. List the lines that lack any.
3. **Lifecycle:** flag anything end of life, last time buy, or not recommended for new designs. Record the source and
   the date checked.
4. **Supply:** how many distributors stock it, minimum order, lead time, sole-source parts. A sole-source part
   needs an ADR that accepts the risk or a second source.
5. **Cost:** price per line at stated volumes (for example 1, 100, 1000) with source and date. Total per board and per
   variant. If a figure is not sourced, write "not priced", never an estimate presented as a fact.
6. **Cost drivers:** the three lines that cost the most, and the lines that scale with a variant (channels, current
   sensing, MCU). State the cost per channel for multi-channel boards.
7. **Assembly:** package sizes a hobbyist or a contract assembler can handle, double-sided assembly, hand-soldered
   parts, parts needing special process.
8. Compare variants side by side in one table and say what each saves or costs against the requirement it serves.

## Output

`docs/research/bom-<revision>.md` with the tables, the flagged lines and recommendations; a changed part goes back
through `scavenge-parts` and an ADR.

## Do not

- Cost-reduce by dropping something a requirement or a risk control needs; name the requirement.
- Quote a price without source, date and quantity.
- Treat an alternate as equivalent without checking the datasheet limits against the requirement.
