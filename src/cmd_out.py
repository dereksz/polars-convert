# -*- coding: utf-8 -*-
import typing as t
from enum import Enum
from pathlib import Path

import polars as pl
import typer
from state import STATE


app = typer.Typer()


class Compression(Enum):
    zstd = "zstd"


@app.command()
def parquet(
    name: Path,
    *,
    compression: Compression = Compression.zstd,
    compression_level: t.Optional[int] = None,
    row_group_size: t.Optional[int] = None,
    data_pagesize_limit: t.Optional[int] = None,
) -> None:
    def out(lf: pl.LazyFrame) -> None:
        lf.sink_parquet(
            name,
            compression=compression.value,
            compression_level=compression_level,
            row_group_size=row_group_size,
            data_pagesize_limit=data_pagesize_limit,
        )

    STATE["OUT"] = out


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
) -> None:
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

    STATE["OUT"] = out
    STATE["OUT_FILE"] = name
    STATE["OUT_DELIM"] = separator
