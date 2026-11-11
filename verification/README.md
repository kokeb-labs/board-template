# Verification

Test procedures and their results. `trace/verification.yml` points here.

## Layout

- `procedures/` one file per procedure: purpose, the requirements it verifies, equipment, steps, pass criteria
- `results/` one file per run: date, board revision and serial, software versions, equipment and calibration,
  measurements, pass or fail, who ran it

## Rules

- A procedure is written and reviewed before the run, so the criteria are not chosen after seeing the result.
- A result records the exact board revision and firmware version. A different revision is a new run.
- A failed run is kept. The verification in the trace turns `failed`, and the fix is a new run, not an edit.
- A passed verification lists its result files under `evidence`.
