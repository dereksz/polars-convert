# -*- coding: utf-8 -*-
import typing as t
from enum import Enum, StrEnum, auto
from pathlib import Path

import polars as pl
import typer
from state import STATE


OUT_FUNCTION = t.Callable[[pl.LazyFrame], None]
RESULT_TYPE = t.Tuple[Path, OUT_FUNCTION]


def result_callback(args: RESULT_TYPE) -> None:
    """Common post-processing after an `out` has been created."""
    name: Path
    _out: OUT_FUNCTION
    name, _out = args
    STATE["OUT"] = _out
    STATE["OUT_FILE"] = name


app = typer.Typer(
    result_callback=result_callback,
)


class Compression(StrEnum):
    """Compression options for Parquet."""
    # pylint: disable=invalid-name
    zstd = auto()
    lz4 = auto()
    uncompressed = auto()
    snappy = auto()
    gzip = auto()
    lzo = auto()
    brotli = auto()


@app.command()
def parquet(
    name: Path,
    *,
    compression: Compression = Compression.zstd,
    compression_level: t.Optional[int] = None,
    row_group_size: t.Optional[int] = None,
    data_pagesize_limit: t.Optional[int] = None,
) -> RESULT_TYPE:
    """Set up output to named parquet file with options.

    Still needs a `go` - or another "immediate" command - to perform execution.
    """
    def out(lf: pl.LazyFrame) -> None:
        lf.sink_parquet(
            name,
            compression=compression.name,
            compression_level=compression_level,
            row_group_size=row_group_size,
            data_pagesize_limit=data_pagesize_limit,
        )

    return name, out


@app.command()
def csv(
    name: Path,
    *,
    include_header: bool = True,
    separator: str = ",",
    line_terminator: str = "\n",
    quote_char: str = '"',
    batch_size: int = 1024,
    datetime_format: t.Optional[str] = None,
    date_format: t.Optional[str] = None,
    time_format: t.Optional[str] = None,
    float_precision: t.Optional[int] = None,
) -> RESULT_TYPE:
    """Set up output to named CSV file with options.

    Still needs a `go` - or another "immediate" command - to perform execution.
    """
    def out(lf: pl.LazyFrame) -> None:
        lf.sink_csv(
            name,
            include_header=include_header,
            separator=separator,
            line_terminator=line_terminator,
            quote_char=quote_char,
            batch_size=batch_size,
            datetime_format=datetime_format,
            date_format=date_format,
            time_format=time_format,
            float_precision=float_precision,
        )

    STATE["OUT_DELIM"] = separator
    return name, out
