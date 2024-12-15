# Import Pyside6 Classes
from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon

#  Import Components
from qfluentwidgets import FluentWindow as QFluentWindow

# Import Utility Classes
from qfluentwidgets import setTheme, Theme
from core.config import config_file
from ui_lib.icons import logoIcon


class FluentWindow(QFluentWindow):  # TODO make better initial resize code
    """Subclass this class to create a window with a sidebar for tabs."""

    def __init__(self, remember_window_pos: bool = False, menu_expand_width: int = 150):
        QFluentWindow.__init__(self)
        self.menu_expand_width: int = menu_expand_width
        self.navigationInterface.setExpandWidth(menu_expand_width)
        self.setWindowIcon(QIcon(logoIcon))
        setTheme(theme=Theme.DARK if config_file.data['theme'] == 0 else Theme.LIGHT if config_file.data[
                                                                                            'theme'] == 1 else Theme.AUTO)  # CRAZY BUG! -> This bug happens when window is opened to full screen using showMaximized() and the setTheme() is called afterwards. To fix this bug simply call setTheme() before calling showMaximized().
        if remember_window_pos:
            self.move(*config_file.data['win_pos']) if config_file.data['win_pos'] else None
            self.resize(*config_file.data['win_size']) if config_file.data['win_size'] else None
            self.showMaximized() if config_file.data['win_max'] else None
        self.__remember_window_pos: bool = remember_window_pos

    def enterEvent(self, e):
        self.navigationInterface.setExpandWidth(
            self.menu_expand_width)  # must do this because of crazy bug with the menu expand width being inherited from other windows.

    def closeEvent(self, event):
        if self.__remember_window_pos:
            if self.isMaximized():
                config_file.data['win_max']: tuple = True
            else:
                config_file.data['win_max']: tuple = False
                config_file.data['win_pos']: tuple = self.pos().toTuple()
                config_file.data['win_size']: tuple = self.size().toTuple()
            config_file.save()
        event.ignore()


class SubFluentWindow(FluentWindow):
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
