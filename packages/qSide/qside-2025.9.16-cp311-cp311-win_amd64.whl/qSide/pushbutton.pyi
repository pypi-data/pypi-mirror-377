from .qt import QIcon as QIcon, QWidget as QWidget
from qtpy import QtWidgets
from typing import Callable

class QPushButton(QtWidgets.QPushButton):
    def __init__(self, text: str, parent: QWidget | None = None, icon: QIcon | None = None, tip: str = '', triggered: Callable[[bool], ...] | None = None, toggled: Callable[[bool], ...] | None = None) -> None: ...
