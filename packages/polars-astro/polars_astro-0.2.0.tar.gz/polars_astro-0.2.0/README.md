# polars_astro

A package adding support for common astronomy data files in Polars.

[![DOI](https://zenodo.org/badge/960686891.svg)](https://doi.org/10.5281/zenodo.15151274)

## Installing

`pip install polars_astro`

# Usage

### FITS Files

`scan_fits_file` adds support for reading in FITS files as a `LazyFrame` including
predicate pushdown and column projection. The python package fitsio (built around CFITSIO)
is used internally for efficient row/column access.

```python
import polars as pl
from polars_astro import scan_fits_table

scan_fits_table("astro_catalog.fits").filter(
    pl.col("parallax") > 0.1,
    pl.col("parallax_err") < 0.01
).select(
    pl.col("ID"),
    pl.col("pm_ra"),
    pl.col("pm_dec"),
    pl.col("B_mag"),
    pl.col("V_mag")
)
```