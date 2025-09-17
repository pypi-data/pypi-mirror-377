import enum
import functools
import math
import tomllib
from importlib import resources
from typing import *

import click
import preparse

__all__ = ["calculate", "main", "score"]


class Util(enum.Enum):
    util = None

    @functools.cached_property
    def data(self: Self) -> dict:
        "This cached property holds the cfg data."
        text: str = resources.read_text("gravy.core", "cfg.toml")
        ans: dict = tomllib.loads(text)
        return ans


def score(seq: Iterable) -> float:
    "This function calculates the GRAVY score."
    l: list = list()
    x: Any
    y: Any
    for x in seq:
        y = Util.util.data["values"][str(x)]
        if not math.isnan(y):
            l.append(y)
    if len(l):
        return sum(l) / len(l)
    else:
        return float("nan")


calculate = score  # for legacy


@preparse.PreParser().click()
@click.command(add_help_option=False)
@click.option(
    "--format",
    "f",
    help="format of the output",
    default=".5f",
    show_default=True,
)
@click.help_option("-h", "--help")
@click.version_option(None, "-V", "--version")
@click.argument("seq")
def main(seq: Iterable, f: str) -> None:
    "This command calculates the GRAVY score of seq."
    ans: float = score(seq)
    out: str = format(ans, f)
    click.echo(out)
