from core.translation import tr
from core.config import user_docs_path
from core import os_utils

# Import Components and Visual Tools
from qfluentwidgets import BodyLabel, HorizontalSeparator, PrimaryPushButton, PushButton
from ui_comps import AlignFlag, SizePolicy, primitives, windows
from PySide6.QtWidgets import QHBoxLayout, QFileDialog
from ui_comps.selection_ui_comps import CustomPathEntryTab, SelectedPath


class SelectionManagerTab(windows.TabComponent):
    def __init__(self):
        super().__init__(tab_title=None)
        self.setObjectName('selection_manager_tab')
        h_lay = QHBoxLayout()
        h_lay.setAlignment(AlignFlag.AlignRight)
        self.layout.addWidget(HorizontalSeparator())
        self.layout.addLayout(h_lay)

        _ = BodyLabel()
        _.setText('<center style="line-height: 0.5;"><h4 style="color: gray;">Drag & Drop Folders</h4>'
                  'or&nbsp;&nbsp;'
                  '<a style="text-decoration: none" href="folder">Add Folder</a>&nbsp;&nbsp;/&nbsp;&nbsp;'
                  '<a style="text-decoration: none" href="path">Add Custom Path</a></center>')
        self.addItemsLinksClicked = _.linkActivated
        h_lay.addItem(primitives.HorizontalExpandSpace())
        h_lay.addWidget(_)
        h_lay.addItem(primitives.HorizontalExpandSpace())

        _ = PushButton()
        _.setText('Clear Selection')
        _.setSizePolicy(SizePolicy.Fixed, SizePolicy.Fixed)
        self.clearButtonClicked = _.clicked
        h_lay.addWidget(_)
        _ = PrimaryPushButton()
        _.setText('Confirm')
        _.setSizePolicy(SizePolicy.Fixed, SizePolicy.Fixed)
        self.confirmButtonClicked = _.clicked
        h_lay.addWidget(_)

    def add_path(self, path: str):
        self.add_widget(SelectedPath(path))


class MainWindow(windows.SubWindow):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setWindowTitle(tr('Select Destination'))
        self.navigationInterface.setReturnButtonVisible(False)
        self.navigationInterface.setMenuButtonVisible(False)
        self.navigationInterface.hide()

        # -------------------------------- Tabs --------------------------------
        # Selection Manager
        self.selection_manager_tab = SelectionManagerTab()
        self.selection_manager_tab.confirmButtonClicked.connect(self.hide)
        self.selection_manager_tab.clearButtonClicked.connect(lambda: self.selection_manager_tab.clear_widgets())
        self.selection_manager_tab.addItemsLinksClicked.connect(lambda href: self.add_folder() if href == 'folder' else self.switchTo(self.custom_path_entry_tab) if href == 'path' else None)
        self.addSubInterface(self.selection_manager_tab, None, 'SelectionManagerTab')

        # Custom Path Entry
        self.custom_path_entry_tab = CustomPathEntryTab()
        self.custom_path_entry_tab.confirmButtonClicked.connect(lambda: (self.add_custom_path(), self.custom_path_entry_tab.custom_path_entry.setText('')))
        self.custom_path_entry_tab.cancelButtonClicked.connect(lambda: (self.switchTo(self.selection_manager_tab), self.custom_path_entry_tab.custom_path_entry.setText('')))
        self.addSubInterface(self.custom_path_entry_tab, None, 'CustomPathEntryTab')

    def get_destination_selection(self) -> list[str]:
        # noinspection PyUnresolvedReferences
        return [w.path for w in self.selection_manager_tab.get_widgets()]

    def clear_destination_selection(self):
        self.selection_manager_tab.clear_widgets()

    def add_folder(self):
        if p := QFileDialog.getExistingDirectory(self, 'Select Folder', user_docs_path):
            self.selection_manager_tab.add_path(p.replace('/', '\\'))
            self.switchTo(self.selection_manager_tab)

    def add_custom_path(self):
        if (p := self.custom_path_entry_tab.custom_path_entry.text()) != '':
            self.selection_manager_tab.add_path(p.replace('/', '\\'))

    def dropEvent(self, event):
        for p in event.mimeData().text().split('\n'):
            if p == '':
                continue
            self.selection_manager_tab.add_path(p) if os_utils.isdir(p := p[8:].replace('/', '\\')) else None

    # noinspection PyMethodMayBeStatic
    def dragEnterEvent(self, event):
        event.acceptProposedAction()
