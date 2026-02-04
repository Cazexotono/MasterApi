import logging
from logging.handlers import TimedRotatingFileHandler

from .formatters import standart_formatter, debug_formatter, module_formatter

from shared.project_path import logs_path

__all__ = (
    "console_handler",
    "console_module_handler",
    "file_handler",
)

console_handler = logging.StreamHandler()
console_handler.setFormatter(standart_formatter)

console_module_handler = logging.StreamHandler()
console_module_handler.setFormatter(module_formatter)

file_handler = TimedRotatingFileHandler(
    filename=str(logs_path / "logs.log"),
    when="midnight",
    backupCount=56,
    encoding="utf-8"
)
file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(debug_formatter)