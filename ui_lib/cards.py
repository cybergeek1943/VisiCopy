from qfluentwidgets import (PushButton as QFPushButton,
                            SwitchButton as QFSwitch,
                            ComboBox as QFComboBox,
                            SettingCard as QFSettingCard)
from ui_lib import applyAdditionalStyleSheet
from ui_lib.icons import FluentIcon


class SettingWPushButtons(QFSettingCard):
    def __init__(self, icon: FluentIcon, title: str, label: str, button_labels: tuple[str, ...],
                 button_clicked_slots: tuple[callable, ...]):
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
        applyAdditionalStyleSheet(getattr(self, str(button_index)),
                                  f'QPushButton{{border-color: {hex_}; color: {hex_}}}')


class SettingWSwitch(QFSettingCard):
    def __init__(self, icon: FluentIcon, title: str, label: str, toggled: bool, toggled_slot: callable):
        """To connect the button toggled slot pass a callable to the `toggled_slot` argument in the constructor. The slot must expect a toggled `bool` as its argument."""
        QFSettingCard.__init__(self, icon=icon, title=title, content=label)
        self.setContentsMargins(10, 0, 20, 0)
        switch = QFSwitch()
        switch.setChecked(toggled)
        self.hBoxLayout.addWidget(switch)
        switch.checkedChanged.connect(toggled_slot)


class SettingWComboBox(QFSettingCard):
    def __init__(self, icon: FluentIcon, title: str, label: str, items: tuple[str, ...], selected_item: int,
                 item_selected_slot: callable):
        """To connect the item selected slot pass a callable to the `item_selected_slot` argument in the constructor. The slot must expect an index `int` as its argument."""
        QFSettingCard.__init__(self, icon=icon, title=title, content=label)
        self.setContentsMargins(10, 0, 20, 0)
        combo = QFComboBox()
        combo.addItems(items)
        combo.setCurrentIndex(selected_item)
        self.hBoxLayout.addWidget(combo)
        combo.currentIndexChanged.connect(item_selected_slot)