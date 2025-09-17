# Changelog

## 2025-09-19 Version 0.2.1

- Fixed:
  - Bug in `log_orbit` as year was not correctly passed.
  - Big in `check_crabbing`, which could result in the wrong sign when limiting the crabbing angle.

- Changed:
  - Linting and formatting.

## 2024-11-08 Version 0.2.0

- Added:
  - Path Container

- Changed (internal):
  - Updated Workflows
  - Switched to `pyproject.toml`

## 2024-04-05 Version 0.1.0

- Added:
  - new (>2022) lhc orbit variabes and related changes in corresponding functions
  - flexible knob-suffix instead of pre-defined "_sq"
  - new functions: `temp_disable_errors`, `lhc_arc_names` and `add_expression` in `general.py`
  - Coupling knob creation

## 2022-03-22 Version 0.0.2

- typo magentic to magnetic
- more doc
- unified `machine` -> `accel`
- some minor fixes of copy-paste remains

## 2021-11-19 Version 0.0.1

- This is a very early release. Things should work, but I need tests.
