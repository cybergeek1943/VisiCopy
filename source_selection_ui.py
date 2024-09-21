from core.translation import tr
import core.os_utils as os_utils
from core.config import user_docs_path

# Import Components and Visual Tools
from qfluentwidgets import BodyLabel, HorizontalSeparator, CheckBox, PrimaryPushButton, PushButton
from ui_comps import AlignFlag, SizePolicy, Icons, primitives, windows
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QFileDialog
from core.asset_paths import MainIconPaths
from ui_comps.selection_ui_comps import CustomPathEntryTab, SelectedPath


class SelectedFile(SelectedPath):
    def __init__(self, path: str):
        """
        `path` can take a file path or a dir path (if a file path, then the file path gets converted to a folder path and the file put in selected files.)
        `selected_files` this is the selected files in the dir. If empty, this means that the whole dir is being copied.
        """
        super().__init__(path)
        self.iconLabel.setIcon(Icons.DOCUMENT)
        self.include_dir_checkbox = CheckBox()
        self.include_dir_checkbox.toggled.connect(lambda b: self.__setattr__('include_base_dir', b))
        self.include_dir_checkbox.setChecked(False)
        self.include_dir_checkbox.setText('Include Parent Folder')
        self.include_dir_checkbox.setToolTip('Create the parent folder of this file in the destination and copy this file into it.')
        self.include_dir_checkbox.setToolTipDuration(10000)
        self.include_dir_checkbox.setSizePolicy(SizePolicy.Fixed, SizePolicy.Expanding)
        self.hBoxLayout.addWidget(self.include_dir_checkbox)
        self.hBoxLayout.addSpacing(16)

        # Internal State
        self.include_base_dir: bool = False

    def mouseDoubleClickEvent(self, event):
        if not self.include_dir_checkbox.underMouse():
            super().mouseDoubleClickEvent(event)


class SelectedFolder(SelectedFile):
    def __init__(self, path: str, selected_files: list[str] | None):
        """
        `path` can take a file path or a dir path (if a file path, then the file path gets converted to a folder path and the file put in selected files.)
        `selected_files` this is the selected files in the dir. If empty, this means that the whole dir is being copied.
        """
        super().__init__(path)
        self.iconLabel.setIcon(Icons.FOLDER)
        self.include_dir_checkbox.setChecked(True)
        self.include_dir_checkbox.setText('Include Folder')
        self.include_dir_checkbox.setToolTip("Create this folder in the destination and copy this folder's contents into it.\nOtherwise, only this folder's contents will be copied to the destination.")
        if selected_files:
            self.titleLabel.setText(f'{self.titleLabel.text()}  •  {len(selected_files)}/{os_utils.fileCounter(path, recursive=False)} Files Selected')
            self.include_dir_checkbox.setChecked(False)
            self.include_dir_checkbox.setToolTip("Create this folder in the destination and copy this folder's selected contents into it.\nOtherwise, only this folder's selected contents will be copied to the destination.")

        # Internal State
        self.selected_files: list[str] | None = selected_files


class EmptySelectionTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName('empty_selection_tab')
        v_lay = QVBoxLayout()
        self.setLayout(v_lay)

        v_lay.addWidget(primitives.ImageIcon(MainIconPaths.dragDrop), alignment=AlignFlag.AlignHCenter | AlignFlag.AlignBottom)
        _ = BodyLabel()
        _.setText('<center><h2>Drag and Drop files or folders here</h2>'
                  'or&nbsp;&nbsp;'
                  '<a style="text-decoration: none" href="folder">Select Folder</a>&nbsp;&nbsp;/&nbsp;&nbsp;'
                  '<a style="text-decoration: none" href="file">Select File(s)</a>&nbsp;&nbsp;/&nbsp;&nbsp;'
                  '<a style="text-decoration: none" href="path">Custom Path</a></center>')
        v_lay.addWidget(_, alignment=AlignFlag.AlignHCenter | AlignFlag.AlignTop)
        self.addItemsLinksClicked = _.linkActivated


class SelectionManagerTab(windows.TabComponent):
    def __init__(self):
        super().__init__(tab_title=None)
        self.setObjectName('selection_manager_tab')
        h_lay = QHBoxLayout()
        h_lay.setAlignment(AlignFlag.AlignRight)
        self.layout.addWidget(HorizontalSeparator())
        self.layout.addLayout(h_lay)

        _ = BodyLabel()
        _.setText('<center style="line-height: 0.5;"><h4 style="color: gray;">Drag & Drop files or folders to add more</h4>'
                  'or&nbsp;&nbsp;'
                  '<a style="text-decoration: none" href="folder">Add Folder</a>&nbsp;&nbsp;/&nbsp;&nbsp;'
                  '<a style="text-decoration: none" href="file">Add File(s)</a>&nbsp;&nbsp;/&nbsp;&nbsp;'
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

    def add_paths(self, paths: list[str]):
        dir_selection: list[str] = []
        file_selection: list[str] = []
        for p in paths:
            file_selection.append(p) if os_utils.isfile(p) else dir_selection.append(p)
        for p in dir_selection:
            self.add_widget(SelectedFolder(p, None))
        if len(file_selection) > 1:
            self.add_widget(SelectedFolder(os_utils.getParentDir(file_selection[0]), [os_utils.getPathTarget(p) for p in file_selection]))
        elif len(file_selection) == 1:
            self.add_widget(SelectedFile(file_selection[0]))

    def add_path(self, path: str):
        if os_utils.isfile(path):
            self.add_widget(SelectedFile(path))
        else:
            self.add_widget(SelectedFolder(path, None))


class MainWindow(windows.SubWindow):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setWindowTitle(tr('Select Source'))
        self.navigationInterface.setReturnButtonVisible(False)
        self.navigationInterface.setMenuButtonVisible(False)
        self.navigationInterface.hide()

        # -------------------------------- Tabs --------------------------------
        # Empty Selection
        self.empty_selection_tab = EmptySelectionTab()
        self.empty_selection_tab.addItemsLinksClicked.connect(self.__on_addItemsLinksClicked)
        self.addSubInterface(self.empty_selection_tab, None, 'EmptyTab')

        # Selection Manager
        self.selection_manager_tab = SelectionManagerTab()
        self.selection_manager_tab.confirmButtonClicked.connect(self.hide)
        self.selection_manager_tab.clearButtonClicked.connect(lambda: (self.selection_manager_tab.clear_widgets(), self.switchTo(self.empty_selection_tab)))
        self.selection_manager_tab.addItemsLinksClicked.connect(self.__on_addItemsLinksClicked)
        self.addSubInterface(self.selection_manager_tab, None, 'SelectionManagerTab')

        # Custom Path Entry
        self.custom_path_entry_tab = CustomPathEntryTab()
        self.custom_path_entry_tab.confirmButtonClicked.connect(lambda: (self.add_custom_path(), self.custom_path_entry_tab.custom_path_entry.setText('')))
        self.custom_path_entry_tab.cancelButtonClicked.connect(lambda: (self.switchTo(self.empty_selection_tab) if self.selection_manager_tab.widget_count() == 0 else self.switchTo(self.selection_manager_tab), self.custom_path_entry_tab.custom_path_entry.setText('')))
        self.addSubInterface(self.custom_path_entry_tab, None, 'CustomPathEntryTab')

    def get_source_selection(self) -> list[tuple[str, dict]]:
        # noinspection PyUnresolvedReferences
        return [(w.path, {'selected_files': w.selected_files, 'include_base_dir': w.include_base_dir} if isinstance(w, SelectedFolder) else {'include_base_dir': w.include_base_dir})
                for w in self.selection_manager_tab.get_widgets()]

    def clear_source_selection(self):
        self.selection_manager_tab.clear_widgets()

    def __on_addItemsLinksClicked(self, href: str):
        self.add_folder() if href == 'folder' else self.add_file_s() if href == 'file' else self.switchTo(self.custom_path_entry_tab) if href == 'path' else None

    def add_folder(self):
        if p := QFileDialog.getExistingDirectory(self, 'Select Folder', user_docs_path):
            self.selection_manager_tab.add_path(p.replace('/', '\\'))
            self.switchTo(self.selection_manager_tab)

    def add_file_s(self):
        if (paths := QFileDialog.getOpenFileNames(self, 'Select File(s)', user_docs_path))[0].__len__() != 0:
            self.selection_manager_tab.add_paths([p.replace('/', '\\') for p in paths[0]])
            self.switchTo(self.selection_manager_tab)

    def add_custom_path(self):
        if (p := self.custom_path_entry_tab.custom_path_entry.text()) != '':
            self.selection_manager_tab.add_path(p.replace('/', '\\'))
            self.switchTo(self.selection_manager_tab)
        else:
            self.switchTo(self.empty_selection_tab) if self.selection_manager_tab.widget_count() == 0 else self.switchTo(self.selection_manager_tab)

    def dropEvent(self, event):
        self.selection_manager_tab.add_paths([p[8:].replace('/', '\\') for p in event.mimeData().text().split('\n') if p != ''])
        self.switchTo(self.selection_manager_tab)

    # noinspection PyMethodMayBeStatic
    def dragEnterEvent(self, event):
        event.acceptProposedAction()
