"""Contains reusable components for the source and destination selection code."""
import core.os_utils as os_utils

# Import Components and Visual Tools
from qfluentwidgets import (BodyLabel, HorizontalSeparator, LineEdit, SettingCard, PrimaryPushButton, PushButton)
from ui_comps import AlignFlag, SizePolicy, Icons, windows
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtCore import Qt


class CustomPathEntryTab(windows.TabComponent):
    def __init__(self):
        super().__init__(tab_title=None)
        self.setObjectName('custom_path_entry_tab')

        self.custom_path_entry = LineEdit()
        self.custom_path_entry.setPlaceholderText('Custom Path')
        self.layout.insertWidget(0, self.custom_path_entry)

        _ = BodyLabel()
        _.setWordWrap(True)
        _.setText(r"""<h4>You may enter the fallowing:</h4>
        <ul>
            <li>Remote Path (UNC Paths, Shared Folder Links, etc.)</li>
            <li>Local Path (somewhere on this computer)</li>
        </ul>

        <h4>Using remote paths you can copy files from/to servers or other computers:</h4>
        <ul>
            <li>Make sure both computers are connected to the same network.</li>
            <li>Right Click on a folder you want to copy from/to another computer.</li>
            <li>Navigate to "Properties" and then click on the "Sharing" tab.</li>
            <li>Then Click on "Advanced Sharing", enable "Share this folder", and click "Apply". If you want this shared folder to be the destination you must also click on "Permissions" and check the "Full Control" box.</li>
            <li>Enter the network path as the custom path above. It should look like "\\(Computer Name or IP Address)\(Name of shared folder)".</li>
        </ul>

        Note that you may first need to enter the path into the "run" program (using "⊞+r") to access the shared folder by entering a Microsoft account or a Local account's credentials of the other computer.
        """)
        self.add_widget(_)

        h_lay = QHBoxLayout()
        h_lay.setAlignment(AlignFlag.AlignRight)
        self.layout.addWidget(HorizontalSeparator())
        self.layout.addLayout(h_lay)

        _ = PushButton()
        _.setText('Cancel')
        _.setSizePolicy(SizePolicy.Fixed, SizePolicy.Fixed)
        self.cancelButtonClicked = _.clicked
        h_lay.addWidget(_)
        _ = PrimaryPushButton()
        _.setText('Confirm')
        _.setSizePolicy(SizePolicy.Fixed, SizePolicy.Fixed)
        self.confirmButtonClicked = _.clicked
        h_lay.addWidget(_)


class SelectedPath(SettingCard):
    def __init__(self, path: str):
        """
        `path` can take a file path or a dir path (if a file path, then the file path gets converted to a folder path and the file put in selected files.)
        `selected_files` this is the selected files in the dir. If empty, this means that the whole dir is being copied.
        """
        super().__init__(Icons.FOLDER, os_utils.getPathTarget(path))
        self.setToolTip(path)

        # Internal State
        self.path: str = path

    def mouseDoubleClickEvent(self, event):
        os_utils.showDirInExplorer(self.path)

    def enterEvent(self, event):
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def leaveEvent(self, event):
        self.setCursor(Qt.CursorShape.ArrowCursor)
