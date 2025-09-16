import asyncio
from typing import Optional, List, Callable, Any
from qtpy.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QButtonGroup, QPushButton, QSizePolicy
from qtpy.QtCore import Qt, QTimer
from qtpy.QtGui import QColor
from .button import Button
from qtmui.material.styles.create_theme.components.get_qss_styles import get_qss_style
from qtmui.material.styles import useTheme
class ToggleButton:
    def __init__(self, icon: Optional[str], text: Optional[str], value: Optional[object], selected: bool, *args, **kwargs): ...
    def _init_ui(self): ...
    def _set_stylesheet(self, component_styled): ...