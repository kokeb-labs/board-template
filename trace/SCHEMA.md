# Trace schema (version 1)

The trace is four YAML files in `trace/`. Each is a list of items. `tools/kb_check.py` reads them and fails the CI
gate on any error.

| File | Item | ID | What it records |
| --- | --- | --- | --- |
| `needs.yml` | Need | `N-001` | What a stakeholder wants, in their words, with its source |
| `requirements.yml` | Requirement | `R-001` | What the board shall do; testable; derived from a need or another requirement |
| `risks.yml` | Risk | `H-001` | A hazard at board level, its harm and the requirements that control it |
| `verification.yml` | Verification | `V-001` | How a requirement is shown to be met, and the evidence |

IDs are never reused. A finished item is rejected or superseded, never deleted, so the history stays in git.

## Fields every item has

| Field | Meaning |
| --- | --- |
| `id` | Prefix by type and at least three digits: `N-001`, `R-014`, `H-003`, `V-020` |
| `title` | A short name |
| `status` | Per type, below |
| `version` | A whole number from 1. **Raise it whenever the meaning changes** (not for a typo) |
| `classification` | `public`, `internal`, `confidential` or `restricted`. An open board allows `public` only |

## Fields by type

| Type | Also required | Status values |
| --- | --- | --- |
| Need | `statement`, `stakeholder`, `source` (`kind`, `ref`, optional `date`) | draft, accepted, rejected, deferred, superseded |
| Requirement | `statement`, `rationale`, `kind`, `derives_from` | draft, approved, rejected, superseded |
| Risk | `hazard`, `harm`, `controls` | open, controlled, accepted, closed |
| Verification | `method`, `verifies` | planned, passed, failed, waived |

- Requirement `kind`: system, electrical, software, mechanical, manufacturing, documentation.
- Verification `method`: test, inspection, analysis, demonstration.
- Optional: `verification_waiver` on a requirement (why it needs no verification), `evidence` (a list of files or
  links) and `waiver` (a reason) on a verification, `example: true` on placeholder items.

## Links and versions

A link is `{id: R-001, ver: 2}`: the item **and the version it was written or reviewed against**.

| Field | On | Points at |
| --- | --- | --- |
| `derives_from` | Requirement | Need or requirement |
| `controls` | Risk | Requirement |
| `verifies` | Verification | Requirement |

When an item's `version` goes up, every item that links to the old version is **suspect**: the check reports
`K008` until a person reads the item against the change and sets the link to the new version. Do that in the same
pull request as the change, so the review shows what was re-checked. Linking to a version that does not exist, to a
missing item or to the wrong type is an error too. An item that links to a rejected or superseded item must be moved
to its replacement.

## Rules the check enforces

| Code | Rule |
| --- | --- |
| K001 | Every trace file and `board.yml` exists and is valid YAML |
| K002 | IDs are unique |
| K003 | IDs match the file's prefix |
| K004 | Required fields are present and not empty (a requirement has at least one parent) |
| K005 | Status, kind, method and classification are from the lists above |
| K006 | The classification is allowed by `board.yml` (`allowed_classifications`) |
| K007 | Links are well formed, point at an existing item of an allowed type |
| K008 | No suspect links, no links to versions that do not exist |
| K010 | An approved requirement has a verification, or a `verification_waiver` |
| K011 | A passed verification lists evidence; a waived one gives its reason |
| K012 | A controlled or closed risk has at least one control |
| K013 | No live item links to a rejected or superseded one |
| K014 | Warning: an `example: true` item is still present |
| K015 | `version` is a whole number from 1 |

Run it with `python3 tools/kb_check.py`; add `--report build` for a JSON and a Markdown coverage report.

## Where a change starts

| A change in | Start at |
| --- | --- |
| What a user or integrator wants | The need; bump its `version`, then follow the suspect links down |
| A chip, a part or a limit in a datasheet | The requirement that states it, and the driver's `hardware.yml` |
| A hazard found in testing or in the field | A new or changed risk, and the control it needs |
| A test that fails | The verification (`failed`), then the requirement or the design |
