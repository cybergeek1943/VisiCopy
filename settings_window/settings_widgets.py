"""Contains all the individual components like buttons and switches used specifically for the VisiCopy Settings. These switches also automatically alter the mutable __variable__ parameter so that they can make changes to settings data automatically."""
# Import Utility Classes
from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import QDate
from core.translation import tr

# Import Components
from qfluentwidgets import (CheckBox as QFCheckBox,
                            ComboBox as QFComboBox,
                            DatePicker as QFDatePicker,
                            SpinBox as QFSpinBox,
                            DoubleSpinBox as QFDoubleSpinBox,
                            LineEdit as QFLineEdit)
from qfluentwidgets.components.widgets.switch_button import Indicator as QFSwitch  # we do this because the normal SwitchButton has On and Off text which is inconvenient for our purposes.
from ui_lib import Label
from qfluentwidgets import setTheme, Theme
setTheme(Theme.DARK)  # TODO we may not want this here.


# noinspection PyUnresolvedReferences
class __hierarchy_manager__:
    """This class must be subclassed by elements that need hierarchy"""
    def __init__(self):
        self.__children__: list = []  # add children elements to this after subclass initialization
        self.disabled: bool = False

    def set_disabled(self, b: bool, __disable_children__: bool = True, __update_variable__: bool = True) -> None:
        self.disabled = b
        self.setDisabled(b)  # This is a method of the subclasses. Any widget that is disabled has all its children disabled as well.
        if self.__dict__.__contains__('label'):  # we must do this because the Label object has its own overridden setDisabled() for changing it's disabled color state
            self.label.setDisabled(b)
        if __disable_children__ and self.toggled:  # we must check if self is toggled so that when the parent is switched on again the children widgets of self still stay disabled if self.toggled is off.
            self.__disable_children__(b)
        if __update_variable__:
            self.__variable__['disabled']: bool = b

    def __disable_children__(self, b: bool) -> None:
        for elem in self.__children__:
            elem.set_disabled(b)


class Switch(__hierarchy_manager__, QWidget):
    def __init__(self, toggled: bool, label: str, sub_pos: int, __variable__: dict, parent: QWidget = None) -> None:
        QWidget.__init__(self, parent=parent)
        __hierarchy_manager__.__init__(self)
        self.__variable__: dict = __variable__
        self.toggled: bool = toggled

        # Set Layout
        layout = QHBoxLayout()
        self.setLayout(layout)

        # sub_pos
        if sub_pos != 0:
            layout.addSpacing(45 * sub_pos)

        # Switch
        self.switch = QFSwitch(self)
        self.switch.setChecked(toggled)
        layout.addWidget(self.switch)
        self.switch.checkedChanged.connect(self.__on_toggled)

        # Label
        self.label = Label(label)
        layout.addWidget(self.label)

    def __on_toggled(self, toggled: bool) -> None:
        self.__variable__['toggled']: bool = toggled
        self.__disable_children__(not toggled)
        self.toggled = toggled


class CheckBox(__hierarchy_manager__, QWidget):
    def __init__(self, toggled: bool, label: str, sub_pos: int, __variable__: dict, parent: QWidget = None) -> None:
        QWidget.__init__(self, parent=parent)
        __hierarchy_manager__.__init__(self)
        self.__variable__: dict = __variable__
        self.toggled: bool = toggled

        # Set Layout
        layout = QHBoxLayout()
        self.setLayout(layout)

        # sub_pos
        if sub_pos != 0:
            layout.addSpacing(45 * sub_pos)

        # CheckBox
        self.checkbox = QFCheckBox()
        self.checkbox.setText(label)
        self.checkbox.setChecked(toggled)
        layout.addWidget(self.checkbox)
        self.checkbox.checkStateChanged.connect(self.__on_toggled)

    def __on_toggled(self) -> None:
        toggled = self.checkbox.isChecked()
        self.__variable__['toggled']: bool = toggled
        self.__disable_children__(not toggled)
        self.toggled = toggled


class SwitchStrEntry(__hierarchy_manager__, QWidget):
    def __init__(self, toggled: bool, label: str, entry: str, placeholder: str, width_factor: int, sub_pos: int, __variable__: dict, parent: QWidget = None) -> None:
        QWidget.__init__(self, parent=parent)
        __hierarchy_manager__.__init__(self)
        self.__variable__: dict = __variable__
        self.toggled: bool = toggled

        # Set Layout
        layout = QHBoxLayout()
        self.setLayout(layout)

        # sub_pos
        if sub_pos != 0:
            layout.addSpacing(45 * sub_pos)

        # Switch
        self.switch = QFSwitch(self)
        self.switch.setChecked(toggled)
        layout.addWidget(self.switch)
        self.switch.checkedChanged.connect(self.__on_toggled)

        # Label
        self.label = Label(f'{label}: ')
        layout.addWidget(self.label)

        # Entry Box
        self.entry = QFLineEdit()
        self.entry.setText(entry)
        self.entry.setPlaceholderText(placeholder)
        self.entry.setDisabled(not toggled)
        self.entry.setMinimumWidth(self.entry.sizeHint().width() * width_factor) if width_factor != 0 else None
        layout.addWidget(self.entry)
        self.entry.editingFinished.connect(self.__on_entry_confirmed)

    def __on_toggled(self, toggled: bool) -> None:
        self.__variable__['toggled']: bool = toggled
        self.__disable_children__(not toggled)
        self.toggled = toggled
        self.entry.setDisabled(not toggled)

    def __on_entry_confirmed(self):
        self.entry.clearFocus()
        self.__variable__['entry']: str = self.entry.text()


class SwitchNumEntry(__hierarchy_manager__, QWidget):
    def __init__(self, toggled: bool, label: str, entry: int | float, min_entry: int | float, max_entry: int | float, width_factor: int, sub_pos: int, __variable__: dict, parent: QWidget = None) -> None:
        QWidget.__init__(self, parent=parent)
        __hierarchy_manager__.__init__(self)
        self.__variable__: dict = __variable__
        self.toggled: bool = toggled

        # Set Layout
        layout = QHBoxLayout()
        self.setLayout(layout)

        # sub_pos
        if sub_pos != 0:
            layout.addSpacing(45 * sub_pos)

        # Switch
        self.switch = QFSwitch(self)
        self.switch.setChecked(toggled)
        layout.addWidget(self.switch)
        self.switch.checkedChanged.connect(self.__on_toggled)

        # Label
        self.label = Label(f'{label}: ')
        layout.addWidget(self.label)

        # Entry Box

        if type(entry) is int:
            self.entry = QFSpinBox()
            self.entry.setValue(entry)
            self.entry.setMinimum(min_entry)
            self.entry.setMaximum(max_entry)
        else:
            self.entry = QFDoubleSpinBox()
            self.entry.setDecimals(3)
            self.entry.setSingleStep(0.001)
            self.entry.setValue(entry)
            self.entry.setMinimum(min_entry)
            self.entry.setMaximum(max_entry)
        self.entry.setDisabled(not toggled)
        self.entry.setMinimumWidth(150 if width_factor == 0 else 150 * width_factor)
        layout.addWidget(self.entry)
        self.entry.editingFinished.connect(self.__on_entry_confirmed)

    def __on_toggled(self, toggled: bool) -> None:
        self.__variable__['toggled']: bool = toggled
        self.__disable_children__(not toggled)
        self.toggled = toggled
        self.entry.setDisabled(not toggled)

    def __on_entry_confirmed(self):
        self.__variable__['entry']: int = self.entry.value()
        self.entry.clearFocus()


class SwitchSizeEntry(__hierarchy_manager__, QWidget):
    def __init__(self, toggled: bool, label: str, entry: int, min_entry: int, max_entry: int, size_options: list | tuple, selected_option: int, width_factor: int, sub_pos: int, __variable__: dict, parent: QWidget = None) -> None:
        QWidget.__init__(self, parent=parent)
        __hierarchy_manager__.__init__(self)
        self.__variable__: dict = __variable__
        self.toggled: bool = toggled

        # Set Layout
        layout = QHBoxLayout()
        self.setLayout(layout)

        # sub_pos
        if sub_pos != 0:
            layout.addSpacing(45 * sub_pos)

        # Switch
        self.switch = QFSwitch(self)
        self.switch.setChecked(toggled)
        layout.addWidget(self.switch)
        self.switch.checkedChanged.connect(self.__on_toggled)

        # Label
        self.label = Label(f'{label}: ')
        layout.addWidget(self.label)

        # Entry Box
        self.entry = QFSpinBox()
        self.entry.setValue(entry)
        self.entry.setMinimum(min_entry)
        self.entry.setMaximum(max_entry)
        self.entry.setDisabled(not toggled)
        self.entry.setMinimumWidth(150 if width_factor == 0 else 150 * width_factor)
        layout.addWidget(self.entry)
        self.entry.editingFinished.connect(self.__on_entry_confirmed)

        # Size ComboBox
        self.size_combo = QFComboBox()
        self.size_combo.addItems(size_options)
        self.size_combo.setCurrentIndex(selected_option)
        self.size_combo.setDisabled(not toggled)
        layout.addWidget(self.size_combo)
        self.size_combo.currentIndexChanged.connect(self.__on_size_option_changed)

    def __on_toggled(self, toggled: bool) -> None:
        self.__variable__['toggled']: bool = toggled
        self.__disable_children__(not toggled)
        self.toggled = toggled
        self.entry.setDisabled(not toggled)
        self.size_combo.setDisabled(not toggled)

    def __on_entry_confirmed(self):
        self.__variable__['entry']: int = self.entry.value()
        self.entry.clearFocus()

    def __on_size_option_changed(self, index: int):
        self.__variable__['selected_option']: int = index


class SwitchDateEntry(__hierarchy_manager__, QWidget):
    def __init__(self, toggled: bool, label: str, day: int, month: int, year: int, use_days: bool, days: int, min_days: int, max_days: int, sub_pos: int, __variable__: dict, parent: QWidget = None) -> None:
        QWidget.__init__(self, parent=parent)
        __hierarchy_manager__.__init__(self)
        self.__variable__: dict = __variable__
        self.toggled: bool = toggled

        # Set Layout
        layout = QHBoxLayout()
        self.setLayout(layout)

        # sub_pos
        if sub_pos != 0:
            layout.addSpacing(45 * sub_pos)

        # Switch
        self.switch = QFSwitch(self)
        self.switch.setChecked(toggled)
        layout.addWidget(self.switch)
        self.switch.checkedChanged.connect(self.__on_toggled)

        # Label
        self.label = Label(f'{label}: ')
        layout.addWidget(self.label)

        # Date Picker
        self.date_picker = QFDatePicker()
        self.date_picker.setDate(QDate(year, month, day))
        self.date_picker.setDisabled(not toggled)
        layout.addWidget(self.date_picker)
        self.date_picker.dateChanged.connect(self.__on_date_changed)

        # Days Entry
        self.days_entry = QFSpinBox()
        self.days_entry.setValue(days)
        self.days_entry.setMinimum(min_days)
        self.days_entry.setMaximum(max_days)
        self.days_entry.setDisabled(not toggled)
        self.days_entry.setMinimumWidth(150)
        layout.addWidget(self.days_entry)
        self.days_entry.editingFinished.connect(self.__on_days_confirmed)

        if use_days:
            self.date_picker.hide()
            self.days_entry.show()
        else:
            self.date_picker.show()
            self.days_entry.hide()

        # Days or Date ComboBox
        self.combo = QFComboBox()
        self.combo.addItems((tr('Date'), tr('Days')))
        self.combo.setDisabled(not toggled)
        self.combo.setCurrentIndex(1 if use_days else 0)
        layout.addWidget(self.combo)
        self.combo.currentIndexChanged.connect(self.__on_use_days_swapped)

    def __on_toggled(self, toggled: bool) -> None:
        self.__variable__['toggled']: bool = toggled
        self.__disable_children__(not toggled)
        self.toggled = toggled
        self.date_picker.setDisabled(not toggled)
        self.days_entry.setDisabled(not toggled)
        self.combo.setDisabled(not toggled)

    def __on_use_days_swapped(self, idx: int):
        if idx == 0:
            self.__variable__['use_days']: bool = False
            self.date_picker.show()
            self.days_entry.hide()
        elif idx == 1:
            self.__variable__['use_days']: bool = True
            self.date_picker.hide()
            self.days_entry.show()

    def __on_days_confirmed(self):
        self.days_entry.clearFocus()
        self.__variable__['days']: int = self.days_entry.value()

    def __on_date_changed(self, date: QDate):
        self.__variable__['year']: int = date.year()
        self.__variable__['month']: int = date.month()
        self.__variable__['day']: int = date.day()


class SwitchDropdown(__hierarchy_manager__, QWidget):
    def __init__(self, toggled: bool, options: list | tuple, selected_option: int, sub_pos: int, __variable__: dict, parent: QWidget = None):
        QWidget.__init__(self, parent=parent)
        __hierarchy_manager__.__init__(self)
        self.__variable__: dict = __variable__
        self.toggled: bool = toggled

        # Set Layout
        layout = QHBoxLayout()
        self.setLayout(layout)

        # sub_pos
        if sub_pos != 0:
            layout.addSpacing(45 * sub_pos)

        # Switch
        self.switch = QFSwitch(self)
        self.switch.setChecked(toggled)
        layout.addWidget(self.switch)
        self.switch.checkedChanged.connect(self.__on_toggled)

        # Combo Box
        self.combo = QFComboBox()
        self.combo.addItems(options)
        self.combo.setCurrentIndex(selected_option)
        self.combo.setDisabled(not toggled)
        layout.addWidget(self.combo)
        self.combo.currentIndexChanged.connect(self.__on_item_selected)

    def __on_item_selected(self, index: int):
        self.__variable__['selected_option']: int = index

    def __on_toggled(self, toggled: bool):
        self.__variable__['toggled']: bool = toggled
        self.__disable_children__(not toggled)
        self.toggled = toggled
        self.combo.setDisabled(not toggled)


class Constant(__hierarchy_manager__, QWidget):
    def __init__(self, label: str, sub_pos: int, __variable__: dict, parent: QWidget = None):
        QWidget.__init__(self, parent=parent)
        __hierarchy_manager__.__init__(self)
        self.__variable__: dict = __variable__
        self.toggled: bool = True

        # Set Layout
        layout = QHBoxLayout()
        self.setLayout(layout)

        # sub_pos
        if sub_pos != 0:
            layout.addSpacing(45 * sub_pos)

        # Label
        self.label = Label(label)
        layout.addWidget(self.label)


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QVBoxLayout
    app = QApplication()

    window = QWidget()
    l = QVBoxLayout()
    w1 = SwitchNumEntry(True, 'Test1', 0, min_entry=0, max_entry=45, width_factor=0, sub_pos=0, __variable__={})
    l.addWidget(w1)
    window.setLayout(l)
    window.show()

    app.exec()
