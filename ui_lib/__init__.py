# Import Pyside6 Classes
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSpacerItem
from PySide6.QtGui import QColor

#  Import Components
from qfluentwidgets import (BodyLabel as QFLabel, ImageLabel as QFImageLabel, SingleDirectionScrollArea)

# Import Utility Classes
from qfluentwidgets import setFont
from ui_lib.icons import logoIcon
from ui_lib.policy import *


def applyAdditionalStyleSheet(widget: QWidget, stylesheet: str) -> None:  # TODO maybe move into separate file
    widget.setStyleSheet(f'{widget.styleSheet()}\n{stylesheet}')


class Label(QFLabel):
    def __init__(self, text: str, font_size: int = 14, weight: FontWeight = FontWeight.Normal, dark_color: QColor = QColor(255, 255, 255, 255), light_color: QColor = QColor(0, 0, 0, 255), parent: QWidget = None):
        """Color is Light Gray by default"""
        QFLabel.__init__(self, parent=parent)
        self.setText(text)
        setFont(self, fontSize=font_size, weight=weight)
        self.darkColor = dark_color
        self.lightColor = light_color

    # noinspection PyPropertyAccess
    def setDisabled(self, arg__1):
        self.darkColor: QColor = QColor(*self.darkColor.getRgb()[:3], 100 if arg__1 else 255)
        self.lightColor: QColor = QColor(*self.lightColor.getRgb()[:3], 100 if arg__1 else 255)


class ImageLabel(QFImageLabel):
    def __init__(self, image_path, height: int = 180):
        super().__init__()
        self.setImage(image_path)
        self.scaledToHeight(height)


class HorizontalExpandSpace(QSpacerItem):
    def __init__(self):
        QSpacerItem.__init__(self, 0, 0, SizePolicy.Expanding, SizePolicy.Fixed)


class SpacerItem(QWidget):
    def __init__(self, w: int, h: int):
        super().__init__()
        self.setMinimumSize(w, h)


class VerticalScrollArea(SingleDirectionScrollArea):
    def __init__(self):
        SingleDirectionScrollArea.__init__(self)
        self.setStyleSheet("QScrollArea{background: transparent; border: none}")
        self.setWidgetResizable(True)
        # self.setFocusPolicy(FocusPolicy.NoFocus)


class ScrollView(VerticalScrollArea):
    def __init__(self):
        super().__init__()
        view = QWidget()
        view.setStyleSheet("QWidget{background: transparent}")
        self.widgets = QVBoxLayout()
        view.setLayout(self.widgets)
        self.widgets.setAlignment(AlignFlag.AlignTop)
        self.setWidget(view)
        self.__widgets__: list[QWidget] = []

    def add_widget(self, w: QWidget):
        self.widgets.addWidget(w)
        self.__widgets__.append(w)

    def clear_widgets(self) -> None:
        for w in self.__widgets__:
            w.deleteLater()
        self.__widgets__.clear()

    def get_widgets(self) -> list[QWidget]:
        return self.__widgets__

    def widget_count(self) -> int:
        return len(self.__widgets__)


if __name__ == "__main__":
    pass
