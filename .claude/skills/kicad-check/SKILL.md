---
name: kicad-check
description: Run ERC, DRC and the release outputs with kicad-cli and KiBot, and edit KiCad files safely, including through an MCP server. Use before and after every change to hardware/, and before any review or release.
---

# Check and edit KiCad safely

`kicad-cli` is the judge. An edit counts only when ERC and DRC pass afterwards, whoever or whatever made it.

## Check

1. `kicad-cli sch erc --exit-code-violations -o build/erc.rpt hardware/<board>/<board>.kicad_sch`
2. `kicad-cli pcb drc --exit-code-violations -o build/drc.rpt hardware/<board>/<board>.kicad_pcb`
3. Outputs: KiBot with `.kibot/release.kibot.yaml` (the `Hardware` workflow runs it from a pinned container).
4. Read the reports; do not only look at the exit code. A rule switched off in the project is a decision: it needs
   an ADR.

## Edit

1. Work on a branch with a clean tree; commit before each session so every edit is a reviewable `git diff`.
2. KiCad files are text. Check the diff for lost labels, wires, sheet properties, title block and UUIDs.
3. Every net and part traces to a requirement: put `Implements R-0xx` in the sheet. A part not in `kokeb-libs` goes
   through its review first.
4. After the edit run Check; revert an edit that adds violations or loses content.
5. Open the project in KiCad once in a while and save from KiCad, so the files stay in the format KiCad writes.

## MCP servers

An MCP server is a convenience over the same files. Use one only by these rules:

- Pin the version and read its release notes before bumping; read the code before the first run.
- Start read-only, on a throwaway copy of the project, stdio transport only, no cloud, pairing or telemetry features.
- Move to write mode only for schematic work, and re-run Check outside the server after every change.
- Never let it release or manufacture; a person does.

## Do not

- Mark a review or a verification done because a check passed; checks are necessary, a reviewer decides.
- Commit `*-backups/`, `*.kicad_prl`, `fp-info-cache` or autosave files.
