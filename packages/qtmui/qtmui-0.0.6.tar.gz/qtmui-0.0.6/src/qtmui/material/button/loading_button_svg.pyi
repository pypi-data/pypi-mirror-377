from qtpy.QtWidgets import QHBoxLayout
from qtpy.QtCore import Qt
from .button import Button
from .loading_icon import LoadingIcon
from ..py_svg_widget import PySvgWidget
from qtmui.material.styles.create_theme.components.get_qss_styles import get_qss_style
from qtmui.material.styles import useTheme
from qtmui.i18n.use_translation import translate, i18n
class LoadingButton:
    def __init__(self, type: str, loading: bool, loadingPosition: str, loadingIndicator: str, color: str, *args, **kwargs): ...
    def _init_ui(self): ...
    def __set_stylesheet(self, _theme): ...