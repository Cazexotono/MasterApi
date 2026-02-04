import logging

__all__ = (
    "standart_formatter",
    "message_formatter",
    "debug_formatter",
    "module_formatter",
    )

datefmt = "%Y.%m.%d %H:%M:%S"
style = "{"

standart_formatter = logging.Formatter(fmt="{asctime} | {levelname:8} | {message}", datefmt=datefmt, style=style)
message_formatter = logging.Formatter(fmt="{asctime} - {message}", datefmt=datefmt, style=style)
debug_formatter = logging.Formatter(fmt="{asctime} | {levelname:8} | {filename} - {funcName}: {message}", datefmt=datefmt, style=style)
module_formatter = logging.Formatter(fmt="{asctime} | {levelname:8} | {name}: {message}", datefmt=datefmt, style=style)