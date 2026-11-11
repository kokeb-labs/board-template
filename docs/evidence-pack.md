# Evidence pack

An evidence pack is what a board's release gives an integrator who builds it into their own product: the facts they
need to put it in their own design file. It supports their process. It does not make the board a medical device or
a certified part, and Kokeb Labs does not claim it does.

The supplier tiers say how far a board's records go:

| Tier | Name | What it means |
| --- | --- | --- |
| 0 | Open | Community design with the handbook's checks and CI; trace kept, no evidence pack promised |
| 1 | Evidence | A signed release with the pack below, built from a trace with no open errors |
| 2 | Qualified | Tier 1 plus formal change control, change notices to customers and controlled build records |

## Contents of a tier 1 pack

| Part | Source in this repository |
| --- | --- |
| Intended use and limits: what the board is and is not for | `board.yml` (`intended_use`) |
| Requirements baseline with its version | `trace/requirements.yml` at the release tag |
| Risk analysis at board level and the controls | `trace/risks.yml` |
| Verification records and results, with the evidence files | `trace/verification.yml`, `verification/` |
| Trace coverage report | `python3 tools/kb_check.py --report build` |
| Bill of materials with manufacturer part numbers and lifecycle status | `manufacturing/` |
| Design files: schematic, layout, enclosure, with the exact revision | `hardware/`, `mechanical/` |
| Software: the driver and firmware versions, with an SBOM | `board.yml` (`drivers`), the release assets |
| Known anomalies and errata, open and closed | `docs/errata.md` |
| Release notes and what changed since the previous revision | `CHANGELOG.md` |
| Checksums and a signed release tag | The GitHub release |

## Rules

- A pack is built from a tagged commit and is never edited afterwards. A correction is a new revision.
- A requirement the pack lists as verified has a passed verification with evidence. Anything else is listed as
  open, waived or unverified, with the reason.
- Known anomalies are published. Hiding one is a defect in the pack.
- A pack never contains customer data, supplier prices or anything classified above `public` in an open board.
