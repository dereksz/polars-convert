from typing import Optional
from pathlib import Path
import polars as pl
import typer
from state import STATE

app = typer.Typer()

@app.command()
def csv(
    name: Path,
    separator: str=",",
    encoding: str="utf8",
    low_memory: bool =False,
    eol_char: str="\n",
    quote_char: Optional[str]=None,
    infer_schema_length: int=1_000_000,   
):
    STATE["IN"] = pl.scan_csv(
        name,
        separator=separator,
        encoding=encoding,
        low_memory=low_memory,
        eol_char=eol_char,
        quote_char=quote_char,
        infer_schema_length=infer_schema_length,
    ).rename(str.strip)