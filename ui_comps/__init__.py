# Import Pyside6 Classes
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QMessageBox, QSpacerItem
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor, QIcon

#  Import Components
from qfluentwidgets import (BodyLabel as QFLabel,
                            PushButton as QFPushButton,
                            SwitchButton as QFSwitch,
                            ComboBox as QFComboBox,
                            SettingCard as QFSettingCard,
                            FluentWindow as QFluentWindow, TitleLabel, BodyLabel, ImageLabel, HyperlinkButton, SingleDirectionScrollArea)

# Import Utility Classes
from qfluentwidgets import setTheme, Theme, setFont, FluentIcon
import core.config as user_data
from core.translation import tr
from core.asset_paths import logoIconPath

# TODO make Policy module in UI lib
SizePolicy = QSizePolicy.Policy
AlignFlag = Qt.AlignmentFlag
FocusPolicy = Qt.FocusPolicy
FontWeight = QFont.Weight
LayoutDirection = Qt.LayoutDirection

# TODO put all icons in one icon module within UI lib
Icons = FluentIcon


def applyAdditionalStyleSheet(widget: QWidget, stylesheet: str) -> None:
    widget.setStyleSheet(f'{widget.styleSheet()}\n{stylesheet}')


class primitives:
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

    class ImageIcon(ImageLabel):
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

    class ScrollContainer(SingleDirectionScrollArea):
        def __init__(self):
            SingleDirectionScrollArea.__init__(self)
            # self.setFocusPolicy(FocusPolicy.NoFocus)
            self.setStyleSheet("QScrollArea{background: transparent; border: none}")

            view = QWidget()
            view.setStyleSheet("QWidget{background: transparent}")
            self.cards = QVBoxLayout()
            self.cards.setAlignment(AlignFlag.AlignTop)
            view.setLayout(self.cards)
            self.__cards__: list[QWidget] = []

            self.setWidgetResizable(True)
            self.setWidget(view)

        def add_widget(self, w: QWidget):
            self.cards.addWidget(w)
            self.__cards__.append(w)

        def clear_widgets(self) -> None:
            for w in self.__cards__:
                w.deleteLater()
            self.__cards__.clear()

        def get_widgets(self) -> list[QWidget]:
            return self.__cards__

        def widget_count(self) -> int:
            return len(self.__cards__)


class cards:
    class SettingWPushButtons(QFSettingCard):
        def __init__(self, icon: Icons, title: str, label: str, button_labels: tuple[str, ...], button_clicked_slots: tuple[callable, ...]):
            """To connect the button clicked slots pass a tuple of callables to the `button_clicked_slots` argument in the constructor."""
            QFSettingCard.__init__(self, icon=icon, title=title, content=label)
            self.setContentsMargins(10, 0, 20, 0)
            for i, t in enumerate(button_labels):
                button = QFPushButton()
                button.setText(t)
                self.hBoxLayout.addSpacing(8)
                self.hBoxLayout.addWidget(button)
                button.clicked.connect(button_clicked_slots[i])
                setattr(self, str(i), button)

        def setButtonBorderColor(self, button_index: int, hex_: str) -> None:
            applyAdditionalStyleSheet(getattr(self, str(button_index)), f'QPushButton{{border-color: {hex_}; color: {hex_}}}')

    class SettingWSwitch(QFSettingCard):
        def __init__(self, icon: Icons, title: str, label: str, toggled: bool, toggled_slot: callable):
            """To connect the button toggled slot pass a callable to the `toggled_slot` argument in the constructor. The slot must expect a toggled `bool` as its argument."""
            QFSettingCard.__init__(self, icon=icon, title=title, content=label)
            self.setContentsMargins(10, 0, 20, 0)
            switch = QFSwitch()
            switch.setChecked(toggled)
            self.hBoxLayout.addWidget(switch)
            switch.checkedChanged.connect(toggled_slot)

    class SettingWComboBox(QFSettingCard):
        def __init__(self, icon: Icons, title: str, label: str, items: tuple[str, ...], selected_item: int, item_selected_slot: callable):
            """To connect the item selected slot pass a callable to the `item_selected_slot` argument in the constructor. The slot must expect an index `int` as its argument."""
            QFSettingCard.__init__(self, icon=icon, title=title, content=label)
            self.setContentsMargins(10, 0, 20, 0)
            combo = QFComboBox()
            combo.addItems(items)
            combo.setCurrentIndex(selected_item)
            self.hBoxLayout.addWidget(combo)
            combo.currentIndexChanged.connect(item_selected_slot)


class windows:
    class TabWindow(QFluentWindow):  # TODO make better initial resize code
        """Subclass this class to create a window with a sidebar for tabs."""
        def __init__(self, remember_window_pos: bool = False, menu_expand_width: int = 150):
            QFluentWindow.__init__(self)
            self.menu_expand_width: int = menu_expand_width
            self.navigationInterface.setExpandWidth(menu_expand_width)
            self.setWindowIcon(QIcon(logoIconPath))
            setTheme(theme=Theme.DARK if user_data.preferences['theme'] == 0 else Theme.LIGHT if user_data.preferences['theme'] == 1 else Theme.AUTO)  # CRAZY BUG! -> This bug happens when window is opened to full screen using showMaximized() and the setTheme() is called afterwards. To fix this bug simply call setTheme() before calling showMaximized().
            if remember_window_pos:
                self.move(*user_data.preferences['win_pos']) if user_data.preferences['win_pos'] else None
                self.resize(*user_data.preferences['win_size']) if user_data.preferences['win_size'] else None
                self.showMaximized() if user_data.preferences['win_max'] else None
            self.__remember_window_pos: bool = remember_window_pos

        def enterEvent(self, e):
            self.navigationInterface.setExpandWidth(self.menu_expand_width)  # must do this because of crazy bug with the menu expand width being inherited from other windows.

        def closeEvent(self, event):
            if self.__remember_window_pos:
                if self.isMaximized():
                    user_data.preferences['win_max']: tuple = True
                else:
                    user_data.preferences['win_max']: tuple = False
                    user_data.preferences['win_pos']: tuple = self.pos().toTuple()
                    user_data.preferences['win_size']: tuple = self.size().toTuple()
                user_data.save_config()
            event.ignore()

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
            self.card_container = primitives.ScrollContainer()
            self.layout.addWidget(self.card_container)

        def add_widget(self, w_: QWidget):
            self.card_container.add_widget(w_)

        def clear_widgets(self):
            self.card_container.clear_widgets()

        def get_widgets(self) -> list[QWidget]:
            return self.card_container.get_widgets()

        def widget_count(self) -> int:
            return self.card_container.widget_count()

    class SubWindow(TabWindow):
        windowClosing: Signal = Signal()

        def show(self):
            self.activateWindow()
            super().show()

        def closeEvent(self, event):
            self.hide()
            super().closeEvent(event)

        def hide(self):
            self.windowClosing.emit()
            super().hide()


class dialogs:
    response: type[QMessageBox.StandardButton] = QMessageBox.StandardButton

    @staticmethod
    def question(parent: QWidget, title: str, message: str, show_cancel_button: bool = False) -> QMessageBox.StandardButton | int:
        q = QMessageBox(parent)
        q.setIcon(q.Icon.Question)
        q.setWindowTitle(title)
        q.setText(message)
        q.setStandardButtons(q.StandardButton.Yes | q.StandardButton.No | q.StandardButton.Cancel if show_cancel_button else q.StandardButton.Yes | q.StandardButton.No)
        q.button(q.StandardButton.Yes).setText(tr('Yes'))
        q.button(q.StandardButton.No).setText(tr('No'))
        q.button(q.StandardButton.Cancel).setText(tr('Cancel')) if show_cancel_button else None
        return q.exec()

    @staticmethod
    def info(parent: QWidget, title: str, message: str, critical: bool = False) -> QMessageBox.StandardButton | int:
        i = QMessageBox(parent)
        i.setIcon(i.Icon.Critical if critical else i.Icon.Information)
        i.setWindowTitle(title)
        i.setText(message)
        i.setStandardButtons(i.StandardButton.Ok)
        i.button(i.StandardButton.Ok).setText(tr('Ok'))
        return i.exec()


class InfoPageWidget(BodyLabel):
    """This component displays info about VisiCopy"""
    def __init__(self):
        BodyLabel.__init__(self)
        # TODO put in strings resource file
        html: str = tr("""v1.0.0-beta<p>Under the hood, VisiCopy currently utilizes robocopy. In the future, support will be added for rsync and/or rclone."
In addition to the functionality that robocopy provides, VisiCopy introduces features such as multiprocessing & process management;
overall progress (rather than just the progress of a single file); and many other features.</p>
<p>I have developed VisiCopy as a free and open source software. I do not have any contributors yet; hence, this project takes 
a significant amount of time and dedication. You can help the development of this software through donations, code contributions, 
and sharing VisiCopy with others. Any support would be greatly appreciated.</p>
<p>Thank you for using VisiCopy!</p>

<h2>Support</h2>
<a href='https://www.artixios.com/software/visicopy.html'>Download Page</a>
<br/><a href='https://www.artixios.com/software/visicopy.html'>Documentation</a>

<br/><h2>Legal</h2>
License:  GPLv3 (Open Source)
<br/>© 2024 - VisiCopy Trademark

<br/><h2>Developer (Isaac M. Wolford)</h2>
<a href='https://www.artixios.com/about.html#dev_section'>About Me</a>
<br/><a href='https://pay.artixios.com/donate'>Donate Now</a>""")
        self.setWordWrap(True)
        self.setText(html)
        self.setOpenExternalLinks(True)


if __name__ == "__main__":
    pass
    # app = QApplication()
    #
    # window = TabWindow()
    # window.show()
    #
    # app.exec()
