from .qt import QIcon as QIcon, QObject as QObject
from .tooltip import QToolTipFilter as QToolTipFilter
from qtpy import QtWidgets
from typing import Callable

class QToolButton(QtWidgets.QToolButton):
    def __init__(self, name: str, text: str = '', parent: QObject = None, icon: QIcon = None, tip: str = '', triggered: Callable[[bool], ...] | None = None, toggled: Callable[[bool], ...] | None = None) -> None: ...
