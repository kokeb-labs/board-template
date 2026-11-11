# AGENTS.md

Agents working in this repository follow the Kokeb Labs
[agent rules](https://github.com/kokeb-labs/.github/blob/main/standards/agents.md). Read them first.

## This repository

- It is the template for every Kokeb Labs board. A change here changes every new board, so keep it small and
  tested.
- `tools/kb_check.py` is covered by `tests/test_kb_check.py`. Change both together and run
  `python3 -m unittest discover -s tests`.
- `tools/setup.py` turns the template into a board: it fills the `{{...}}` placeholders, replaces `README.md` with
  `tools/scaffold/README.md.in` and removes itself. Test it on a copy.
- Nothing here claims a regulatory status. Keep the `intended_use` wording in `board.yml` as it is.

## Rules for a board made from it

- Agents propose; a person approves. Do not set a requirement to `approved`, a verification to `passed` or the
  board `status` forward without a reviewer who did not write the change.
- Never invent a test result, a measurement or a datasheet value. Cite the datasheet section and page, or leave the
  value open.
- Keep `classification: public` on everything in an open board.

## Checks before pushing

- `python3 tools/kb_check.py` and `python3 -m unittest discover -s tests`.
- Markdown: markdownlint with line length 120 (tables and code blocks exempt). YAML: yamllint.
- Commits are signed off (`git commit -s`).
