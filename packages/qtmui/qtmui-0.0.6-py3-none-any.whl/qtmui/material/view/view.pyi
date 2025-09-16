import asyncio
from typing import Callable, Dict, Optional, Union
import uuid
from qtpy.QtWidgets import QFrame, QVBoxLayout, QWidget, QSizePolicy
from qtpy.QtCore import Qt, QTimer
from qtmui.hooks.use_state import State
from ...common.ui_functions import clear_layout
from qtmui.material.styles.create_theme.components.get_qss_styles import get_qss_style
from qtmui.material.styles import useTheme
from ..widget_base import PyWidgetBase
class View:
    def __init__(self, parent, content: State, hightLight: bool, sx: Optional[Union[Callable, str, Dict]], *args, **kwargs): ...
    def _render_ui(self): ...
    def slot_set_stylesheet(self, value): ...
    def _set_stylesheet(self, component_styled): ...