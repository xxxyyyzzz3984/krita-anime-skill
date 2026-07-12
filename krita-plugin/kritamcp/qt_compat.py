"""Small PyQt5/PyQt6 compatibility surface for supported Krita releases."""

from __future__ import annotations

try:
    from PyQt6.QtCore import QByteArray, QEvent, QPoint, QPointF, QRect, Qt, QThread, QTimer
    from PyQt6.QtGui import QColor, QImage, QMouseEvent, QPolygon, QTransform

    QT_MAJOR = 6
except ImportError:
    from PyQt5.QtCore import QByteArray, QEvent, QPoint, QPointF, QRect, Qt, QThread, QTimer
    from PyQt5.QtGui import QColor, QImage, QMouseEvent, QPolygon, QTransform

    QT_MAJOR = 5

if QT_MAJOR == 6:
    LEFT_BUTTON = Qt.MouseButton.LeftButton
    NO_BUTTON = Qt.MouseButton.NoButton
    NO_MODIFIER = Qt.KeyboardModifier.NoModifier
    MOUSE_BUTTON_PRESS = QEvent.Type.MouseButtonPress
    MOUSE_MOVE = QEvent.Type.MouseMove
    MOUSE_BUTTON_RELEASE = QEvent.Type.MouseButtonRelease
else:
    LEFT_BUTTON = Qt.LeftButton
    NO_BUTTON = Qt.NoButton
    NO_MODIFIER = Qt.NoModifier
    MOUSE_BUTTON_PRESS = QEvent.MouseButtonPress
    MOUSE_MOVE = QEvent.MouseMove
    MOUSE_BUTTON_RELEASE = QEvent.MouseButtonRelease


def get_qt_widgets():
    if QT_MAJOR == 6:
        from PyQt6.QtWidgets import QApplication, QWidget
    else:
        from PyQt5.QtWidgets import QApplication, QWidget
    return QApplication, QWidget
