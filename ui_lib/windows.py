# Import Pyside6 Classes
from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QApplication
from qfluentwidgets import FluentWindow as QFluentWindow, SimpleCardWidget
from qfluentwidgets import setTheme, Theme
from core.config import config_file
from ui_lib.icons import logoIcon

# Set the theme of the application
setTheme(Theme.DARK if config_file.data['theme'] == 0
else Theme.LIGHT if config_file.data['theme'] == 1 else Theme.AUTO)  # CRAZY BUG! -> This bug happens when window is opened to full screen using showMaximized() and the setTheme() is called afterwards. To fix this bug simply call setTheme() before calling showMaximized().


class Window(QWidget):
    def __init__(self, remember_window_pos: bool = False):
        super().__init__()
        self.setWindowIcon(QIcon(logoIcon))
        if remember_window_pos:
            self.move(*config_file.data['win_pos']) if config_file.data['win_pos'] else None
            self.resize(*config_file.data['win_size']) if config_file.data['win_size'] else None
            self.showMaximized() if config_file.data['win_max'] else None
        self.remembering_window_pos: bool = remember_window_pos

    def closeEvent(self, event):
        """Override this method if one wants to close the window."""
        if self.remembering_window_pos:
            if self.isMaximized():
                config_file.data['win_max']: tuple = True
            else:
                config_file.data['win_max']: tuple = False
                config_file.data['win_pos']: tuple = self.pos().toTuple()
                config_file.data['win_size']: tuple = self.size().toTuple()
            config_file.save()
        event.ignore()


class SubWindow(Window):
    onWindowHidden: Signal = Signal()

    def show(self):
        super().show()
        self.activateWindow()  # If window is hidden, activates the window

    def hide(self):
        super().hide()
        self.onWindowHidden.emit()

    def closeEvent(self, event):
        self.hide()
        super().closeEvent(event)


class FluentWindow(Window, QFluentWindow):
    """Subclass this class to create a window with a sidebar for tabs."""
    def __init__(self, menu_expand_width: int = 150):
        super().__init__(self)
        self.menu_expand_width: int = menu_expand_width
        self.navigationInterface.setExpandWidth(menu_expand_width)

    def enterEvent(self, e):
        self.navigationInterface.setExpandWidth(self.menu_expand_width)  # must do this because of crazy bug with the menu expand width being inherited from other windows.


class SubFluentWindow(FluentWindow):
    pass



if __name__ == '__main__':
    app = QApplication()
    window = FluentWindow()
    window.show()
    app.exec()
