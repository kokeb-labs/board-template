---
name: plan-board
description: Plan a board or a variant from user needs down to design intent, before any schematic is drawn. Use when starting a board, adding a variant, or changing a need that reaches the design.
---

# Plan a board

Design follows the trace, never the other way. Nothing is drawn until the steps below have a reviewed answer.

## Steps

1. **Needs.** Who wants this and why, in their words, with the source. Run `market-research` for what exists. A need
   with no real user behind it stays `draft`.
2. **Inherit.** List the platform and family requirements this board must meet (the Kokeb board standard and the
   family's requirements); each is inherited, specialised, or waived with a reason.
3. **Requirements.** Testable, each derived from a need or a parent requirement, with a rationale that cites the
   datasheet section and page (`read-datasheet`). Mark the mechanical, electrical, software, manufacturing and
   documentation ones.
4. **Risks.** What could go wrong for the user, the control for each, and the requirement that implements the control.
5. **Options and decisions.** One ADR per real choice (host, connectors, power, bus, mechanical, MCU): options table
   with for and against, the decision, its consequences. Candidates come from `scavenge-parts`. Status `proposed`
   until a person accepts it.
6. **Variants.** What differs (channels, MCU, current sensing), which requirements apply to which, and the cost of
   each (`bom-cost-review`).
7. **Verification and validation.** For every requirement, how it is shown (test, inspection, analysis,
   demonstration), and how the need itself is validated with a real user.
8. **Open questions.** What only a person or a user can answer, listed on `docs/engineering.md`.

## Output

Trace items, ADRs, `docs/engineering.md` updated, `python3 tools/kb_check.py` clean, and a pull request that says what is
a proposal. Then, and only then, the schematic.

## Do not

- Start the schematic before the requirements and ADRs it depends on are reviewed.
- Decide an open question yourself; ask.
