# Hardware

The KiCad project for the board lives here, in `hardware/<board>/`: `<board>.kicad_pro`, `.kicad_sch` and
`.kicad_pcb`, with hierarchical sheets for each circuit block.

## Rules

- **KiCad 9 or newer.** Commit the text files KiCad writes; do not commit `*-backups/`, `*.kicad_prl`, `fp-info-cache`
  or `_autosave-*` (the `.gitignore` already skips them).
- **Parts come from `kokeb-libs`.** Use the symbols, footprints and 3D models that have passed review there, pinned
  by release tag. A part that is not there yet is added to `kokeb-libs` first, through its review, then used here.
- **Circuits come from `kokeb-blocks` where one exists.** A new circuit that could be reused becomes a block.
- **Chip facts come from the driver.** Pins, supply ranges and reference circuits follow the driver repository's
  `docs/hardware.yml`; a board that differs says why in an ADR.
- **Every schematic net has a reason.** Each requirement in `trace/requirements.yml` that the layout implements is
  named in the sheet it belongs to, in a text note: `Implements R-002`.
- **Reviews are files.** A schematic review and a layout review are written up in `hardware/reviews/` before the
  matching gate in [`docs/index.md`](../docs/index.md).

## Checks

ERC and DRC with `kicad-cli`, and the release outputs (Gerbers, BOM, placement, PDFs, 3D render) through KiBot,
are added to the CI gate when the first board design lands in this repository.
