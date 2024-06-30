# -*- coding: utf-8 -*-
import typing as t


def comma_list(raw: str) -> t.List[str]:
    return raw.split(",")
