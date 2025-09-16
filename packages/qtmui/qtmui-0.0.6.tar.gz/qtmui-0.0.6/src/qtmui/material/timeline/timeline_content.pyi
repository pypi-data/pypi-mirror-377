import uuid
from qtpy.QtWidgets import QVBoxLayout, QFrame, QSizePolicy
from qtpy.QtCore import Qt
from typing import Union, List, Callable
from ..typography import Typography
from ..box import Box
from qtmui.material.styles import store, useTheme
class AlignBox:
    def __init__(self, **kwargs): ...
class TimelineContent:
    def __init__(self, children, classes: dict, sx: Union[List[Union[Callable, dict, bool]], Callable, dict], text: str): ...
    def _initUI(self): ...