"""Bear GUI Tools package.

A set of GUI tools for Bear Projects
"""

from bear_gui_tools._internal.cli import main
from bear_gui_tools._internal.debug import METADATA

__version__: str = METADATA.version

from .qt_app import QTApplication
from .qt_color_picker import select_color
from .qt_input_dialog import get_text

__all__: list[str] = ["METADATA", "QTApplication", "__version__", "get_text", "main", "select_color"]
