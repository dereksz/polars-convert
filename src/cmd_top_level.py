# -*- coding: utf-8 -*-
import sys
import time
from typing import Annotated
from typing import Optional

import cmd_in
import cmd_out
import polars as pl
import typer  # https://typer.tiangolo.com/
from state import CONSOLE
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
    _as = STATE.get("AS")
    if _as is None:
        _as = {}
        STATE["AS"] = _as
    _as[name] = STATE["IN"]
    _sql = STATE.get("SQL")
    if _sql is not None:
        _sql.register(name, STATE["IN"])


@app.callback(invoke_without_command=True)
def base(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        # See: https://click-shell.readthedocs.io/en/latest/usage.html#factory-method
        from click_shell import make_click_shell

        shell = make_click_shell(ctx, prompt=f"{sys.argv[0]} > ", intro="Starting up...")
        shell.cmdloop()
        typer.Exit(0)
