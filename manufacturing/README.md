# Manufacturing

What a fabricator and an assembler need, generated from a tagged release and never edited by hand.

## Release package

| File | Content |
| --- | --- |
| Gerbers and drill files | Fabrication data for the PCB |
| `bom.csv` | Bill of materials: reference, value, manufacturer, manufacturer part number, footprint, lifecycle status, alternates |
| `placement.csv` | Component placement for assembly |
| Assembly drawings | PDFs of both sides with polarity and fitting notes |
| Test specification | What the end-of-line test checks and the limits |
| `SHA256SUMS` | Checksums of every file, signed with the release |

The package carries the board revision and the commit it was built from.

## Release checklist

- [ ] Trace check clean, no `example` items left
- [ ] Every approved requirement verified or waived with a reason
- [ ] Schematic and layout reviews written up and signed off by someone who did not draw them
- [ ] BOM parts checked for lifecycle status; none end of life or not recommended for new designs
- [ ] ERC and DRC clean
- [ ] Errata for the previous revision reviewed
- [ ] Evidence pack built from the tag ([`docs/evidence-pack.md`](../docs/evidence-pack.md))
- [ ] Signed tag `board-<name>-rev<X>` and the GitHub release with the package attached
