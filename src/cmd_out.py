# -*- coding: utf-8 -*-
from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Optional

import polars as pl
import typer
from state import STATE


app = typer.Typer()


class Compression(Enum):
    zstd = "zstd"


@app.command()
def parquet(
    name: Path,
    compression: Compression = Compression.zstd,
    compression_level: Optional[int] = None,
    row_group_size: Optional[int] = None,
    data_pagesize_limit: Optional[int] = None,
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
) -> None:
    def out(lf: pl.LazyFrame) -> None:
        lf.sink_csv(
            str(name),
        )

    STATE["OUT"] = out
    STATE["OUT_FILE"] = name
