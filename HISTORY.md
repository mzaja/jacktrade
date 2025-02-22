# Release History

## 0.10.0 (2025-02-19)
### Improvements
- Python 3.13 supported.
- Added `message` and `time_str` properties to `CodeTimer` class.

## 0.9.1 (2023-10-25)
### Fixes
- `StringBuffers.flush(file)` does not raise `ValueError` if `file` has not been previously added.

## 0.9.0 (2023-10-23)
### Improvements
- `StringBuffers.remove_all` method added.
### Fixes
- `StringBuffers.flush(file)` raises `ValueError` if `file` has not been previously added.

## 0.8.0 (2023-10-11)
### Improvements
- Added `MasterDict` class.
- `BaseMapping` instances can be inverted.
- `CodeTimer` supports minutes, hours and days.
- Python 3.12 supported.

## 0.7.0 (2023-09-26)
### Improvements
- Added `Permutations` class.

## 0.6.0 (2023-09-24)
### Improvements
- Added Windows and Linux power management commands.
- `CodeTimer` instances can be used as decorators.
### Fixes
- Top-level module interface contains no latent imports from other packages.

## 0.5.0 (2023-09-09)
### Improvements
- Added `BaseMapping` class.
### Fixes
- Corrected a typo in readme.

## 0.4.0 (2023-08-16)
### Improvements
- Added `in_virtual_environment` function.

## 0.3.0 (2023-08-11)
### Improvements
- Added `merge_csv_files` function.

## 0.2.1 (2023-08-08)
### Improvements
- Documentation updated with `StringBuffers` example and new import syntax.

## 0.2.0 (2023-08-08)
### Improvements
- Added `StringBuffers` class.
- All utilities are available for import from the top-level module.

## 0.1.2 (2023-08-01)
### Improvements
- Chunk size is infinite if set to `None`.

## 0.1.1 (2023-04-09)
### Improvements
- Documentation updated.
- Removed redundant statement in `CodeTimer` class.

## 0.1.0 (2023-04-09)
First release.
