---
name: scavenge-parts
description: Find candidate parts (ICs, connectors, regulators, passives, modules) and prior art for a design choice, and record them with the facts that matter. Use when an ADR needs options, a part must be chosen, or a block might already exist.
---

# Scavenge parts and prior art

Look first in our own work, then outside, and keep a record of what was considered.

## Where to look, in order

1. `kokeb-libs` (`parts/`) and `kokeb-blocks` (`blocks/`): a reviewed part or block beats a new one.
2. The driver repository's `docs/hardware.yml` and reference circuits.
3. Manufacturer reference designs and evaluation boards for the chip.
4. Open hardware with an open licence: read its licence before reading its design. A design without a licence, or
   with a non-commercial or no-derivatives licence, is for ideas only; copy nothing.
5. Distributor parametric search for alternatives, with the filters written down.

## For each candidate

Manufacturer, manufacturer part number, package and size, the electrical facts the requirement needs (with datasheet
section and page, see `read-datasheet`), **lifecycle status** and its source, how many distributors stock it, an
alternate, how hard it is to hand-solder, and whether a KiCad symbol and footprint exist and who reviewed them.

## Output

- A table of options in the ADR (`docs/adr/`), each with for and against, and the requirement it serves.
- New parts go to `kokeb-libs` through its review before a board uses them.
- A short list of rejected candidates and why, so the question is not asked again.

## Do not

- Pick on price or availability alone; the requirement and the datasheet come first.
- Quote stock or price without the source, date and quantity. They go stale in days.
- Choose a part that is not recommended for new designs or end of life.
