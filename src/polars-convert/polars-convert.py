#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import typing as t

from cmd_top_level import app
from multi_command import do_multi_no_ok_exit
from multi_command import split_command_line

SEP: t.Final[str] = ":"

if __name__ == "__main__":
    if any(a == SEP for a in sys.argv):
        orig_argv = sys.argv
        do_multi_no_ok_exit(app, split_command_line(sys.argv[1:]))
    else:
        app()  # dispatch to one of multiple commands
