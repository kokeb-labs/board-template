---
name: trace-change
description: Change a need, requirement, risk or verification in trace/ and carry the change through. Use whenever the meaning of a trace item changes, a datasheet fact changes, or a test fails.
---

# Change the trace

The trace is the record of why the board is the way it is. A change is complete only when everything that depends on
it has been re-read.

## Steps

1. Read `trace/SCHEMA.md`. Find where the change starts (the table "Where a change starts").
2. Edit the item. If its **meaning** changes, raise its `version` by one; a typo does not change it.
3. Run `python3 tools/kb_check.py`. Each `K008` names a link now older than its target. Open each linking item, read it
   against the change, decide whether it still holds, change it if not, and only then set the link to the new
   version. Do this in the same pull request, so the review shows what was re-checked.
4. Check downstream: the verification that covers the requirement (does its procedure still show it?), the risks it
   controls, the ADR that cites it, the schematic notes `Implements R-...`, and the docs.
5. A failed verification sets `status: failed` and opens the question at the requirement or the design, not at the
   test.
6. Add the change to `CHANGELOG.md` when it affects a released revision, and to `docs/errata.md` if a released board
   is affected.

## Rules

- IDs are never reused and items are never deleted: reject or supersede them.
- An agent proposes; a person who did not write the change sets a requirement to `approved`, a verification to
  `passed` (with evidence files) and a need to `accepted`.
- Keep `classification: public` on everything in an open board.

## Output

A pull request whose description lists the item changed, the old and new version, every link re-read and what was
concluded, and the check output.
