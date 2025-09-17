"""Configuration management for Bear GUI Tools."""

from bear_dereth.config.config_manager import ConfigManager
from pydantic import BaseModel, ConfigDict

from bear_gui_tools._internal._info import _ProjectMetadata
from bear_gui_tools._internal.debug import METADATA


class FrozenModel(BaseModel):
    """A Pydantic model that is immutable (frozen)."""

    model_config = ConfigDict(frozen=True)


class Metadata(FrozenModel):
    """Metadata about the application."""

    info_: _ProjectMetadata = METADATA

    def __getattr__(self, name: str) -> str:
        """Delegate attribute access to the internal _ProjectMetadata instance."""
        return getattr(self.info_, name)


class AppConfig(FrozenModel):
    """Application configuration model."""

    env: str = "prod"
    debug: bool = False
    metadata: Metadata = Metadata()


def get_config_manager(env: str = "prod") -> ConfigManager[AppConfig]:
    """Get the configuration manager for the application."""
    return ConfigManager[AppConfig](config_model=AppConfig, program_name=METADATA.name, env=env)


__all__ = ["AppConfig", "get_config_manager"]
