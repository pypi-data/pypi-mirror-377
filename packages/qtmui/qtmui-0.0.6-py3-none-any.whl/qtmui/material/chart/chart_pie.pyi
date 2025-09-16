from __future__ import annotations
from typing import Optional, Union, List, Dict
import random
from qtpy.QtCore import QPointF, Qt
from qtpy.QtWidgets import QWidget, QVBoxLayout
from qtpy.QtCharts import QChart, QChartView, QPieSeries, QPieSlice
from qtpy.QtGui import QPainter, QColor, QBrush
from qtmui.material.styles import useTheme
class ChartPie:
    def __init__(self, dir: str, series: Optional[List[Dict]], width: Optional[Union[str, int]], height: Optional[Union[str, int]], options: Optional[Dict], key: str, title: str, *args, **kwargs): ...
    def _init_pie_chart(self): ...
    def _set_stylesheet(self): ...