from typing import  Callable, Dict, Any, Optional, TypedDict
import polars as pl

class State(TypedDict, total=False):
    IN: pl.LazyFrame
    OUT: Callable[[pl.LazyFrame], None]
    OUT_FILE: Optional[str]

STATE = State()
