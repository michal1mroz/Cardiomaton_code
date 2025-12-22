from PyQt6.QtWidgets import QWidget, QLabel, QApplication
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath
from PyQt6.QtCore import Qt, QRect, QPoint
from src.frontend.help_view.tutorial_step import TutorialStep


class HelpOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setMouseTracking(True)

        self.targets: list[TutorialStep] = []
        self.active_target: TutorialStep | None = None

        self.tooltip_widget = QLabel(self)
        self.tooltip_widget.setObjectName("tooltip_widget")
        self.tooltip_widget.setVisible(False)
        self.tooltip_widget.setWordWrap(True)
        self.tooltip_widget.setFixedWidth(250)

    def add_target(self, widget: QWidget, title: str, description: str):
        self.targets.append(TutorialStep(widget, title, description))

    def show_tutorial(self):
        if self.parent():
            self.resize(self.parent().size())
            self.show()
            self.raise_()
            self.setFocus()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        path = QPainterPath()
        path.setFillRule(Qt.FillRule.OddEvenFill)
        path.addRect(self.rect().x(), self.rect().y(), self.rect().width(), self.rect().height())

        for target in self.targets:
            if target.widget.isVisible():
                global_pos = target.widget.mapToGlobal(QPoint(0, 0))
                local_pos = self.mapFromGlobal(global_pos)

                target_rect = QRect(local_pos, target.widget.size()).adjusted(-2, -2, 2, 2)
                path.addRoundedRect(target_rect.x(), target_rect.y(), target_rect.width(), target_rect.height(), 10, 10)

        painter.setBrush(QBrush(QColor(0, 0, 0, 180)))
        painter.setPen(Qt.PenStyle.NoPen)

        painter.drawPath(path)

        if self.active_target:
            global_pos = self.active_target.widget.mapToGlobal(QPoint(0, 0))
            local_pos = self.mapFromGlobal(global_pos)
            target_rect = QRect(local_pos, self.active_target.widget.size()).adjusted(-2, -2, 2, 2)

            pen = QPen(QColor("#E1605D"))
            pen.setWidth(3)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(target_rect, 10, 10)

    def mouseMoveEvent(self, event):
        found_target = None

        for target in self.targets:
            if not target.widget.isVisible():
                continue

            global_pos = target.widget.mapToGlobal(QPoint(0, 0))
            local_pos = self.mapFromGlobal(global_pos)
            target_rect = QRect(local_pos, target.widget.size()).adjusted(-2, -2, 2, 2)

            if target_rect.contains(event.pos()):
                found_target = target
                break

        if found_target != self.active_target:
            self.active_target = found_target
            self.update()

            if found_target:
                text = f"<b>{found_target.title}</b><br>{found_target.description}"
                self.tooltip_widget.setText(text)
                self.tooltip_widget.adjustSize()

                tip_w = self.tooltip_widget.width()
                tip_h = self.tooltip_widget.height()

                screen_w = self.width()
                screen_h = self.height()

                cursor_x = event.pos().x()
                cursor_y = event.pos().y()
                offset = 20

                tooltip_x = cursor_x + offset
                tooltip_y = cursor_y + offset

                if tooltip_x + tip_w > screen_w:
                    tooltip_x = cursor_x - tip_w - offset

                if tooltip_y + tip_h > screen_h:
                    tooltip_y = cursor_y - tip_h - offset

                self.tooltip_widget.move(tooltip_x, tooltip_y)
                self.tooltip_widget.show()
                self.tooltip_widget.raise_()
            else:
                self.tooltip_widget.hide()

    def mousePressEvent(self, event):
        self.close_tutorial()

    def close_tutorial(self):
        self.hide()

    def resizeEvent(self, event):
        super().resizeEvent(event)

    def set_steps(self, steps: list[TutorialStep]):
        self.targets = []
        self.targets = steps
        self.update()