# board-template

Start a new Kokeb Labs board: a repository with the board record, the requirements trace, the folders for the
electronics, enclosure, firmware and manufacturing data, and CI that checks the trace on every pull request.
It is the board counterpart of [`driver-template`](https://github.com/kokeb-labs/driver-template).

> **Status: version 0.** The trace, the check and the CI are working and tested. The KiCad checks (ERC, DRC, release
> outputs) arrive with the first real board design, so they are tested against a real project. See the
> [roadmap](#whats-next).

## What you get

| Path | What it holds |
| --- | --- |
| `board.yml` | The board in one file: name, status, revision, intended use, the drivers it is built around, variants |
| `trace/` | Needs, requirements, risks and verifications as data, linked with versions; [schema](trace/SCHEMA.md) |
| `tools/kb_check.py` | The trace check: broken links, suspect links, unverified requirements, evidence, classification |
| `hardware/` | The KiCad project, libraries used and the schematic and layout reviews |
| `mechanical/` | The enclosure and mounting as code-CAD or CAD source, with STEP exports |
| `firmware/` | Example firmware that uses the matching drivers on a host or an MCU |
| `manufacturing/` | The release package definition: Gerbers, BOM, placement, assembly drawings, test spec |
| `verification/` | Test procedures, raw results and the evidence the trace points at |
| `docs/` | Board documentation, decisions (`docs/adr/`) and the [evidence pack](docs/evidence-pack.md) outline |
| `.github/workflows/ci.yml` | Markdown and YAML lint, the trace check and its tests, DCO sign-off, one `gate` job |

## Start a board

1. On GitHub choose **Use this template** and create `board-<name>` (for example `board-bmp581-breakout`) in
   [`kokeb-labs-open-boards`](https://github.com/kokeb-labs-open-boards).
2. Clone it and run the setup. It reads the organisation and the name from the repository, asks for a title and a
   one-sentence description, fills in the placeholders and checks the trace:

   ```bash
   python3 tools/setup.py
   ```

3. Replace the example items in `trace/` with your own, starting from the needs.
4. Put the KiCad project in `hardware/` as described in [`hardware/README.md`](hardware/README.md).

## How the trace works, in one paragraph

Every need, requirement, risk and verification is an item with an ID and a version. A link names the item **and the
version it was written against**. Change an item and bump its version, and every item that links to the old version
turns *suspect*: the check fails until someone reviews it and updates the link. That is how a change in a need or a
chip choice reaches every requirement, design element and test that depends on it, in the pull request that makes
the change. Read [`trace/SCHEMA.md`](trace/SCHEMA.md).

## What's next

- KiCad project check in CI (`kicad-cli` ERC and DRC) and release outputs through KiBot, added with the first board.
- The trace check moves into [`ci-tools`](https://github.com/kokeb-labs/ci-tools) once it has run on a few boards.
- A generated board page (pinout, BOM, trace coverage) for the Kokeb Labs portal.

## Licence

[MIT](LICENSE) for the tooling and documentation in this template. A board made from it records its own
hardware licence in `board.yml`.
