# -*- coding: utf-8 -*-
import sys
import time
from pathlib import Path
from typing import Annotated
from typing import List
from typing import Optional

import cmd_in
import cmd_out
import polars as pl
import typer  # https://typer.tiangolo.com/
from multi_command import burst_lines
from multi_command import do_multi
from state import CONSOLE
from state import set_as
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
def cat(
    colour: Annotated[bool, typer.Option("--colour", "--color")] = False,
    table: bool = False,
    max_width: Optional[int] = None,
) -> None:
    if colour:
        from rainbowcsv.__main__ import rainbow_csv, CsvDetails

        details = CsvDetails(STATE["OUT_FILE"], STATE["OUT_DELIM"], table, max_width or CONSOLE.width - 1)
        rainbow_csv(details)
    else:
        with open(STATE["OUT_FILE"], "rt") as f:
            for line in f:
                print(line, end="")


@app.command("less")
def less(
    head: Optional[int] = None,
    tail: Optional[int] = None,
    title: str = "",
    caption: str = "",
    width: Optional[int] = None,
) -> None:
    from rich_cli.pager import PagerApp, PagerRenderable
    from rich_cli.__main__ import render_csv

    out_fn = str(STATE["OUT_FILE"])
    if width is None:
        width = CONSOLE.width
    renderable = render_csv(out_fn, head, tail, title, caption)
    render_options = CONSOLE.options.update(width=width)
    lines = CONSOLE.render_lines(renderable, render_options, new_lines=True)
    PagerApp.run(title=out_fn, content=PagerRenderable(lines, width=width))


@app.command("as")
def cmd_as(name: str) -> None:
    """Stores the most recent `in` data source with a name for muse in SQL."""
    set_as(name, STATE["IN"])


@app.command()
def sql(
    tokens: List[str],
) -> None:
    """Executes SQL."""
    _sql = STATE.get("SQL")
    if _sql is None:
        _sql = pl.SQLContext(STATE["AS"])
        STATE["SQL"] = _sql
    lf = _sql.execute(" ".join(tokens), eager=False)
    _out = STATE["OUT"]
    _out(lf)


@app.callback(invoke_without_command=True)
def base(
    ctx: typer.Context,
    command_file: Annotated[
        Optional[typer.FileText],
        typer.Option(
            "--file",
            "-f",
            help="Path to file to get commands, one per line.",
        ),
    ] = None,
) -> None:
    if command_file is not None:
        if ctx.invoked_subcommand is not None:
            raise typer.BadParameter("Can't have both commands and a command file.")
        do_multi(app, burst_lines(command_file))
    elif ctx.invoked_subcommand is None:
        # See: https://click-shell.readthedocs.io/en/latest/usage.html#factory-method
        from click_shell import make_click_shell

        shell = make_click_shell(ctx, prompt=f"{sys.argv[0]} > ", intro="Starting up...")
        shell.cmdloop()
        typer.Exit(0)
