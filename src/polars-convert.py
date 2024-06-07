#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from collections.abc import Sequence
from typing import List

import click
import typer
from cmd_top_level import app

# See: https://click-shell.readthedocs.io/en/latest/usage.html#factory-method


@click.pass_context
@click.group()
def my_app(ctx: typer.Context) -> None:
    pass


# Back to regular `typer` code


def multiple(argv: List[str], separators: List[int]) -> None:
    # Adding a "full-back" makes the loop logic easier
    separators.append(len(argv))
    orig_argv = argv.copy()
    start_idx = 1
    for sep_idx in separators:
        if start_idx == sep_idx:  # catch a separator at the end or 2 next to each other
            raise typer.BadParameter("Bad command separator layout")
        new_argv = [orig_argv[0]]
        new_argv.extend(orig_argv[start_idx:sep_idx])
        sys.argv = new_argv
        try:  # Could try this instead: https://github.com/tiangolo/typer/issues/129
            app()
        except SystemExit as ex:
            if ex.args[0] != 0:
                raise
        start_idx = sep_idx + 1


def main() -> None:
    # typer.run(main) # When only a single command
    separators = [idx for idx, arg in enumerate(sys.argv) if arg == ":"]
    if not separators:
        app()  # dispatch to one of multiple commands
    else:  # hack for dispatching MULTIPLE command from a single command line invocation
        multiple(sys.argv, separators)


if __name__ == "__main__":
    main()
