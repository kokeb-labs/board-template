---
name: read-datasheet
description: Extract facts from a chip or part datasheet for a requirement or a schematic, with section and page for each. Use whenever a value, pin, limit, land pattern or layout rule is about to be used in the trace, the schematic or the layout.
---

# Read a datasheet

A wrong number here becomes a damaged board. Every fact carries its place in the source.

## Steps

1. Identify the document: title, document number, **revision** and date. Use the revision the driver cites in its
   `docs/datasheets.yml`; record the file's SHA-256 so a later reader knows it is the same file. If the revision
   differs from the driver's, say so and stop to ask.
2. Get real text. If extraction fails (encrypted or scanned PDF), say which method worked. Page numbers are the
   printed page numbers; check them against the PDF page.
3. Read in this order: absolute maximum ratings, electrical characteristics, pin description, interface timing,
   typical application circuits, package and land pattern, soldering, layout notes, errata.
4. Record each fact as: value with unit and condition (min, typ or max; temperature; supply), section, table or
   figure, page. Keep the chip's own names for pins and registers.
5. Cross-check the facts that matter twice: a table against a figure, a limit against the application circuit. Flag
   any disagreement; do not pick a side silently.
6. Separate **what the datasheet says** from **what it does not say**. A silent datasheet is not permission:
   write "not stated" and raise the question.
7. Figures and drawings are read from the page image, not guessed from text extraction.

## Output

- Facts into the driver's `docs/hardware.yml` when they are chip facts, or into the requirement's `rationale` when
  they justify one, always with the reference.
- An **unverified list**: values you could not confirm, figures you could not read, anything inferred.
- A note on errata and application notes the datasheet points to.

## Do not

- Invent, round or "typically assume" a value. Leave it open and name the question.
- Cite a section you did not read.
- Use a distributor's summary or a forum post in place of the datasheet.
