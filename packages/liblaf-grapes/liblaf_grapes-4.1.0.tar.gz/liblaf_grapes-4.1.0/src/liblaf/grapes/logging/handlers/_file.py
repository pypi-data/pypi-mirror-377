import types
from pathlib import Path
from typing import Unpack

import loguru
from rich.console import Console
from rich.traceback import Traceback

from liblaf.grapes import pretty
from liblaf.grapes.conf import config
from liblaf.grapes.logging._traceback import rich_traceback
from liblaf.grapes.logging.filters import new_filter


def file_handler(
    **kwargs: Unpack["loguru.FileHandlerConfig"],
) -> "loguru.FileHandlerConfig":
    if "sink" not in kwargs:
        kwargs["sink"] = config.logging.file or Path("run.log")
    kwargs.setdefault("format", _format)
    kwargs["filter"] = new_filter(kwargs.get("filter"))
    kwargs.setdefault("mode", "w")
    return kwargs


def _format(record: "loguru.Record") -> str:
    fmt: str = (
        "<green>{elapsed}</green> "
        "<level>{level:<8}</level> "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> "
        "<level>{message}</level>\n"
    )
    if record["exception"] is None:
        return fmt
    exc_type: type[BaseException] | None
    exc_value: BaseException | None
    traceback: types.TracebackType | None
    exc_type, exc_value, traceback = record["exception"]
    if exc_type is None or exc_value is None:
        return fmt + "{exception}\n"
    console: Console = pretty.get_console(color_system=None)
    rich_tb: Traceback = rich_traceback(exc_type, exc_value, traceback, width=128)
    with console.capture() as capture:
        console.print(rich_tb)
    record["extra"]["rich_traceback"] = capture.get()
    return fmt + "{extra[rich_traceback]}\n"
