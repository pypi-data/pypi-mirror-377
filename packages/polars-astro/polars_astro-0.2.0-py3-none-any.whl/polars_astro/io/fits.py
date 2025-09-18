import fitsio
import numpy as np
import polars as pl
from polars.io.plugins import register_io_source
from os import PathLike, fspath
from typing import Any, Iterator
from re import sub


def scan_fits_table(filepath: PathLike | str | bytes, *, ext: str | int | None = None, nan_to_null: bool = True) -> pl.LazyFrame:
    """
    Lazily scans a FITS file into a polars LazyFrame. Supports column projection and predicate pushdown.
    In other words, this reader can make some optimizations by reading only the relevant columns and rows.
    Predicate pushdown uses the CFITSIO library's query system.

    Although this creates some great optimizations over reading the entire table into memory, there are still some
    inefficiencies. If speed is important to you, consider converting your tabular data to an optimized data storage
    format like parquet. (Could be as simple as `scan_fits_table(filepath).collect().write_parquet(new_filepath)`)

    :param filepath: The path to the FITS file to be read. This file must contain at least one extension with a table.

    :param ext: The extension (specified as either an int index or string name) in this FITS file containing the
     table to be scanned. If None (the default), then the first extension containing a table is chosen. Raises a
     ValueError if this extension can't be found.

    :param nan_to_null: Whether to replace NaN values in the table with Null. Polars treats NaN as a valid float
    value rather than a null value. Setting this to True (default) will convert existing NaN values to Null.

    :return: A polars LazyFrame
    """
    fits = fitsio.FITS(fspath(filepath))

    # Find table HDU using given ext or the first ext with tabular data
    hdu_index: int | None = None
    if ext is None:
        for _hdu in fits:
            if _hdu.get_exttype() in _supported_ext_types:
                hdu_index = _hdu.get_extnum()
                break
        if hdu_index is None:
            raise ValueError(f"Could not find a supported extension type in {filepath}. Supported types are: {', '.join(_supported_ext_types)}")
    else:
        if ext not in fits:
            raise ValueError(f"Extension {ext} not found in {filepath}.")
        hdu_index = fits[ext].get_extnum()
        if fits[ext].get_exttype() not in _supported_ext_types:
            raise ValueError(f"Extension type {hdu.get_exttype()} is not supported. Supported types are: {', '.join(_supported_ext_types)}")

    # Create Schema from header data
    raw_schema = dict()
    colnames = fits[hdu_index].get_colnames()
    dtypes = fits[hdu_index].get_rec_dtype()[0]
    for i in range(len(dtypes)):
        raw_schema[colnames[i]] = _parse_dtype(dtypes[i])
    schema = pl.Schema(raw_schema)

    # Record Potential Null Values
    null_columns = dict()
    header = fits[hdu_index].read_header()
    for key in header:
        if "TNULL" in key:
            col_index = int(key.replace("TNULL", "")) - 1
            col_name = list(schema.keys())[col_index]
            null_columns[col_name] = header[key]

    fits.close()

    def io_source(with_columns: list[str] | None, predicate: Any, n_rows: int | None, batch_size: int | None) -> Iterator[pl.DataFrame]:
        _fits = fitsio.FITS(fspath(filepath))
        hdu: fitsio.hdu.TableHDU = _fits[hdu_index]

        current_row = 0
        num_rows = hdu.get_nrows()

        if batch_size is None:
            batch_size = 10000

        parsed_predicate = None
        post_filter = False
        if predicate is not None:
            try:
                parsed_predicate = _parse_predicate(predicate)
            except _PredicateParseError:
                post_filter = True

        sub_schema = pl.Schema({
            col: dtype for col, dtype in schema.items() if with_columns is None or col in with_columns
        })

        while n_rows is None or n_rows > 0:
            if n_rows is not None:
                batch_size = min(batch_size, n_rows)

            start = current_row
            end = current_row + batch_size
            current_row += batch_size

            if start >= num_rows:
                break

            if end > num_rows:
                end = num_rows

            raw_result = None
            if parsed_predicate is not None and with_columns is not None:
                matched_rows = hdu.where(parsed_predicate, firstrow=start, lastrow=end) + start
                if len(matched_rows) == 0:
                    yield sub_schema.to_frame()
                    continue
                raw_result = hdu[with_columns][matched_rows]
            elif parsed_predicate is None and with_columns is not None:
                raw_result = hdu[with_columns][start:end]
            elif parsed_predicate is not None and with_columns is None:
                matched_rows = hdu.where(parsed_predicate, firstrow=start, lastrow=end) + start
                if len(matched_rows) == 0:
                    yield sub_schema.to_frame()
                    continue
                raw_result = hdu[matched_rows]
            elif parsed_predicate is None and with_columns is None:
                raw_result = hdu[start:end]

            result: pl.DataFrame = _to_df(raw_result, sub_schema, nan_to_null, null_columns)

            # If the predicate couldn't be converted to a row filter expression, we filter it after the fact
            if post_filter:
                result = result.filter(predicate)

            if n_rows is not None:
                n_rows -= len(result)

            yield result

        _fits.close()

    return register_io_source(io_source=io_source, schema=schema)


_supported_ext_types = ('BINARY_TBL', 'ASCII_TBL')


def _parse_dtype(dtype: str) -> pl.schema.DataType:
    match dtype:
        case "bool": return pl.Boolean
        case ">i1": return pl.Int8
        case ">i2": return pl.Int16
        case ">i4": return pl.Int32
        case ">i8": return pl.Int64
        case ">u1": return pl.UInt8
        case ">u2": return pl.UInt16
        case ">u4": return pl.UInt32
        case ">u8": return pl.UInt64
        case ">f4": return pl.Float32
        case ">f8": return pl.Float64
        case S if "S" in str(S) or "U" in str(S): return pl.String
    ...  # TODO need to add more cases
    print("Unknown type", dtype)
    return pl.Object


def _parse_dtype_numpy(dtype: str) -> np.dtype:
    match dtype:
        case "bool": return np.bool
        case ">i1": return np.int8
        case ">i2": return np.int16
        case ">i4": return np.int32
        case ">i8": return np.int64
        case ">u1": return np.uint8
        case ">u2": return np.uint16
        case ">u4": return np.uint32
        case ">u8": return np.uint64
        case ">f4": return np.float32
        case ">f8": return np.float64
        case S if "S" in str(S) or "U" in str(S): return np.str_
    ...  # TODO need to add more cases
    print("Unknown type", dtype)
    return np.object_


class _PredicateParseError(Exception):
    ...


def _parse_predicate(predicate: Any) -> str:
    """
    Converts the given polars Predicate into a row-filter expression compatible with CFITSIO.

    If no compatible expression can be found, this function raises a _PredicateParseError

    See documentation at e.g. https://github.com/HEASARC/cfitsio/ for more information about compatible
     expression strings.

    :param predicate: A polars predicate expression
    :return: A string expression exactly faithful to the given predicate.
    """
    # TODO replace with better parser
    expr = str(predicate)
    # Replace col("col_name") with $col_name$
    expr = sub(r'col\("([^"]+)"\)', r'$\1$', expr)
    # Replace & with &&
    expr = sub(r'\s*&\s*', ' && ', expr)
    # Remove square brackets
    expr = sub(r'[\[\]]', '', expr)

    return expr


def _to_df(raw_result, schema: pl.Schema, nan_to_null: bool, null_columns: dict) -> pl.DataFrame:
    """Converts the raw array results into a polars DataFrame"""
    rec = np.rec.fromrecords(raw_result, dtype=raw_result.dtype)

    # Data is converted to native endian order
    df = pl.DataFrame(
        {key: rec[key].astype(_parse_dtype_numpy(rec[key].dtype)) for key in schema.keys()},
        schema=schema,
        nan_to_null=nan_to_null
    )

    # Replace null values defined in the FITS header with None
    df = df.with_columns([
        pl.when(pl.col(key) == v)
        .then(None)
        .otherwise(pl.col(key))
        .alias(key) for key, v in null_columns.items() if key in schema
    ])
    return df

# TODO
# ====
# - See if we can optimize this any further
# - Try with more complicated polars filters and more complicated FITS tables
# - Test with an ASCII FITS table (do people use these nowadays?)
# - Test ext option with named extensions
