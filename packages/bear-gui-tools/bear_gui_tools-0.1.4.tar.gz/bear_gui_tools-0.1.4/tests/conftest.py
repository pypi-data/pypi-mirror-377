"""Configuration for the pytest test suite."""

from os import environ

from bear_gui_tools import METADATA

environ[f"{METADATA.env_variable}"] = "test"
