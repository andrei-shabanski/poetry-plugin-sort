# Change Log

## [0.3.0] - 2025-01-06

### Added

- Sort lines in `[project.dependencies]` section.

## [0.2.2] - 2025-01-05

### Added

- Support Poetry version 2.0.

## [0.2.1] - 2024-01-06

### Fixed

- Read the updated pyproject.toml file before sorting dependencies (#15)

## [0.2.0] - 2023-05-21

### Added

- Added a `--check` option to verify if dependencies are already sorted.
- New environment variable `POETRY_SORT_ENABLED` to enable or disable sorting in `poetry init`, `poetry add` commands.
- New environment variable `POETRY_SORT_MOVE_OPTIONALS_TO_BOTTOM` to move optional packages to the bottom.

### Removed

- Support for `poetry remove` command.

## [0.1.1] - 2022-10-25

### Changed

- Attached comment lines to a package below instead of moving all comment lines to the top of the section

## [0.1.0] - 2022-09-02

### Added

- Added `poetry sort` command to sort dependencies.

## [0.1.0b2] - 2022-09-01

### Added

- Implemented dependencies sorting after calling `poetry init`, `poetry add`, and `poetry remove` commands.
