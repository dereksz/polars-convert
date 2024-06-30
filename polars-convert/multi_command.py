# -*- coding: utf-8 -*-
import shlex
import sys
from collections.abc import Iterable
from collections.abc import Sequence

import typer


ARGV0 = sys.argv[0]


def do_multi_no_ok_exit(
    app: typer.Typer,
    argvs: Iterable[Sequence[str]],
) -> None:
    """Runs a sequence (Iterable) of commands.

    Each argument sequence _must_ exclude the "typical" argv[0] (the program name).
    """
    # Adding a "full-back" makes the loop logic easier
    for argv in argvs:
        do_one_no_ok_exit(app, argv)


def do_one_no_ok_exit(
    app: typer.Typer,
    argv: Sequence[str],
) -> None:
    """Runs a commands from a sequence of tokens.

    The argument sequence _must_ exclude the "typical" argv[0] (the program name).
    """
    sys.argv = [ARGV0, *argv]
    try:  # Could try this instead: https://github.com/tiangolo/typer/issues/129
        app()
    except SystemExit as ex:
        if ex.args[0] != 0:
            raise


def burst_lines(
    line_generator: Iterable[str],
) -> Iterable[Sequence[str]]:
    for line in line_generator:
        if line:
            yield shlex.split(line)


def split_command_line(
    args: Sequence[str],
    sep: str = ":",
) -> Iterable[Sequence[str]]:
    """Splits command line args into command segments separated by `sep`."""
    separators = [idx for idx, arg in enumerate(args) if arg == sep]
    if not separators:
        yield args
        return
    else:  # hack for dispatching MULTIPLE command from a single command line invocation
        separators.append(len(args))  # Adding a "full-back" makes the loop logic easier
        start_idx = 0
        for sep_idx in separators:
            if start_idx == sep_idx:  # catch a separator at the end or 2 next to each other
                raise typer.BadParameter("Bad command separator layout")
            _next = args[start_idx:sep_idx]
            yield _next
            start_idx = sep_idx + 1
