# -*- coding: utf-8 -*-
from __future__ import annotations

import sys
import time

import cmd_in
import cmd_out
import polars as pl
import typer  # https://typer.tiangolo.com/
from click_shell import make_click_shell
from state import STATE


app = typer.Typer(
    no_args_is_help=False,
    pretty_exceptions_short=False,
)

app.add_typer(cmd_in.app, name="in")
app.add_typer(cmd_out.app, name="out")


@app.command()
def head(rows: int) -> None:
    current_in: pl.LazyFrame = STATE["IN"]
    STATE["IN"] = current_in.head(rows)


@app.command()
def go(timeit: bool = False) -> None:
    _in = STATE["IN"]
    _out = STATE["OUT"]
    start = time.time()
    _out(_in)
    if timeit:
        end = time.time()
        print(f"Took {end-start}")


@app.command()
def cat() -> None:
    with open(STATE["OUT_FILE"], "rt") as f:
        for line in f:
            print(line, end="")


@app.callback(invoke_without_command=True)
def base(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        # See: https://click-shell.readthedocs.io/en/latest/usage.html#factory-method
        shell = make_click_shell(ctx, prompt=f"{sys.argv[0]} > ", intro="Starting up...")
        shell.cmdloop()
        typer.Exit(0)
