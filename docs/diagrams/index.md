# Figures

<!-- Written by kokeb-docs figures from docs/diagrams/figures/*.py. Do not edit by hand. -->

Every figure on this site is drawn by a Python module from facts extracted from the code, so it is rebuilt,
not redrawn, when the code changes. CI runs `kokeb-docs figures --check` and fails when a
committed figure no longer matches the code. Each figure below lists the files it is drawn from.

## Board lifecycle

<!-- figure: lifecycle -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="lifecycle.dark.svg">
  <img src="lifecycle.svg"
    alt="Lifecycle of a board in board.yml: concept, design, prototype, verified, released and deprecated,
    each reached through a gate that a person signs off.">
</picture>
<!-- /figure -->

Hardware description: [`docs/model/lifecycle.state.yml`](../model/lifecycle.state.yml)

Drawn from:

- [`docs/model/lifecycle.state.yml`](../model/lifecycle.state.yml)
