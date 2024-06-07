#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from collections.abc import Generator
from collections.abc import Sequence
from typing import List

import click
import typer
from cmd_top_level import app
from multi_command import do_multi

# See: https://click-shell.readthedocs.io/en/latest/usage.html#factory-method


@click.pass_context
@click.group()
def my_app(ctx: typer.Context) -> None:
    pass


# Back to regular `typer` code


def main() -> None:
    # typer.run(main) # When only a single command
    separators = [idx for idx, arg in enumerate(sys.argv) if arg == ":"]
    if not separators:
        app()  # dispatch to one of multiple commands
    else:  # hack for dispatching MULTIPLE command from a single command line invocation
        do_multi(app, gen_multiple(separators))


def gen_multiple(separators: List[int]) -> Generator[Sequence[str], None, None]:
    orig_argv = sys.argv
    try:
        separators.append(len(orig_argv))
        start_idx = 1
        for sep_idx in separators:
            if start_idx == sep_idx:  # catch a separator at the end or 2 next to each other
                raise typer.BadParameter("Bad command separator layout")
            yield orig_argv[start_idx:sep_idx]
            start_idx = sep_idx + 1
    finally:
        sys.argv = orig_argv


if __name__ == "__main__":
    main()
