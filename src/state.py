# -*- coding: utf-8 -*-
from pathlib import Path
from typing import Callable
from typing import Dict
from typing import TypedDict

import polars as pl
from rich.console import Console


CONSOLE = Console()
ERROR_CONSOLE = Console(stderr=True)


class State(TypedDict, total=False):
    IN: pl.LazyFrame
    NEXT_AS: str
    OUT: Callable[[pl.LazyFrame], None]
    OUT_FILE: Path
    OUT_DELIM: str
    # Dictionary of registrations to be used when using SQL
    AS: Dict[str, pl.LazyFrame]
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


def set_next_as(frame: pl.LazyFrame) -> None:
    sql_name = STATE.get("NEXT_AS")
    if sql_name is not None:
        set_as(sql_name, frame)
        del STATE["NEXT_AS"]
