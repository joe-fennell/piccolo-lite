<!-- markdownlint-disable -->

# API Overview

## Modules

- [`piccololite`](./piccololite.md#module-piccololite)
- [`piccololite.correct`](./piccololite.correct.md#module-piccololitecorrect): Radiometric Correction
- [`piccololite.io`](./piccololite.io.md#module-piccololiteio): Piccolo file (.pico) input/output

## Classes

- [`correct.RadiometricCorrection`](./piccololite.correct.md#class-radiometriccorrection): Class for performing calibration transformation of Piccolo data.

## Functions

- [`io.read_piccolo_file`](./piccololite.io.md#function-read_piccolo_file): Read in a piccolo data file.
- [`io.read_piccolo_sequence`](./piccololite.io.md#function-read_piccolo_sequence): Read a directory of .pico files or an explicit list.
- [`io.sequence_to_datasets`](./piccololite.io.md#function-sequence_to_datasets): Converts a Piccolo sequence dictionary to xarray Datasets.
- [`io.sequence_to_netcdf`](./piccololite.io.md#function-sequence_to_netcdf): Converts a Piccolo sequence dictionary to NetCDF files.


---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
