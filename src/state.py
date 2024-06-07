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
    OUT: Callable[[pl.LazyFrame], None]
    OUT_FILE: Path
    OUT_DELIM: str
    # Dictionary of registrations to be used when using SQL
    AS: Dict[str, pl.LazyFrame]
    SQL: pl.SQLContext


STATE = State()
