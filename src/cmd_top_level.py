# -*- coding: utf-8 -*-
import sys
import time
import typing as t

import cmd_in
import cmd_out
import polars as pl
import typer  # https://typer.tiangolo.com/
from multi_command import burst_lines
from multi_command import do_multi_no_ok_exit
from state import CONSOLE
from state import set_as
from state import STATE


app = typer.Typer()


app.add_typer(cmd_in.app, name="in")
app.add_typer(cmd_out.app, name="out")


@app.command()
def head(nrows: int) -> None:
    """Restricts the current input to just the first `nrows` lines."""
    current_in: pl.LazyFrame = STATE["IN"]
    STATE["IN"] = current_in.head(nrows)


@app.command()
def go(timeit: bool = False) -> None:
    """When specifying just `in` and `out`, causes one to be streamed to the other."""
    _in = STATE["IN"]
    _out = STATE["OUT"]
    start = time.time()
    _out(_in)
    if timeit:
        end = time.time()
        print(f"Took {end-start}")


@app.command()
def cat(
    colour: t.Annotated[bool, typer.Option("--colour", "--color")] = False,
    table: bool = False,
    max_width: t.Optional[int] = None,
) -> None:
    """Displays the last `go` / `select` / `sql` output to the console,
    with optional colourisation and / or tabulation."""
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
    head: t.Optional[int] = None,
    tail: t.Optional[int] = None,
    title: str = "",
    caption: str = "",
    width: t.Optional[int] = None,
) -> None:
    """Displays the last `go` / `select` / `sql` output in a pager."""
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


def do_sql(*tokens: str) -> None:
    """Executes SQL."""
    _sql = STATE.get("SQL")
    if _sql is None:
        _sql = pl.SQLContext(STATE["AS"])
        STATE["SQL"] = _sql
    lf = _sql.execute(" ".join(tokens), eager=False)
    _out = STATE["OUT"]
    _out(lf)


@app.command()
def sql(tokens: t.List[str]) -> None:
    """Executes SQL."""
    do_sql(*tokens)


@app.command()
def select(tokens: t.List[str]) -> None:
    """Executes Select.

    A slightly briefer form of `sql`.
    """
    do_sql("select", *tokens)


@app.command()
def source(command_file: typer.FileText) -> None:
    """Source commands from given file.

    An alternative to the `-f` option.
    """
    do_multi_no_ok_exit(app, burst_lines(command_file))


@app.callback(invoke_without_command=True)
def base(
    ctx: typer.Context,
    command_file: t.Annotated[
        t.Optional[typer.FileText],
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
        do_multi_no_ok_exit(app, burst_lines(command_file))
    elif ctx.invoked_subcommand is None:
        # See: https://click-shell.readthedocs.io/en/latest/usage.html#factory-method
        from click_shell import make_click_shell

        shell = make_click_shell(ctx, prompt=f"{sys.argv[0]} > ", intro="Starting up...")
        shell.cmdloop()
        typer.Exit(0)
