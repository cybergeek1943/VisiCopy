from PySide6.QtWidgets import QWidget, QMessageBox
from core.translation import tr

response: type[QMessageBox.StandardButton] = QMessageBox.StandardButton


def question(parent: QWidget, title: str, message: str, show_cancel_button: bool = False) -> QMessageBox.StandardButton | int:
    q = QMessageBox(parent)
    q.setIcon(q.Icon.Question)
    q.setWindowTitle(title)
    q.setText(message)
    q.setStandardButtons(
        q.StandardButton.Yes | q.StandardButton.No | q.StandardButton.Cancel if show_cancel_button else q.StandardButton.Yes | q.StandardButton.No)
    q.button(q.StandardButton.Yes).setText(tr('Yes'))
    q.button(q.StandardButton.No).setText(tr('No'))
    q.button(q.StandardButton.Cancel).setText(tr('Cancel')) if show_cancel_button else None
    return q.exec()


def info(parent: QWidget, title: str, message: str, critical: bool = False) -> QMessageBox.StandardButton | int:
    i = QMessageBox(parent)
    i.setIcon(i.Icon.Critical if critical else i.Icon.Information)
    i.setWindowTitle(title)
    i.setText(message)
    i.setStandardButtons(i.StandardButton.Ok)
    i.button(i.StandardButton.Ok).setText(tr('Ok'))
    return i.exec()
