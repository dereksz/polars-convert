from typing import Optional
from pathlib import Path
import polars as pl
import typer
from state import STATE


app = typer.Typer()

@app.command()
def parquet(
    name: Path,
    compression="zstd"
):
    def out(lf: pl.LazyFrame):
        lf.sink_parquet(
            name,
            compression=compression,
        )

    STATE["OUT"] = out


@app.command()
def csv(
    name: Optional[Path],
):
    def out(lf: pl.LazyFrame):
        lf.sink_csv(
            name,
        )

    STATE["OUT"] = out
    STATE["OUT_FILE"] = name

