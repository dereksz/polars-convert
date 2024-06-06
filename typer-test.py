#!/usr/bin/env python3

# RUS AS: ./typer-test.py in typer-test.py : out t.t : go

import sys
import time
from typing import Annotated, Dict, Optional, Any
import typer
from pathlib import Path
import polars as pl

# See: https://click-shell.readthedocs.io/en/latest/usage.html#factory-method
import click
from click_shell import make_click_shell

@click.group()
@click.pass_context
def my_app(ctx):
    pass

# Back to normal `typer` code

STATE: Dict[str, Any] = {}

app = typer.Typer(
    no_args_is_help=False,
    pretty_exceptions_short=False,
)

@app.command("in")
def cmd_in(
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
    )


@app.command("out")
def cmd_out(
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
def head(rows: int):
    current_in : pl.LazyFrame = STATE["IN"]
    STATE["IN"] = current_in.head(rows)
    

@app.command("go")
def cmd_go(timeit: bool = False):
    _in = STATE["IN"]
    _out = STATE["OUT"]
    start = time.time()
    _out(_in)
    if timeit:
        end = time.time()
        print(f"Took {end-start}")

    
@app.callback(invoke_without_command=True)
def base(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        # See: https://click-shell.readthedocs.io/en/latest/usage.html#factory-method
        shell = make_click_shell(ctx, prompt=f'{sys.argv[0]} > ', intro='Starting up...')
        shell.cmdloop()
        typer.Exit(0)


if __name__ == "__main__":
    # typer.run(main) # When only a single command
    orig_argv = sys.argv
    separators = [ idx for idx, arg in enumerate(orig_argv) if arg == ":" ]
    if not separators:
        app() # dispatch to one of multiple commands
    else: # hack for dispatching MULTIPLE command from a single command line invocation
        separators.append(len(orig_argv)) # Adding a "full-back" makes the loop logic easier
        orig_argv = orig_argv.copy()
        start_idx = 1
        for sep_idx in separators:
            if start_idx == sep_idx: # catch a separator at the end or 2 next to each other
                raise typer.BadParameter("Bad command separator layout")
            new_argv = [orig_argv[0]]
            new_argv.extend(orig_argv[start_idx:sep_idx])
            sys.argv = new_argv
            try: # Could try this instead: https://github.com/tiangolo/typer/issues/129
                app()
            except SystemExit as ex:
                if ex.args[0] != 0:
                    raise
            start_idx = sep_idx + 1
