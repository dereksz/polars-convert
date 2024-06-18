# -*- coding: utf-8 -*-
import typing as t
from pathlib import Path

import polars as pl
import typer
from rich.console import Console


CONSOLE = Console()
ERROR_CONSOLE = Console(stderr=True)


class State(t.TypedDict, total=False):
    IN: pl.LazyFrame
    IN_FILE: Path
    NEXT_AS: str
    OUT: t.Callable[[pl.LazyFrame], None]
    OUT_FILE: Path
    OUT_DELIM: str
    # Dictionary of registrations to be used when using SQL
    AS: t.Dict[str, pl.LazyFrame]
    SQL: pl.SQLContext


STATE = State()


def set_as(name: str, frame: pl.LazyFrame) -> None:
    _as = STATE.get("AS")
    if _as is None:
        _as = {}
        STATE["AS"] = _as
    _as[name] = frame
    _sql = STATE.get("SQL")
    if _sql is not None:
        _sql.register(name, STATE["IN"])
