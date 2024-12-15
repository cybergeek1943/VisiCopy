from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtGui import QFont
from qfluentwidgets import TitleLabel
from qfluentwidgets import setFont
from ui_lib import ScrollContainer



class TabComponent(QWidget):
    def __init__(self, tab_title: str | None):
        QWidget.__init__(self)

        # Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Title
        if tab_title:
            title = TitleLabel(text=tab_title)
            setFont(title, 24, QFont.Weight.Bold)
            self.layout.addWidget(title)

        # Scrollable Card Container
        self.card_container = ScrollContainer()
        self.layout.addWidget(self.card_container)

    def add_widget(self, w_: QWidget):
        self.card_container.add_widget(w_)

    def clear_widgets(self):
        self.card_container.clear_widgets()

    def get_widgets(self) -> list[QWidget]:
        return self.card_container.get_widgets()

    def widget_count(self) -> int:
        return self.card_container.widget_count()