# Mechanical

The enclosure, mounting and any fixtures. Keep the source (code-CAD such as CadQuery or build123d, or FreeCAD) in
this folder and the exports next to it:

- `src/` the source of truth
- `step/` STEP exports of the board assembly and the enclosure, named with the revision
- `drawings/` the PDF drawings that go in the release package

Rules:

- The board outline and mounting holes in the enclosure come from the KiCad board, exported as STEP by
  `kicad-cli`, never measured by hand.
- Each mechanical requirement in `trace/requirements.yml` (`kind: mechanical`) names the dimension or feature that
  meets it, and a verification names how it is checked (fit check, inspection, analysis).
- Materials and finishes appear in the bill of materials of the release package.
