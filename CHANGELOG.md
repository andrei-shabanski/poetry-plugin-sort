# Change Log

## dev

### Added

- Added a `--check` option to verify if dependencies are already sorted.
- `POETRY_SORT_ENABLED` environment variable to enable or disable sorting in `poetry init`, `poetry add` commands.

## [0.1.1] - 2022-10-25

### Changed

- Attached comment lines to a package below instead of moving all comment lines to the top of the section

## [0.1.0] - 2022-09-02

### Added

- Added `poetry sort` command to sort dependencies.

## [0.1.0b2] - 2022-09-01

### Added

- Implemented dependencies sorting after calling `poetry init`, `poetry add`, and `poetry remove` commands.
