# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path
from typing import Any
from typing import Callable
from typing import Dict
from typing import Optional
from typing import TypedDict

import polars as pl


class State(TypedDict, total=False):
    IN: pl.LazyFrame
    OUT: Callable[[pl.LazyFrame], None]
    OUT_FILE: Path
    # Dictionary of registrations to be used when using SQL
    AS: Dict[str, pl.LazyFrame]
    SQL: pl.SQLContext


STATE = State()
