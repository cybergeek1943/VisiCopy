from core.settings import settings_file
import core.settings as settings
from core.settings import CustomSettings
from core.translation import tr, init_translator
from core.os_utils import user_docs_path
import core.importer_exporter as importer_exporter
from core.jobs import job_file
from core import process_manager
import process_manager_window
import settings_window
from qfluentwidgets import TitleLabel, PrimaryPushButton, PushButton, ProgressBar, VerticalSeparator, SingleDirectionScrollArea, NavigationItemPosition, MessageBoxBase, SubtitleLabel, LineEdit
from ui_lib.policy import *
from ui_lib.icons import FluentIcon, MainIcon
from ui_lib import windows, dialogs
from ui_lib import ImageLabel, SpacerItem, Label
from PySide6.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QWidget, QGridLayout, QFileDialog, QListWidget
from PySide6.QtCore import QTimer
from source_sub_window import MainWindow as SourceSelectionSubWindow
from destination_sub_window import MainWindow as DestinationSelectionWindow


class builders:  # TODO abstract me!
    class VisualConnectorLine(ProgressBar):
        def __init__(self):
            super().__init__()
            self.setMinimumHeight(6)
            self.setMinimumWidth(200)
            self.setCustomBarColor('#73e68c', '#73e68c')

        def set_complete(self, b: bool):
            """Sets value to 100 if True"""
            self.setValue(100 if b else 0)

    class PrimaryButton(PrimaryPushButton):
        """Inherits from PrimaryPushButton and initializes a button."""
        def __init__(self, label: str, slots: tuple[callable] = None, disabled: bool = True):
            super().__init__()
            if slots:
                for c in slots:
                    self.clicked.connect(c)
            self.setText(label)
            self.setMinimumWidth(170)
            # applyAdditionalStyleSheet(self, 'QPushButton {border-radius: 10px;}')
            self.setDisabled(disabled)

    class Button(PushButton):
        """Inherits from PushButton and initializes a button."""
        def __init__(self, icon: FluentIcon | None, label: str, tooltip: str, slots: tuple[callable] = None, disabled: bool = False):
            super().__init__()
            if slots:
                for c in slots:
                    self.clicked.connect(c)
            self.setIcon(icon) if icon else None
            self.setText(label)
            self.setToolTip(tooltip)
            self.setDisabled(disabled)
            self.setSizePolicy(SizePolicy.Fixed, SizePolicy.Fixed)


class HomeTab(QWidget):
    """Sets up the layout of the home tab."""
    def __init__(self):
        super().__init__()
        self.setObjectName('home_tab')
        v_lay = QVBoxLayout()
        self.setLayout(v_lay)
        v_lay.addWidget(ImageLabel(MainIcon.logoWName, 32), alignment=AlignFlag.AlignHCenter)

        # -------- UI --------
        ui = QWidget()
        ui.setSizePolicy(SizePolicy.Fixed, SizePolicy.Fixed)
        v_lay.addWidget(ui, alignment=AlignFlag.AlignCenter)
        grid = QGridLayout()
        ui.setLayout(grid)

        QTimer.singleShot(100, self.source_selection_window_size)

        self.source_selection_sub_window = SourceSelectionSubWindow()
        self.source_selection_sub_window.onWindowHidden.connect(self.source_selection_window_closer)
        grid.addWidget(ImageLabel(MainIcon.selectSource), 0, 0, alignment=AlignFlag.AlignCenter)
        self.select_source_button = builders.PrimaryButton(tr('Select Source'), slots=(self.source_selection_sub_window.show,), disabled=False)
        grid.addWidget(self.select_source_button, 2, 0, alignment=AlignFlag.AlignCenter)
        self.source_connector_line = builders.VisualConnectorLine()
        grid.addWidget(self.source_connector_line, 0, 1, alignment=AlignFlag.AlignCenter)

        QTimer.singleShot(100, self.destination_selection_window_size)

        self.destination_selection_sub_window = DestinationSelectionWindow()
        self.destination_selection_sub_window.onWindowHidden.connect(self.destination_selection_window_closer)
        grid.addWidget(ImageLabel(MainIcon.selectDestination), 0, 2, alignment=AlignFlag.AlignCenter)
        self.select_destination_button = builders.PrimaryButton(tr('Select Destination'), slots=(self.destination_selection_sub_window.show,))
        grid.addWidget(self.select_destination_button, 2, 2, alignment=AlignFlag.AlignCenter)
        self.destination_connector_line = builders.VisualConnectorLine()
        grid.addWidget(self.destination_connector_line, 0, 3, alignment=AlignFlag.AlignCenter)

        # start copy
        grid.addWidget(ImageLabel(MainIcon.startCopy), 0, 4, alignment=AlignFlag.AlignCenter)
        self.start_copy_button = builders.PrimaryButton(tr('Start Copy'), slots=(self.on_start_copy_pressed,))
        grid.addWidget(self.start_copy_button, 2, 4, alignment=AlignFlag.AlignCenter)

        # spacers
        grid.addWidget(SpacerItem(0, 32), 1, 2)  # vertical space between buttons and icons.
        grid.addWidget(SpacerItem(0, 32), 3, 2)  # vertical space after buttons to shift ui up.

    def source_selection_window_size(self):
        """Sizes the source selection menu"""
        self.source_selection_sub_window.resize(int(self.window().size().width() * 0.9), int(self.window().size().height() * 0.9))
        self.source_selection_sub_window.move(self.window().pos().x() + 32, self.window().pos().y() + 32)

    def source_selection_window_closer(self):
        """Calls to close the selection window"""
        self.on_source_selection_window_closed(self.source_selection_sub_window.selection_manager_tab.widget_count())

    def destination_selection_window_size(self):
        """Sizes the source destination menu"""
        self.destination_selection_sub_window.resize(int(self.window().size().width() * 0.9), int(self.window().size().height() * 0.9))
        self.destination_selection_sub_window.move(self.window().pos().x() + 32, self.window().pos().y() + 32)

    def destination_selection_window_closer(self):
        """Calls to close the selection window"""
        self.on_destination_selection_window_closed(self.destination_selection_sub_window.selection_manager_tab.widget_count())

    def on_source_selection_window_closed(self, selected_file_count: int):
        """Updates the interface based on selected files."""
        if selected_file_count == 0:
            self.select_destination_button.setDisabled(True)
            self.start_copy_button.setDisabled(True)
            self.source_connector_line.set_complete(False)
            self.destination_connector_line.set_complete(False)
            return
        self.select_destination_button.setDisabled(False)
        self.source_connector_line.set_complete(True)

    def on_destination_selection_window_closed(self, selected_folder_count: int):
        """Either enables or disables the copy button based on if a destination folder is selected."""
        if selected_folder_count == 0:
            self.start_copy_button.setDisabled(True)
            self.destination_connector_line.set_complete(False)
            return
        self.start_copy_button.setDisabled(False)
        self.destination_connector_line.set_complete(True)

    def on_start_copy_pressed(self):
        """Initializes copying process."""
        source_selection: list[tuple[str, dict]] = self.source_selection_sub_window.get_source_selection()
        destination_selection: list[str] = self.destination_selection_sub_window.get_destination_selection()
        process_manager.init_processes(source_selection, destination_selection)
        self.window().hide()
        if CustomSettings.use_gui:
            process_manager_window.start(app_context=app)
        else:
            process_manager.start_all_processes()


class AdvancedHomeTab(QWidget):  # TODO this class is not being used yet. Implement it later to add better source and destination selection UI when advanced mode is on.
    def __init__(self):
        super().__init__()
        self.setObjectName('home_tab')
        grid = QGridLayout()
        self.setLayout(grid)

        # -------- UI --------
        grid.addWidget(Label('Source', 24, weight=FontWeight.Bold), 0, 0)
        grid.addWidget(SingleDirectionScrollArea(), 1, 0)
        grid.addWidget(builders.Button(None, 'Clear Selection', 'Clear the source selection'), 2, 0)
        grid.addWidget(VerticalSeparator(), 0, 1, 2, 1)
        grid.addWidget(Label('Destination', 24, weight=FontWeight.Bold), 0, 2)
        grid.addWidget(SingleDirectionScrollArea(), 1, 2)


class TextEntryDialog(MessageBoxBase):  # TODO put this in dialogs module in UI lib as a generalised form
    """ Dialog box with text entry """
    def __init__(self, title: str, placeholder: str):
        super().__init__(main_window)
        self.titleLabel = SubtitleLabel()
        self.titleLabel.setText(title)
        self.urlLineEdit = LineEdit()
        self.urlLineEdit.setPlaceholderText(placeholder)
        self.urlLineEdit.setClearButtonEnabled(True)
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.urlLineEdit)
        self.widget.setMinimumWidth(350)


def showJobNameDialog(title: str, placeholder: str):  # TODO put this in dialogs module in UI lib
    w = TextEntryDialog(title, placeholder)
    if w.exec():
        return w.urlLineEdit.text()



class JobTab(QWidget):
    """Manages job files"""
    def __init__(self, home_tab: HomeTab | AdvancedHomeTab):
        super().__init__()
        self.home_tab = home_tab
        self.setObjectName('job_tab')
        v_lay = QVBoxLayout()
        v_lay.setAlignment(AlignFlag.AlignTop)
        self.setLayout(v_lay)

        # -------- UI --------
        v_lay.addWidget(_:=TitleLabel(tr('Job Manager')))

        # Job List View
        self.list_view = QListWidget()
        for name in job_file.data:
            self.list_view.addItem(name)
        v_lay.addWidget(self.list_view)

        # Buttons
        buttons_lay = QHBoxLayout()
        buttons_lay.setAlignment(AlignFlag.AlignRight)
        buttons_lay.addWidget(builders.Button(FluentIcon.SAVE_AS, tr('Create Job'), tr('Create a job from the current selection of sources, destinations, and settings.'), slots=(self.create_job,)))
        buttons_lay.addWidget(builders.Button(FluentIcon.DELETE, tr('Delete Job'), tr('Delete the selected job.'), slots=(self.delete_job,)))
        buttons_lay.addWidget(builders.Button(FluentIcon.EDIT, tr("Update Job's Settings"), tr("Update the selected job's settings based on the current selection of settings."), slots=(self.update_jobs_settings,)))
        buttons_lay.addWidget(builders.Button(FluentIcon.PLAY, tr('Run Job'), tr('Run the selected job containing sources, destinations, and settings.'), slots=(self.run_job,)))

        v_lay.addLayout(buttons_lay)

    def get_selected_job_name(self) -> str:
        if (i:=self.list_view.currentRow()) != -1:
            return self.list_view.item(i).text()

    def run_job(self):
        """Prompts selection of job, initiates processes, and begins copy."""
        if not (name:=self.get_selected_job_name()):
            dialogs.info(self, tr('Info'), tr('Please select a job first.'))
            return
        process_manager.init_processes(*job_file.data[name])
        self.window().hide()
        if CustomSettings.use_gui:
            process_manager_window.start(app_context=app)
        else:
            app.quit()
            process_manager.start_all_processes()

    def update_jobs_settings(self):
        if not (name:=self.get_selected_job_name()):
            dialogs.info(self, tr('Info'), tr('Please select a job first.'))
            return
        if dialogs.response.Yes == dialogs.question(self, tr('Update Job Settings'), tr("Do you want to update this job's settings with the current settings?")):
            job_file.data[name][-1] = settings_file.data
            job_file.save()

    def create_job(self):
        """Enables user to save new job file."""
        source_selection: list[tuple[str, dict]] = self.home_tab.source_selection_sub_window.get_source_selection()
        destination_selection: list[str] = self.home_tab.destination_selection_sub_window.get_destination_selection()
        if not source_selection or not destination_selection:
            dialogs.info(self, tr('Cannot Create Job'), tr('Please select both a source and destination before you create a job.'), critical=True)
            return
        if not (name:=showJobNameDialog(tr('Please enter a job name'), tr('Name'))):
            return
        if name in job_file.data:
            dialogs.info(self, tr('Existing Job Warning!'), tr('There is already a job with this name.'), critical=True)
            return
        self.list_view.addItem(name)
        job_file.data[name] = [source_selection, destination_selection, settings_file.data]
        job_file.save()

    def delete_job(self):
        if not (name:=self.get_selected_job_name()):
            dialogs.info(self, tr('Info'), tr('Please select a job first.'))
            return
        del job_file.data[name]
        job_file.save()
        self.list_view.takeItem(self.list_view.currentRow())



class MainWindow(windows.FluentWindow):
    """Creates main window"""
    def __init__(self):
        super().__init__(remember_window_pos=False, menu_expand_width=150)
        self.setWindowTitle(tr('VisiCopy'))  # if not config_file.data['advanced_mode'] else tr('VisiCopy (Pro Mode)'))
        self.resize(1370, 700)
        self.navigationInterface.setCollapsible(True)
        self.navigationInterface.setReturnButtonVisible(False)

        # -------------------------------- Tabs --------------------------------
        # src/dst selection
        home_tab: HomeTab = HomeTab()  # | AdvancedHomeTab = AdvancedHomeTab() if config_file.data['advanced_mode'] else HomeTab()
        self.addSubInterface(home_tab, FluentIcon.HOME, tr('Home'))

        # Job Manager
        self.addSubInterface(JobTab(home_tab), FluentIcon.BOOK_SHELF, tr('Job Manager'))

        # Settings Button
        self.navigationInterface.addItem('open_settings', FluentIcon.SETTING, tr('Settings'), selectable=False, onClick=settings_window.start, position=NavigationItemPosition.BOTTOM)

    def closeEvent(self, event):
        """Exists application on window close."""
        app.exit()
        event.ignore()  # so that exit()'s dialogs can work.


class Application(QApplication):
    def exit(self, retcode: int = 0, force_exit: bool = False):
        """Checks for unsaved changes, if found, prompts the user."""
        if not force_exit and settings.detected_changes != 0:
            title: str = tr('Confirm Change')
            message: str = tr('You made 1 change in the settings.\nDo you want to save this change for future use?') if settings.detected_changes == 1 \
                else tr('You made {} changes in the settings.\nDo you want to save these changes for future use?').format(settings.detected_changes)
            r = dialogs.question(main_window, title, message, show_cancel_button=True)
            if r == dialogs.response.Yes:
                settings_file.save()
            elif r == dialogs.response.Cancel:
                return
        settings.set_detected_changes(0)
        super().exit(retcode)


app: Application = Application()
init_translator(app)
main_window: MainWindow
def start():
    global main_window
    main_window = MainWindow()
    main_window.show()
    settings_window.app = app
    app.exec()  # loop starts here and only exits when application is quit or restarted


if __name__ == '__main__':  # pyside6-deploy main.py
    start()
