from os import getenv

from bear_gui_tools import METADATA


def test_config_works() -> None:
    """Test to ensure the env was set"""
    assert getenv(METADATA.env_variable) == "test", "Environment variable not set correctly"


def test_metadata() -> None:
    """Test to ensure metadata is correctly set."""
    assert METADATA.name == "bear-gui-tools", "Metadata name does not match"
    assert METADATA.version != "0.0.0", "Metadata version should not be '0.0.0'"
    assert METADATA.description != "No description available.", "Metadata description should not be empty"
    assert METADATA.project_name == "bear_gui_tools", "Project name does not match"
