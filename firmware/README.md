# Firmware

Example firmware that runs the board with the Kokeb Labs drivers it is built around, on a host PC first and on an
MCU after that.

- Pull each driver in as a submodule or a pinned release from `kokeb-labs-drivers`, and record its version in
  `board.yml` (`drivers`).
- The board's pin map (which MCU pin reaches which chip pin) is a configuration file, never driver code.
- One example per supported host MCU, built with the matching tooling (for ESP32,
  [`espidf-tools`](https://github.com/kokeb-labs/espidf-tools)).
- Each software requirement in `trace/requirements.yml` (`kind: software`) is verified by a test here or by the
  driver's own tests, and the verification names which.
