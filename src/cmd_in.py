# -*- coding: utf-8 -*-
import typing as t
from pathlib import Path

import polars as pl
import typer
from parse_functions import comma_list
from state import set_as
from state import STATE


result_type = t.Tuple[Path, pl.LazyFrame]


def result_callback(
    args: result_type,
    sql_name: t.Optional[str] = None,
) -> None:
    """Common post-processing after an `in` has been defined."""
    name: Path
    _in: pl.LazyFrame
    name, _in = args
    set_as(sql_name or name.name, _in)
    STATE["IN"] = _in


app = typer.Typer(
    result_callback=result_callback,
)


@app.callback(invoke_without_command=False)
def base(
    # pylint: disable=unused-argument
    sql_name: t.Annotated[t.Optional[str], typer.Option("--as")] = None
) -> None:
    """the `sql_name` will get passed to `result_callback`"""


@app.command()
def csv(
    # pylint: disable=too-many-arguments
    name: Path,
    *,
    has_header: bool = True,
    column_names: t.Annotated[t.Optional[str], typer.Option(parser=comma_list)] = None,
    skip_rows: int = 0,
    separator: str = ",",
    encoding: str = "utf8",
    low_memory: bool = False,
    eol_char: str = "\n",
    quote_char: t.Optional[str] = None,
    infer_schema_length: int = 250_000,
    glob: bool = True,
    comment_prefix: t.Optional[str] = None,
    null_values: t.Annotated[t.Optional[str], typer.Option(parser=comma_list)] = None,
) -> result_type:
    """Define CSV file to read and it's format."""
    if column_names:
        has_header = False

    _in = pl.scan_csv(
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

    return name, _in


@app.command()
def parquet(
    name: Path,
    *,
    low_memory: bool = False,
    cache: bool = False,
    n_rows: t.Optional[int] = None,
    glob: bool = True,
) -> result_type:
    """Define Parquet file to read and how to read it."""
    _in = pl.scan_parquet(
        name,
        low_memory=low_memory,
        cache=cache,
        n_rows=n_rows,
        glob=glob,
    )
    return name, _in
