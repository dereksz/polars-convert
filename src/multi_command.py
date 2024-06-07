# -*- coding: utf-8 -*-
import sys
from collections.abc import Generator
from collections.abc import Iterable
from collections.abc import Sequence

from typer import Typer


ARGV0 = sys.argv[0]


def do_multi(app: Typer, argvs: Iterable[Sequence[str]]) -> None:
    # Adding a "full-back" makes the loop logic easier
    for argv in argvs:
        do_one(app, argv)


def do_one(app: Typer, argv: Sequence[str]) -> None:
    sys.argv = [ARGV0, *argv]
    try:  # Could try this instead: https://github.com/tiangolo/typer/issues/129
        app()
    except SystemExit as ex:
        if ex.args[0] != 0:
            raise


def burst_lines(
    line_generator: Iterable[str],
) -> Generator[Sequence[str], None, None]:
    for line in line_generator:
        if line:
            yield line.split()
