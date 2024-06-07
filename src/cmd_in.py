# -*- coding: utf-8 -*-
from pathlib import Path
from typing import Annotated
from typing import List
from typing import Optional

import polars as pl
import typer
from parse_functions import comma_list
from polars.type_aliases import CsvEncoding
from state import STATE

app = typer.Typer()


@app.command()
def csv(
    name: Path,
    *,
    has_header: bool = True,
    column_names: Annotated[Optional[List[str]], typer.Option(parser=comma_list)] = None,
    skip_rows: int = 0,
    separator: str = ",",
    encoding: str = "utf8",
    low_memory: bool = False,
    eol_char: str = "\n",
    quote_char: Optional[str] = None,
    infer_schema_length: int = 1_000_000,
    glob: bool = True,
    comment_prefix: Optional[str] = None,
    null_values: Annotated[Optional[List[str]], typer.Option(parser=comma_list)] = None,
) -> None:
    if column_names:
        has_header = False

    STATE["IN"] = pl.scan_csv(
        name,
        has_header=has_header,
        new_columns=column_names,
        skip_rows=skip_rows,
        separator=separator,
        encoding=encoding,
        low_memory=low_memory,
        eol_char=eol_char,
        quote_char=quote_char,
        infer_schema_length=infer_schema_length,
        glob=glob,
        comment_prefix=comment_prefix,
        null_values=null_values,
    ).rename(str.strip)


@app.command()
def parquet(
    name: Path,
    *,
    low_memory: bool = False,
    cache: bool = False,
    n_rows: Optional[int] = None,
    glob: bool = True,
) -> None:
    STATE["IN"] = pl.scan_parquet(
        name,
        low_memory=low_memory,
        cache=cache,
        n_rows=n_rows,
        glob=glob,
    )
