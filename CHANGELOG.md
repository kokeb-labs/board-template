# Changelog

All notable changes to this template. A board made from it keeps its own changelog.

## [Unreleased]

### Added

- Board record (`board.yml`), trace data (`trace/`) with a version-linked schema, and `tools/kb_check.py` with
  tests: broken, suspect and wrongly typed links, unverified approved requirements, evidence, classification.
- Folders and rules for hardware, mechanical, firmware, manufacturing and verification.
- Evidence pack outline and supplier tiers; an ADR template.
- `tools/setup.py` to turn the template into a board.
- CI: Markdown and YAML lint, the trace check and its tests, DCO sign-off and the `gate` job.
