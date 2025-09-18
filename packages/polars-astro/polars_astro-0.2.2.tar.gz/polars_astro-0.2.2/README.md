# polars_astro

A package adding support for common astronomy data files in Polars.

[![DOI](https://zenodo.org/badge/960686891.svg)](https://doi.org/10.5281/zenodo.15151274)

## Installing

`pip install polars_astro`

# Usage

### FITS Files

`scan_fits` adds support for reading in FITS files as a `LazyFrame` including
predicate pushdown and column projection. The python package fitsio (built around CFITSIO)
is used internally for efficient row/column access.

```python
import polars as pl
import polars_astro as pla

pla.scan_fits("astro_catalog.fits").filter(
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

### Numpy Arrays

The `np` namespace makes it easy to retrieve numpy arrays from a `DataFrame`

```python
import polars as pl
import polars_astro as pla

pmra, pmdec, distance = pla.read_fits("astro_catalog.fits").filter(
    pl.col("parallax") > 0.1,
    pl.col("parallax_err") < 0.01
).np.select(
    "pm_ra",
    "pm_dec",
    1/pl.col("parallax")
)
```

`pmra`, `pmdec` and `distance` will all be one-dimensional numpy arrays of the appropriate type. 
Nulls are handled as described in the polars documentation for `Series.to_numpy`. This may involve casting integers to floats.