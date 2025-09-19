#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" custom_widgets

This modules contains custom widgets.

Contains classes:
    * Toggle - round toggle button switching between two positions
    * AnimatedToggle - animates the Toggle switch
    * FileInfoWidget - table-like widget filed with metadata from file

modified from qt-widgets: github.com/pythonguis/python-qtwidgets

"""

from typing import Optional

import math

from PySide6.QtCore import (
    Qt, QSize, QPoint, QPointF, QRectF, QTimer, QRect,
    QEasingCurve, QPropertyAnimation, QSequentialAnimationGroup, QAbstractAnimation
)

from PySide6.QtCore import Slot, Property

from PySide6.QtWidgets import (
    QWidget, QCheckBox, QStyle, QProxyStyle, QStyleOption, QTabBar, QDockWidget, QMainWindow
)

from PySide6.QtGui import QColor, QBrush, QPaintEvent, QPen, QPainter, QIcon


class IconDockStyle(QProxyStyle):

    # adapted from https://stackoverflow.com/a/3482795

    def __init__(self, icon: QIcon, style: Optional[QStyle] = None):
        super().__init__(style)
        self.icon = icon

    def drawControl(self, element: QStyle.ControlElement, option: QStyleOption, painter: QPainter,
                    widget: Optional[QWidget] = None) -> None:
        if element == QStyle.ControlElement.CE_DockWidgetTitle:
            # width of the icon
            width: int = self.pixelMetric(QStyle.PixelMetric.PM_TabBarIconSize)
            # margin of title from frame
            margin: int = self.baseStyle().pixelMetric(QStyle.PixelMetric.PM_DockWidgetTitleMargin)
            icon_point = QPoint(margin + option.rect.left(),
                                margin + option.rect.center().y() - width//2)
            painter.drawPixmap(icon_point, self.icon.pixmap(width, width))
            option.rect = option.rect.adjusted(width, 0, 0, 0)
        self.baseStyle().drawControl(element, option, painter, widget)


def add_icon_to_tab(window: QMainWindow, tab_name: str, icon: QIcon):
    # adapted from https://stackoverflow.com/a/46623219
    def f(_):
        try:
            for tabbar in window.findChildren((QTabBar)):
                for i in range(tabbar.count()):
                    if tabbar.tabText(i) == tab_name:
                        tabbar.setTabIcon(i, icon)
        except RuntimeError:
            # window has been deleted
            pass
    return f


class IconDockWidget(QDockWidget):

    def __init__(self, name: str, parent: QWidget, icon: QIcon):
        assert isinstance(parent, QMainWindow)
        super().__init__(name, parent)
        self.setStyle(IconDockStyle(icon))
        self.visibilityChanged.connect(add_icon_to_tab(parent, name, icon))


class Toggle(QCheckBox):

    _transparent_pen = QPen(Qt.GlobalColor.transparent)
    _light_grey_pen = QPen(Qt.GlobalColor.lightGray)

    def __init__(self, parent=None, bar_color: QColor = QColor("gray"),
                 checked_color: QColor = QColor("white"), handle_color: QColor = QColor("white")):
        super().__init__(parent)
        # Save our properties on the object via self, so we can access them
        # later in the paintEvent.
        self._bar_brush = QBrush(bar_color)
        self._bar_checked_brush = QBrush(QColor(checked_color).lighter())
        self._handle_brush = QBrush(handle_color)
        self._handle_checked_brush = QBrush(QColor(checked_color))
        # Setup the rest of the widget.
        self.setContentsMargins(8, 0, 8, 0)
        self._handle_position = 0
        self.stateChanged.connect(self.handle_state_change)

    def sizeHint(self) -> QSize:
        return QSize(58, 45)

    def hitButton(self, pos: QPoint) -> bool:
        return self.contentsRect().contains(pos)

    def paintEvent(self, e: QPaintEvent) -> None:
        # pylint: disable=missing-function-docstring, invalid-name, unused-argument
        contRect = self.contentsRect()
        handleRadius = round(0.24 * contRect.height())

        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        p.setPen(self._transparent_pen)
        barRect = QRectF(
            0, 0,
            contRect.width() - handleRadius, 0.40 * contRect.height()
        )
        barRect.moveCenter(contRect.center())
        rounding = barRect.height() / 2

        # the handle will move along this line
        trailLength = contRect.width() - 2 * handleRadius
        xPos = (
            contRect.x() + handleRadius + trailLength * self._handle_position
        )

        if self.isChecked():
            p.setBrush(self._bar_checked_brush)
            p.drawRoundedRect(barRect, rounding, rounding)
            p.setPen(self._light_grey_pen)

            p.setBrush(self._handle_checked_brush)

        else:
            p.setBrush(self._bar_brush)
            p.drawRoundedRect(barRect, rounding, rounding)
            p.setPen(self._light_grey_pen)
            p.setBrush(self._handle_brush)

        p.drawEllipse(
            QPointF(xPos, barRect.center().y()),
            handleRadius, handleRadius)

        p.end()

    @Slot(int)
    def handle_state_change(self, value: int) -> None:
        self._handle_position = 1 if value else 0

    @Property(float)
    def handle_position(self) -> float:
        return self._handle_position

    @handle_position.setter
    def handle_position(self, pos):
        """change the property
        we need to trigger QWidget.update() method, either by:
            1- calling it here [ what we're doing ].
            2- connecting the QPropertyAnimation.valueChanged() signal to it.
        """
        self._handle_position = pos
        self.update()

    @Property(float)
    def pulse_radius(self):
        return self._pulse_radius

    @pulse_radius.setter
    def pulse_radius(self, pos):
        self._pulse_radius = pos
        self.update()


class AnimatedToggle(Toggle):

    _transparent_pen = QPen(Qt.GlobalColor.transparent)
    _light_grey_pen = QPen(Qt.GlobalColor.lightGray)

    def __init__(self,
                 *args,
                 pulse_unchecked_color="#44999999",
                 pulse_checked_color="#44999999",
                 **kwargs):

        self._pulse_radius: float = 0

        super().__init__(*args, **kwargs)

        self.animation = QPropertyAnimation(self, b"handle_position", self)
        self.animation.setEasingCurve(QEasingCurve.InOutCubic)
        self.animation.setDuration(200)  # time in ms

        self.pulse_anim = QPropertyAnimation(self, b"pulse_radius", self)
        self.pulse_anim.setDuration(350)  # time in ms
        self.pulse_anim.setStartValue(10)
        self.pulse_anim.setEndValue(20)

        self.animations_group = QSequentialAnimationGroup()
        self.animations_group.addAnimation(self.animation)
        self.animations_group.addAnimation(self.pulse_anim)

        self._pulse_unchecked_animation = QBrush(QColor(pulse_unchecked_color))
        self._pulse_checked_animation = QBrush(QColor(pulse_checked_color))

    @Slot(int)
    def handle_state_change(self, value):
        self.animations_group.stop()
        if value:
            self.animation.setEndValue(1)
        else:
            self.animation.setEndValue(0)
        self.animations_group.start()

    def paintEvent(self, e: QPaintEvent):

        contRect = self.contentsRect()
        handleRadius = int(round(0.24 * contRect.height()))

        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        p.setPen(self._transparent_pen)
        barRect = QRectF(
            0, 0,
            contRect.width() - handleRadius, handleRadius*2
            # 0.25 * contRect.height()
        )
        barRect.moveCenter(contRect.center())
        rounding = barRect.height() / 2

        # the handle will move along this line
        trailLength = contRect.width() - 2 * handleRadius

        xPos = (
            contRect.x() + handleRadius + trailLength * self._handle_position
        )

        if self.pulse_anim.state() == QAbstractAnimation.State.Running:
            p.setBrush(
                self._pulse_checked_animation if
                self.isChecked() else self._pulse_unchecked_animation)
            p.drawEllipse(QPointF(xPos, barRect.center().y()),
                          self._pulse_radius, self._pulse_radius)

        if self.isChecked():
            p.setBrush(self._bar_checked_brush)
            p.setPen(self._light_grey_pen)
            p.drawRoundedRect(barRect, rounding, rounding)
            p.setBrush(self._handle_checked_brush)

        else:
            p.setBrush(self._bar_brush)
            p.setPen(self._light_grey_pen)
            p.drawRoundedRect(barRect, rounding, rounding)
            p.setBrush(self._handle_brush)

        p.drawEllipse(
            QPointF(xPos, barRect.center().y()),
            handleRadius, handleRadius)

        p.setBrush(Qt.GlobalColor.black)
        p.drawPie(int(xPos)-handleRadius,
                  int(barRect.center().y())-handleRadius,
                  handleRadius*2,
                  handleRadius*2,
                  90*16,
                  180*16)

        # text under icon:
        # p.setPen(Qt.black)
        # small_font = p.font()
        # small_font.setPointSize(p.font().pointSize()//2)
        # p.setFont(small_font)
        # p.drawText(contRect,
        #            (Qt.AlignCenter | Qt.AlignBottom),
        #            'background \ncolor')

        p.end()


# from https://github.com/z3ntu/QtWaitingSpinner

class QtWaitingSpinner(QWidget):

    def __init__(self, parent, centerOnParent=True, disableParentWhenSpinning=True, modality=Qt.NonModal):
        super().__init__(parent)

        self._centerOnParent = centerOnParent
        self._disableParentWhenSpinning = disableParentWhenSpinning

        # WAS IN initialize()
        self._color = QColor(Qt.black)
        self._roundness = 50.0
        self._minimumTrailOpacity = 30
        self._trailFadePercentage = 60.0
        self._revolutionsPerSecond = 1
        self._numberOfLines = 12
        self._lineLength = 10
        self._lineWidth = 2
        self._innerRadius = 10
        self._currentCounter = 0
        self._isSpinning = False

        self._timer = QTimer(self)
        self._timer.timeout.connect(self.rotate)
        self.updateSize()
        self.updateTimer()
        self.hide()
        # END initialize()

        self.setWindowModality(modality)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def paintEvent(self, event: Optional[QPaintEvent]):
        self.updatePosition()
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.GlobalColor.transparent)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        if self._currentCounter >= self._numberOfLines:
            self._currentCounter = 0

        painter.setPen(Qt.PenStyle.NoPen)
        for i in range(0, self._numberOfLines):
            painter.save()
            painter.translate(self._innerRadius + self._lineLength,
                              self._innerRadius + self._lineLength)
            rotateAngle = float(360 * i) / float(self._numberOfLines)
            painter.rotate(rotateAngle)
            painter.translate(self._innerRadius, 0)
            distance = self.lineCountDistanceFromPrimary(
                i, self._currentCounter, self._numberOfLines)
            color = self.currentLineColor(distance, self._numberOfLines, self._trailFadePercentage,
                                          self._minimumTrailOpacity, self._color)
            painter.setBrush(color)
            rect = QRect(0, int(-self._lineWidth / 2), int(self._lineLength), int(self._lineWidth))
            painter.drawRoundedRect(rect, self._roundness, self._roundness,
                                    Qt.SizeMode.RelativeSize)
            painter.restore()

    def start(self):
        self.updatePosition()
        self._isSpinning = True
        self.show()
        if self.parentWidget and self._disableParentWhenSpinning:
            self.parentWidget().setEnabled(False)
        if not self._timer.isActive():
            self._timer.start()
            self._currentCounter = 0

    def stop(self):
        self._isSpinning = False
        self.hide()

        if self.parentWidget() and self._disableParentWhenSpinning:
            self.parentWidget().setEnabled(True)

        if self._timer.isActive():
            self._timer.stop()
            self._currentCounter = 0

    def setNumberOfLines(self, lines):
        self._numberOfLines = lines
        self._currentCounter = 0
        self.updateTimer()

    def setLineLength(self, length):
        self._lineLength = length
        self.updateSize()

    def setLineWidth(self, width):
        self._lineWidth = width
        self.updateSize()

    def setInnerRadius(self, radius):
        self._innerRadius = radius
        self.updateSize()

    def color(self):
        return self._color

    def roundness(self):
        return self._roundness

    def minimumTrailOpacity(self):
        return self._minimumTrailOpacity

    def trailFadePercentage(self):
        return self._trailFadePercentage

    def revolutionsPersSecond(self):
        return self._revolutionsPerSecond

    def numberOfLines(self):
        return self._numberOfLines

    def lineLength(self):
        return self._lineLength

    def lineWidth(self):
        return self._lineWidth

    def innerRadius(self):
        return self._innerRadius

    def isSpinning(self):
        return self._isSpinning

    def setRoundness(self, roundness):
        self._roundness = max(0.0, min(100.0, roundness))

    def setColor(self, color=Qt.black):
        self._color = QColor(color)

    def setRevolutionsPerSecond(self, revolutionsPerSecond):
        self._revolutionsPerSecond = revolutionsPerSecond
        self.updateTimer()

    def setTrailFadePercentage(self, trail):
        self._trailFadePercentage = trail

    def setMinimumTrailOpacity(self, minimumTrailOpacity):
        self._minimumTrailOpacity = minimumTrailOpacity

    def rotate(self):
        self._currentCounter += 1
        if self._currentCounter >= self._numberOfLines:
            self._currentCounter = 0
        self.update()

    def updateSize(self):
        size = int((self._innerRadius + self._lineLength) * 2)
        self.setFixedSize(size, size)

    def updateTimer(self):
        self._timer.setInterval(int(1000 / (self._numberOfLines * self._revolutionsPerSecond)))

    def updatePosition(self):
        if self.parentWidget() and self._centerOnParent:
            self.move(int(self.parentWidget().width() / 2 - self.width() / 2),
                      int(self.parentWidget().height() / 2 - self.height() / 2))

    def lineCountDistanceFromPrimary(self, current, primary, totalNrOfLines):
        distance = primary - current
        if distance < 0:
            distance += totalNrOfLines
        return distance

    def currentLineColor(self, countDistance, totalNrOfLines, trailFadePerc, minOpacity, colorinput):
        color = QColor(colorinput)
        if countDistance == 0:
            return color
        minAlphaF = minOpacity / 100.0
        distanceThreshold = int(math.ceil((totalNrOfLines - 1) * trailFadePerc / 100.0))
        if countDistance > distanceThreshold:
            color.setAlphaF(minAlphaF)
        else:
            alphaDiff = color.alphaF() - minAlphaF
            gradient = alphaDiff / float(distanceThreshold + 1)
            resultAlpha = color.alphaF() - gradient * countDistance
            # If alpha is out of bounds, clip it.
            resultAlpha = min(1.0, max(0.0, resultAlpha))
            color.setAlphaF(resultAlpha)
        return color
