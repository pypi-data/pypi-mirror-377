import uuid
from qtpy.QtWidgets import QVBoxLayout, QFrame, QSizePolicy
from qtpy.QtCore import Qt
from typing import Union, List, Callable
from ..typography import Typography
class TimelineOppositeContent:
    def __init__(self, children, classes: dict, sx: Union[List[Union[Callable, dict, bool]], Callable, dict], text: str): ...
    def _initUI(self): ...