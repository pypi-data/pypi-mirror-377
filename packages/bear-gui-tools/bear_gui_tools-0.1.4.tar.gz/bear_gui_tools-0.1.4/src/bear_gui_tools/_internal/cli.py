# - When you run `python -m bear_gui_tools` python will execute
#   `__main__.py` as a script. That means there won't be any
#   `bear_gui_tools.__main__` in `sys.modules`.
# - When you import `__main__` it will get executed again (as a module) because
#   there's no `bear_gui_tools.__main__` in `sys.modules`.
from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Annotated, cast

from bear_dereth.cli import ExitCode
from bear_dereth.cli.arg_helpers import CLIArgsType, args_parse
from bear_dereth.versioning import BumpType, cli_bump
from dependency_injector.wiring import Provide, inject
from typer import Argument, Option, Typer, echo

from bear_gui_tools._internal._info import METADATA
from bear_gui_tools._internal.debug import _print_debug_info
from bear_gui_tools.di import Container, container

if TYPE_CHECKING:
    from bear_dereth.typer_bridge import TyperBridge


@inject
def _typer_app(typer_app: Typer = Provide[Container.typer_app]) -> Typer:
    """Get the Typer application instance."""
    return typer_app


@inject
def _get_bridge(typer_bridge: TyperBridge = Provide[Container.typer_bridge]) -> TyperBridge:
    """Get the TyperBridge instance."""
    return typer_bridge


container.wire(modules=[__name__])

_cli: TyperBridge = _get_bridge()


def _debug_info_callback(value: bool) -> None:
    """Print debug information and exit."""
    if value:
        _print_debug_info()
        raise SystemExit


def _version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        echo(METADATA.full_version, color=False)


@_cli.callback()
def _app_callback(
    version: Annotated[
        bool,
        Option("-V", "--version", callback=_version_callback, help="Show version information."),
    ] = False,
) -> None:
    """bear_gui_tools command-line interface."""


@_cli.command("version", hidden=True, ignore=True)
def _get_version() -> ExitCode:
    """CLI command to get the version of the package."""
    echo(METADATA.version, color=False)
    return ExitCode.SUCCESS


@_cli.command(
    "bump",
    help="Bump the version of the package.",
    usage_text="bear_gui_tools bump [major|minor|patch]",
    ignore=True,
    hidden=True,
)
def _bump_version(bump_type: Annotated[str, Argument(help="◉ Bump type (major, minor, patch)")]) -> ExitCode:
    """CLI command to bump the version of the package."""
    bump: BumpType = cast(BumpType, bump_type.lower())
    return cli_bump(b_type=bump, package_name=METADATA.name, ver=METADATA.version_tuple)


@_cli.command(
    "debug-info",
    help="Print debug information.",
    usage_text="bear_gui_tools debug_info [--no-color]",
    ignore=True,
    hidden=True,
)
def _debug_info(
    no_color: Annotated[
        bool,
        Option("--no-color", "-n", help="Disable colored output."),
    ] = False,
) -> ExitCode:
    """CLI command to print debug information."""
    _print_debug_info(no_color=no_color)
    return ExitCode.SUCCESS


@args_parse()
def main(args: CLIArgsType) -> ExitCode:
    """Entry point for the CLI application.

    This function is executed when you type `bear_gui_tools` or `python -m bear_gui_tools`.

    Parameters:
        args: Arguments passed from the command line.

    Returns:
        An exit code.
    """
    arguments: list[str] = args

    if not args:
        arguments: list[str] = ["--help"]

    try:
        _typer_app()(arguments, prog_name=METADATA.name)
        return ExitCode.SUCCESS
    except SystemExit as e:
        exit_code = e.code
        if isinstance(exit_code, int):
            raise SystemExit(exit_code) from e
        return ExitCode.SUCCESS
    except Exception:
        return ExitCode.FAILURE


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
