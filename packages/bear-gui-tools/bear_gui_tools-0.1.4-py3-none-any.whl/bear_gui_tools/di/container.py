"""Dependency Injection container setup for the application."""

from __future__ import annotations

from contextlib import contextmanager
from os import getenv
from typing import TYPE_CHECKING, Any


from bear_dereth.typer_bridge import TyperBridge
from bear_dereth.logger.handlers.queue_handler import QueueHandler
from bear_dereth.logger import LogLevel
from bear_dereth.logger.rich_printer import BearLogger
from bear_dereth.logger.handlers.console_handler import ConsoleHandler
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Resource
from typer import Typer

from bear_gui_tools._internal.debug import METADATA

if TYPE_CHECKING:
    from collections.abc import Generator

    from bear_dereth.config.config_manager import ConfigManager

    from bear_gui_tools.config import AppConfig


@contextmanager
def get_config(env_override: str | None = None) -> Generator[AppConfig, Any]:
    """Context manager to get the application configuration."""
    from bear_gui_tools.config import get_config_manager  # noqa: PLC0415

    env: str = getenv(METADATA.env_variable, "prod")
    if env_override is not None:
        env = env_override
    config_manager: ConfigManager[AppConfig] = get_config_manager(env=env)
    yield config_manager.config


@contextmanager
def get_logger(config: AppConfig) -> Generator[BearLogger, Any]:
    """Context manager to get a logger instance."""
    logger = BearLogger(name=METADATA.name, level=LogLevel.INFO if not config.debug else LogLevel.VERBOSE)
    logger.clear_handlers()
    logger.add_handler(QueueHandler(handlers=[ConsoleHandler()]))
    try:
        yield logger
    finally:
        logger.close()


@contextmanager
def get_typer_app(name: str, help_text: str) -> Generator[Typer, Any]:
    """Context manager to get a Typer application instance."""
    typer_app = Typer(
        name=name,
        help=help_text,
        rich_markup_mode="rich",
        no_args_is_help=True,
    )
    yield typer_app


@contextmanager
def get_typer_bridge(typer_app: Typer, logger: BearLogger) -> Generator[TyperBridge, Any]:
    """Context manager to get a TyperBridge instance."""
    bridge = TyperBridge(typer_app=typer_app, console=logger, is_primary=True)
    yield bridge


class Container(DeclarativeContainer):
    """Dependency Injection container for the application."""

    typer_app = Resource(
        get_typer_app,
        name=METADATA.name,
        help_text=f"[bold bright_green]{METADATA.name}[/bold bright_green] - Command-line interface",
    )
    config = Resource(get_config)
    logger = Resource(get_logger, config=config)
    typer_bridge = Resource(get_typer_bridge, typer_app=typer_app, logger=logger)


container = Container()
