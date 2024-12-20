from core.config import config_file
from core.hooks import Binder
from core.os_utils import copyToClipboard
from core.settings import CustomSettings
from core.translation import tr
import core.os_utils as os_utils
from core.robocopy import CopyProcess
from core.unit_humanizer import format_seconds, format_bytes
from core.eta_calc import EtaAndSpeedCalc
from core import process_manager

# Import Components and Visual Tools
from qfluentwidgets import (SimpleCardWidget,
                            TitleLabel, BodyLabel,
                            HorizontalSeparator, InfoBadge,
                            ProgressRing, ProgressBar, PushButton, ImageLabel, IndeterminateProgressRing)
from ui_components import InfoPageWidget
from ui_lib import AlignFlag, SizePolicy, windows, dialogs, cards
from ui_lib import ScrollView, HorizontalExpandSpace
from ui_lib.icons import ProcessManagerIcon, FluentIcon
from PySide6.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QWidget, QGridLayout
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import QTimer
from qfluentwidgets import setFont, NavigationItemPosition


class builders:  # TODO abstract me!
    """Contains basic builder components."""

    class StatusIcon(ImageLabel):
        def __init__(self):
            """Initializes the StatusIcon component, sets up the progress ring, and sets the initial status to 'Pending.'"""
            ImageLabel.__init__(self)
            self.ring = IndeterminateProgressRing(self)
            self.ring.setCustomBarColor('white', 'white')
            self.ring.setStrokeWidth(4)
            self.set_Pending()

        def __setImage(self, path: str, show_pending_ring: bool = False):
            """Sets the image for the icon and optionally displays a pending progress ring based on the show_pending_ring argument."""
            self.setImage(path)
            self.scaledToHeight(100)
            self.ring.setFixedSize(self.size())
            self.ring.show() if show_pending_ring else self.ring.hide()

        def set_Pending(self):
            """Sets the status to 'Pending' by displaying the pending icon and showing the pending progress ring."""
            self.__setImage(ProcessManagerIcon.pending, show_pending_ring=True)

        def set_Complete(self):
            """Sets the status to 'Complete' by displaying the complete icon."""
            self.__setImage(ProcessManagerIcon.complete)

        def set_Monitoring(self):
            """Sets the status to 'Monitoring' by displaying the monitoring icon and showing the pending progress ring."""
            self.__setImage(ProcessManagerIcon.monitoring, show_pending_ring=True)

        def set_StoppedMidway(self):
            """Sets the status to 'Stopped Midway' by displaying the stopped midway icon."""
            self.__setImage(ProcessManagerIcon.stoppedMidway)

        def set_CompleteWithError(self):
            """Sets the status to 'Complete With Error' by displaying the corresponding error icon."""
            self.__setImage(ProcessManagerIcon.completeWithError)

    class ProcessProgressStats(QWidget):
        def __init__(self):
            """Initializes the overall progress panel UI, sets up labels, progress ring, and internal state, and connects backend hooks for progress updates."""
            QWidget.__init__(self)
            layout = QVBoxLayout()
            self.setLayout(layout)

            # labels
            labels = QHBoxLayout()
            layout.addLayout(labels)
            self.left_label = BodyLabel()
            labels.addWidget(self.left_label)
            labels.addSpacerItem(HorizontalExpandSpace())
            self.right_label = BodyLabel()
            labels.addWidget(self.right_label)

            # progress bar
            self.progress_percentage: int = 0
            self.progress_bar = ProgressBar()
            self.progress_bar.setRange(0, 101)
            self.progress_bar.setMinimumHeight(8)
            layout.addWidget(self.progress_bar)

        def setProgressPercentage(self, p: float):
            """Updates the progress bar's value based on the given percentage p. The percentage is multiplied by 100 and the value is set on the progress bar."""
            self.progress_percentage = int(p * 100)
            self.progress_bar.setValue(1 + self.progress_percentage)

        def setLeftLabel(self, text: str):
            """Sets the text of the left label to the provided string text."""
            self.left_label.setText(text)

        def setRightLabel(self, text: str):
            """Sets the text of the right label to the provided string text."""
            self.right_label.setText(text)


class components:  # TODO abstract me!
    """Contains larger custom UI components that will be used in the main window"""

    class OverallProgressPanel(QWidget):
        def __init__(self):
            QWidget.__init__(self)
            # -------------------------------- UI --------------------------------
            layout = QHBoxLayout()
            self.setLayout(layout)
            stacked_text = QVBoxLayout()
            stacked_text.setSpacing(2)
            layout.addLayout(stacked_text)

            # Title
            self.title = TitleLabel()
            self.title.setText(tr('Overall Progress'))
            setFont(self.title, 22, QFont.Weight.Bold)
            stacked_text.addWidget(self.title)
            stacked_text.addSpacing(8)

            # Info
            self.running_processes_label = BodyLabel()
            stacked_text.addWidget(self.running_processes_label)
            self.eta_label = BodyLabel()
            stacked_text.addWidget(self.eta_label)
            self.speed_label = BodyLabel()
            stacked_text.addWidget(self.speed_label)
            self.elapsed_time_label = BodyLabel()
            stacked_text.addWidget(self.elapsed_time_label)
            self.bytes_copied_label = BodyLabel()
            stacked_text.addWidget(self.bytes_copied_label)

            # Progress Ring
            self.progress_ring = ProgressRing()
            setFont(self.progress_ring, 20, QFont.Weight.Bold)
            self.progress_ring.setTextVisible(True)
            self.progress_ring.setMinimumSize(140, 140)
            self.progress_ring.setStrokeWidth(14)
            layout.addWidget(self.progress_ring, alignment=AlignFlag.AlignBottom | AlignFlag.AlignRight)

            self.__setDefaults()

            # -------------------------------- Connection to Backend --------------------------------
            # Instead of using the Update Hooks we will use a timer to update progress
            process_manager.processesStartedHook.connect_(self.on_processes_started)
            process_manager.allProcessesStoppedHook.connect_(self.on_all_processes_stopped)
            process_manager.runningProcessCountChangedHook.connect_(lambda: self.setRunningProcesses(
                process_manager.running_process_count))

            # -------------------------------- Internal State --------------------------------
            self.total_progress: float = 0
            self.total_bytes_copied: int = 0
            self.elapsed_time: float = 0  # in seconds

            # -------------------------------- Timers --------------------------------
            speed_eta_seconds_interval: int = CustomSettings.speed_eta_seconds_interval
            self.eta_and_speed_calculator: EtaAndSpeedCalc = EtaAndSpeedCalc(speed_eta_seconds_interval,
                                                                             CustomSettings.eta_progress_checkpoints)
            self.eta_and_speed_calculation_timer: QTimer = QTimer(
                self)  # starts and stops when all processes start or stop
            self.eta_and_speed_calculation_timer.setInterval(speed_eta_seconds_interval * 1000)
            self.eta_and_speed_calculation_timer.timeout.connect(
                lambda: self.setEtaAndSpeed(self.eta_and_speed_calculator.eta(current_progress=self.total_progress),
                                            self.eta_and_speed_calculator.speed(self.total_bytes_copied)))

            self.timers_running: bool = False

        # -------------------------------- Setters --------------------------------
        def setProgressBar(self, p: float):
            """Updates the value of the progress bar based on the provided percentage p."""
            self.progress_ring.setValue(int(p * 100))

        def setEtaAndSpeed(self, eta: int | None, b: int | None):
            """Updates the ETA and speed labels with the provided eta and b (speed in bytes)."""
            self.eta_label.setText(tr('Eta') + f':  {format_seconds(eta) if eta else '----'}')
            self.speed_label.setText(tr('Speed') + f':  {format_bytes(b, per_second=True) if b else '----'}')

        def setElapsedTime(self, time: float):
            """Updates the elapsed time label with the provided time in seconds."""
            self.elapsed_time_label.setText(tr('Elapsed Time') + f':  {format_seconds(int(time))}')

        def setBytesCopied(self, b: int):
            """Updates the bytes copied label with the provided byte value b."""
            self.bytes_copied_label.setText(tr('Amount Copied') + f':  {format_bytes(b)}')

        def setRunningProcesses(self, n: int):
            """Updates the running processes label with the provided number n of running processes."""
            self.running_processes_label.setText(
                tr('Running Processes') + f':  {n}')  # sometimes n is negative because of process deletion. Hence, the greater than zero check!

        def __setDefaults(self):
            """Sets the default values for all UI elements (progress bar, ETA, elapsed time, bytes copied, running processes)."""
            self.setProgressBar(0)
            self.setEtaAndSpeed(None, None)
            self.setElapsedTime(0)
            self.setBytesCopied(0)
            self.setRunningProcesses(0)

        def start_timers(self):
            """Starts the timers for updating progress and calculating ETA and speed if the timers are not already running."""
            if self.timers_running:
                return
            update_timer.timeout.connect(self.__on_progress_update_interval)
            self.eta_and_speed_calculation_timer.start()
            self.timers_running = True

        def stop_timers(self):
            """Stops the timers for updating progress and calculating ETA and speed if the timers are running."""
            if not self.timers_running:
                return
            update_timer.timeout.disconnect(self.__on_progress_update_interval)
            self.eta_and_speed_calculation_timer.stop()
            self.timers_running = False

        # -------------------------------- Progress Update Slots --------------------------------
        def __on_progress_update_interval(self):
            """Runs every 100ms and updates the overall progress UI."""
            self.elapsed_time += 0.1
            self.setElapsedTime(self.elapsed_time)
            self.total_progress, self.total_bytes_copied = process_manager.getProcessesStats()
            self.setProgressBar(self.total_progress)
            self.setBytesCopied(self.total_bytes_copied)

        def on_processes_started(self):
            """Resets the internal state for the next restart of processes and starts the timers to begin progress updates."""
            # reset internal state for next restart:
            self.total_bytes_copied = 0
            self.total_progress = 0
            self.elapsed_time = 0
            self.eta_and_speed_calculator.reset_eta_and_speed_vars()
            self.start_timers()

        def on_all_processes_stopped(self):
            """Stops the timers, updates the progress UI, and resets the ETA and speed values when all processes have stopped."""
            self.stop_timers()
            self.__on_progress_update_interval()
            self.setEtaAndSpeed(None, None)

    class ProcessCard(SimpleCardWidget):
        def __init__(self, process_index: int, copy_process: CopyProcess):
            SimpleCardWidget.__init__(self)
            # -------------------------------- UI --------------------------------
            self.process_index = process_index + 1
            self.setBorderRadius(16)
            layout = QVBoxLayout()
            layout.setContentsMargins(12, 8, 12, 16)
            self.setLayout(layout)

            # Titles
            self.title = TitleLabel()
            setFont(self.title, 18, QFont.Weight.Bold)
            layout.addWidget(self.title)
            self.finish_notes = BodyLabel()
            self.finish_notes.hide()
            layout.addWidget(self.finish_notes)
            self.src_dst_label = BodyLabel()
            self.src_dst_label.setText(
                '{0}:  {1}\n{2}:  {3}'.format(tr('Source'), copy_process.src_path, tr('Destination'),
                                              copy_process.dst_path))
            layout.addWidget(self.src_dst_label)

            # Process Stats
            g_lay = QGridLayout()
            layout.addLayout(g_lay)
            self.status_icon = builders.StatusIcon()
            g_lay.addWidget(self.status_icon, 0, 0, 2, 1, AlignFlag.AlignVCenter | AlignFlag.AlignLeft)
            self.process_progress = builders.ProcessProgressStats()
            g_lay.addWidget(self.process_progress, 0, 1)
            self.current_file_progress = builders.ProcessProgressStats()
            g_lay.addWidget(self.current_file_progress, 1, 1)

            # Buttons
            h_lay = QHBoxLayout()
            h_lay.setContentsMargins(8, 8, 8, 0)
            layout.addLayout(h_lay)
            self.view_process_errors = PushButton()
            self.view_process_errors.setText(tr('View Errors'))
            self.view_process_errors.clicked.connect(self.on_view_errors_clicked)
            h_lay.addWidget(self.view_process_errors)
            h_lay.addSpacerItem(HorizontalExpandSpace())
            self.delete_process = PushButton()
            self.delete_process.setText(tr('Delete Process'))
            self.delete_process.setIcon(FluentIcon.DELETE)
            self.delete_process.clicked.connect(self.on_delete_clicked)
            h_lay.addWidget(self.delete_process)
            self.stop_or_restart_process = PushButton()
            self.stop_or_restart_process.setText(tr('Stop Process'))
            self.stop_or_restart_process.setIcon(FluentIcon.PAUSE)
            self.stop_or_restart_process.clicked.connect(self.on_stop_clicked)
            self.stop_button_showing: bool = True  # used to switch between 'stop' and 'reset' buttons
            self.restart_button_showing: bool = False  # used to switch between 'stop' and 'reset' buttons
            h_lay.addWidget(self.stop_or_restart_process)

            # -------------------------------- Connection to Backend --------------------------------
            # Instead of using the Update Hooks we will use a timer to update progress
            self.pr: CopyProcess = copy_process
            self.pr.syncCompleteHook.connect_(self.on_sync_complete)
            self.pr.errorOccurredHook.connect_(self.on_error_occurred)
            self.pr.changeDetectedHook.connect_(self.on_copy_process_started)
            self.pr.pendingStartedHook.connect_(self.on_pending_started)
            self.pr.startedHook.connect_(self.on_copy_process_started)
            self.pr.stoppedHook.connect_(self.on_copy_process_stopped)
            self.pr.deletedHook.connect_(self.on_process_deleted)

            # -------------------------------- Internal State (used to optimize UI updates by only updating detected changes on `update_timer` intervals) --------------------------------
            self.__current_file_progress: float = 0  # used to check for change and update both the current file progress and overall progress
            self.__current_file: str = ''  # used to check for change regarding when a new file is started to being copied.

            speed_eta_seconds_interval: int = CustomSettings.speed_eta_seconds_interval
            self.eta_and_speed_calculator: EtaAndSpeedCalc = EtaAndSpeedCalc(speed_eta_seconds_interval,
                                                                             CustomSettings.eta_progress_checkpoints)
            self.eta_and_speed_calculation_timer: QTimer = QTimer(self)  # starts and stops with process
            self.eta_and_speed_calculation_timer.setInterval(speed_eta_seconds_interval * 1000)
            self.eta_and_speed_calculation_timer.timeout.connect(
                lambda: self.setEtaAndSpeed(self.eta_and_speed_calculator.eta(current_progress=self.pr.total_progress),
                                            self.eta_and_speed_calculator.speed(self.pr.total_bytes_copied)))

            self.timers_running: bool = False

            # -------------------------------- Error Manager --------------------------------
            # Error Count Badge for the 'View Errors' button
            self.error_count_badge = InfoBadge.error(0, self, target=self.view_process_errors)
            self.error_count_badge.hide()

            # Error Window
            self.errors_window = ErrorsWindow(f'%s  •  %s {process_index + 1}' % (tr('Errors'), tr('Process')))
            QTimer.singleShot(100, lambda: (self.errors_window.resize(int(self.window().size().width() * 0.9),
                                                                      int(self.window().size().height() * 0.9)),
                                            self.errors_window.move(self.window().pos().x() + 32,
                                                                    self.window().pos().y() + 32)))  # we must use timer here because for some reason the window does not resize normally.

            # -------------------------------- Set Default Widget Values --------------------------------
            self.on_pending_started()

        # -------------------------------- Setters --------------------------------
        def setTitle(self, *args):
            """Sets the title of the process card. It includes the process index and any additional arguments passed, formatting them into a title string."""
            self.title.setText(tr('Process') + f' {self.process_index}  •  {'  •  '.join(args)}')

        def setNote(self, *args):
            """Sets a note or notes to be displayed on the process card. If no notes are provided, hides the note section. If one or more notes are provided, they are displayed as a list."""
            args: list = [s for s in args if s is not None]
            if not args:
                self.finish_notes.hide()
                return
            if len(args) == 1:
                self.finish_notes.setText(tr('Note') + f':  {args[0]}')
            else:
                self.finish_notes.setText(tr('Notes') + f':\n• {'\n• '.join(args)}')
            self.finish_notes.show()

        def setCurrentFileProgress(self, percentage: float, current_file_name: str | None):
            """Updates the progress for the current file being copied. The percentage of progress and the current file name are updated accordingly. If the file name is None, it shows a placeholder."""
            self.current_file_progress.setProgressPercentage(percentage)
            if current_file_name:
                self.current_file_progress.setLeftLabel(
                    tr('Current File') + f' {self.current_file_progress.progress_percentage}%:  {current_file_name}')
            else:
                self.current_file_progress.setLeftLabel(tr('Current File') + f':  ----')

        def setProcessProgress(self, percentage: float, amount_copied: int):
            """Sets the overall process progress percentage; progress bar; and amount copied in bytes."""
            self.process_progress.setProgressPercentage(percentage)
            self.process_progress.setLeftLabel(
                '{0}:  {1}\n{2}:  {3}%'.format(tr('Amount Copied'), format_bytes(amount_copied), tr('Process Progress'),
                                               self.process_progress.progress_percentage if self.pr.source_files_count else tr(
                                                   'calculating')))

        def setCurrentFileSize(self, size: int | None):
            """Sets the size of the current file being copied. If no size is provided, it shows a placeholder."""
            self.current_file_progress.setRightLabel(
                tr('Current File Size') + f':  {format_bytes(size) if size else '----'}')

        def setEtaAndSpeed(self, eta: int | None, speed: int | None):
            """Sets the estimated time of arrival (ETA) and the copying speed for the process. If either value is None, a placeholder is shown."""
            self.process_progress.setRightLabel(
                '{0}:  {1}\n{2}:  {3}'.format(tr('Eta'), format_seconds(eta) if eta else '----', tr('Speed'),
                                              format_bytes(speed, per_second=True) if speed else '----'))

        def setErrorCountBadge(self, count: int):
            """Updates the error count badge on the process card. If the count is zero, the badge is hidden. Otherwise, it shows the error count."""
            if count == 0:
                self.error_count_badge.hide()
                return
            self.error_count_badge.setText(str(count))
            self.error_count_badge.adjustSize()  # must do this so that the badge can adjust its size to the new text
            self.error_count_badge.show()

        def showRestartProcessButton(self):
            """Changes the "Stop Process" button to a "Restart Process" button, and connects the corresponding slot for restarting the process. Hides the stop button and shows the restart button."""
            if self.restart_button_showing:
                return
            self.stop_or_restart_process.clicked.disconnect(self.on_stop_clicked)
            self.stop_or_restart_process.clicked.connect(self.on_restart_clicked)
            self.stop_or_restart_process.setText(tr('Restart Process'))
            self.stop_or_restart_process.setIcon(FluentIcon.SYNC)
            self.restart_button_showing = True
            self.stop_button_showing = False

        def showStopProcessButton(self):
            """Changes the "Restart Process" button to a "Stop Process" button, and connects the corresponding slot for stopping the process. Hides the restart button and shows the stop button."""
            if self.stop_button_showing:
                return
            self.stop_or_restart_process.clicked.disconnect(self.on_restart_clicked)
            self.stop_or_restart_process.clicked.connect(self.on_stop_clicked)
            self.stop_or_restart_process.setText(tr('Stop Process'))
            self.stop_or_restart_process.setIcon(FluentIcon.PAUSE)
            self.stop_button_showing = True
            self.restart_button_showing = False

        def __set_progress_bars_defaults(self, show_full_progress_bars: bool = True):
            """Sets the default values for the progress bars, including setting the progress to 0 or 100 depending on the show_full_progress_bars flag."""
            self.setEtaAndSpeed(None, None)
            self.setCurrentFileSize(None)
            self.setCurrentFileProgress(1.0 if show_full_progress_bars else 0.0, None)
            self.setProcessProgress(1.0 if show_full_progress_bars else 0.0, self.pr.total_bytes_copied)

        # -------------------------------- Strings --------------------------------
        @property
        def files_copied_title(self) -> str:
            """Returns a string showing the number of files copied out of the total source files, or "calculating" if the total file count is unknown."""
            return (f'{self.pr.total_files_copied}/{self.pr.source_files_count}' if self.pr.source_files_count else tr(
                'calculating')) + ' ' + tr('Files Copied')

        @property
        def failed_copies_note(self) -> str | None:
            """Returns a string describing the number of files that failed to copy due to various issues, or None if all files were copied successfully."""
            not_copied_file_count: int = self.pr.source_files_count - self.pr.total_files_copied
            if not_copied_file_count < 0:
                return None
            if not_copied_file_count == 1:
                return tr(
                    '{0} file was not copied due to Selection Filters, Existence in Destination, Errors, or Early Termination.').format(
                    not_copied_file_count)
            else:
                return tr(
                    '{0} files were not copied due to Selection Filters, Existence in Destination, Errors, or Early Termination.').format(
                    not_copied_file_count)

        # -------------------------------- Progress Update Slots --------------------------------
        def start_timers(self):
            """Starts the timers used to update the progress of the process and calculate the ETA and speed. Ensures that the timers are not started multiple times."""
            if self.timers_running:
                return
            update_timer.timeout.connect(self.__on_progress_update_interval)
            self.eta_and_speed_calculation_timer.start()
            self.timers_running = True

        def stop_timers(self):
            """Stops the timers that update the progress and calculate the ETA and speed. Ensures that the timers are not stopped if they are not running."""
            if not self.timers_running:
                return
            update_timer.timeout.disconnect(self.__on_progress_update_interval)
            self.eta_and_speed_calculation_timer.stop()
            self.timers_running = False

        def __on_progress_update_interval(self):
            """Runs every 100ms and updates the progress UI if changes are detected in the process stats."""
            if self.__current_file != self.pr.current_file:
                self.__current_file = self.pr.current_file
                self.setTitle(self.files_copied_title)
                self.setCurrentFileSize(self.pr.current_file_size)
            if self.__current_file_progress != self.pr.current_file_progress:
                self.__current_file_progress = self.pr.current_file_progress
                self.setProcessProgress(self.pr.total_progress, self.pr.total_bytes_copied)
                self.setCurrentFileProgress(self.pr.current_file_progress,
                                            self.pr.current_file_name(show_parent_dirs=True))

        def on_copy_process_started(self):
            """Slot for when the copy process starts. Clears the error window, resets the ETA and speed variables, and starts the progress timers. Also shows the "Stop Process" button and hides the status icon."""
            self.errors_window.clearAllErrors()
            self.eta_and_speed_calculator.reset_eta_and_speed_vars()
            self.start_timers()
            self.status_icon.hide()
            self.finish_notes.hide()
            self.showStopProcessButton()

        def on_pending_started(self):
            """Slot for when the process is in the "Pending" state. Sets the title to "Pending," hides the finish notes, and shows the "Stop Process" button. The progress bars are also set to a default state."""
            self.setTitle(tr('Pending'))
            self.finish_notes.hide()
            self.status_icon.set_Pending()
            self.showStopProcessButton()
            self.__set_progress_bars_defaults(show_full_progress_bars=False)

        def on_copy_process_stopped(self):
            """Slot for when the process stops. Stops the timers and updates the UI based on the stopping condition (errors, midway stop, or successful completion). Displays the restart button."""
            self.stop_timers()
            if self.pr.process_deleted:
                return
            self.setNote(self.failed_copies_note if self.pr.total_files_copied < self.pr.source_files_count else None)
            if self.pr.unnatural_termination_occurred:
                self.status_icon.set_StoppedMidway()
                self.setTitle(tr('Stopped Midway'), self.files_copied_title)
                self.setEtaAndSpeed(None, None)
            elif self.pr.error_count != 0:
                self.status_icon.set_CompleteWithError()
                self.setTitle(tr('Finished with Errors'), self.files_copied_title)
                self.__set_progress_bars_defaults()
            else:
                self.status_icon.set_Complete()
                self.setTitle(tr('Finished'), self.files_copied_title)
                self.__set_progress_bars_defaults()
            self.status_icon.show()
            self.showRestartProcessButton()

        def on_sync_complete(self):
            """Slot for when the sync process completes. Updates the title to "Finished" with "Continuous Sync Enabled," updates the note, and changes the status icon to "Monitoring."""
            if not self.pr.continuous_sync_running:
                return
            self.stop_timers()
            self.setTitle(tr('Finished'), tr('Continuous Sync Enabled'))
            self.setNote(f'{self.files_copied_title.lower()}.',
                         self.failed_copies_note if self.pr.total_files_copied < self.pr.source_files_count else None,
                         tr('The destination will be updated every {0} minutes only when {1} changes are detected in the source.').format(
                             self.pr.sync_every_n_min, self.pr.sync_every_n_change))
            self.status_icon.set_Monitoring()
            self.status_icon.show()
            self.__set_progress_bars_defaults()

        def on_error_occurred(self):
            """Slot for when an error occurs during the process. Updates the error count badge and adds the error details to the error window."""
            self.setErrorCountBadge(self.pr.error_count)
            self.errors_window.addError(self.pr.errors[-1][0], self.pr.errors[-1][1], self.pr.current_file,
                                        self.pr.current_file_size)

        def on_process_deleted(self):
            """Slot for when the process is deleted. Updates the UI to reflect the deletion by removing the process-related elements and adjusting the layout."""
            self.setTitle(tr('Deleted'))
            # Delete UI elements
            self.finish_notes.deleteLater()
            self.status_icon.deleteLater()
            self.process_progress.deleteLater()
            self.current_file_progress.deleteLater()
            self.view_process_errors.deleteLater()
            self.error_count_badge.deleteLater()
            self.delete_process.deleteLater()
            self.stop_or_restart_process.deleteLater()
            self.setContentsMargins(12, 8, 12, 0)

        # -------------------------------- Button Slots --------------------------------
        def on_delete_clicked(self):
            """Slot for when the "Delete Process" button is clicked. Displays a confirmation dialog and deletes the process if confirmed."""
            self.pr.delete() if dialogs.question(main_window, tr('Delete this Process?'),
                                                 tr('Deleting this process will terminate it!\nAre you sure you want to continue?')) == dialogs.response.Yes else None

        def on_stop_clicked(self):
            """Slot for when the "Stop Process" button is clicked. Displays a confirmation dialog and stops the process if confirmed."""
            self.pr.terminate() if dialogs.question(main_window, tr('Stop this Process?'),
                                                    tr('Stopping this process will temporarily terminate it!\nAre you sure you want to continue?')) == dialogs.response.Yes else None

        def on_restart_clicked(self):
            """Slot for when the "Restart Process" button is clicked. Displays a confirmation dialog and restarts the process if confirmed."""
            if dialogs.question(main_window, tr('Restart this Process?'),
                                tr('Restarting this process will continue the copying of files.\nAre you sure you want to continue?')) == dialogs.response.Yes:
                self.pr.startPending()

        def on_view_errors_clicked(self):
            """Slot for when the "View Errors" button is clicked. Displays the error window to show the detailed error list."""
            self.errors_window.show()


class tabs:
    """Contains the tabs what will be used for each "tab" button on the sidebar of the main window."""

    class GenericTab(QWidget):
        def __init__(self, tab_title: str | None):
            """Initializes the generic tab widget."""
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
            self.card_container = ScrollView()
            self.layout.addWidget(self.card_container)

        def add_widget(self, w_: QWidget):
            """Adds a widget to the tab's card container."""
            self.card_container.add_widget(w_)

    class ProcessesTab(GenericTab):
        # Sets up the "Processes" tab in the UI with error tracking, an overall progress panel, and buttons for managing processes (viewing errors, restarting all processes, and stopping all processes). It connects process error hooks to handle errors and manages the UI layout to display relevant information and controls for the user.
        def __init__(self):
            """Initializes the Processes tab widget."""
            tabs.GenericTab.__init__(self, tab_title=None)
            # -------------------------------- Error Manager --------------------------------
            self.total_error_count: int = 0

            # Error Window
            self.all_errors_window = ErrorsWindow(tr('All Errors'))
            QTimer.singleShot(100, lambda: (self.all_errors_window.resize(int(self.window().size().width() * 0.9),
                                                                          int(self.window().size().height() * 0.9)),
                                            self.all_errors_window.move(self.window().pos().x() + 32,
                                                                        self.window().pos().y() + 32)))  # we must use timer here because for some reason the window does not resize normally.
            for pr in process_manager.processes:
                pr.errorOccurredHook.connect_(Binder(self.on_error_occurred, pr))

            # -------------------------------- UI --------------------------------
            self.layout.addWidget(HorizontalSeparator())

            # Overall Progress Info Section
            overall_progress = components.OverallProgressPanel()
            self.layout.addWidget(overall_progress)
            self.layout.addSpacing(8)

            # Buttons
            buttons = QHBoxLayout()
            self.layout.addLayout(buttons)

            self.view_all_errors = PushButton()
            self.view_all_errors.clicked.connect(self.all_errors_window.show)
            self.view_all_errors.setText(tr('View Errors') + f':  0')
            self.view_all_errors.setSizePolicy(SizePolicy.Fixed, SizePolicy.Fixed)
            buttons.addWidget(self.view_all_errors, alignment=AlignFlag.AlignLeft)
            buttons.addSpacerItem(HorizontalExpandSpace())

            restart_processes = PushButton()
            restart_processes.clicked.connect(self.on_restart_all_processes_clicked)
            restart_processes.setText(tr('Restart All Processes'))
            restart_processes.setSizePolicy(SizePolicy.Fixed, SizePolicy.Fixed)
            buttons.addWidget(restart_processes)

            stop_all_processes = PushButton()
            stop_all_processes.clicked.connect(self.on_stop_all_processes_clicked)
            stop_all_processes.setText(tr('Stop All Processes'))
            stop_all_processes.setSizePolicy(SizePolicy.Fixed, SizePolicy.Fixed)
            buttons.addWidget(stop_all_processes)

        # Slots
        def on_error_occurred(self, pr: CopyProcess):
            """Handles the occurrence of an error in a process."""
            self.total_error_count += 1
            self.view_all_errors.setText(tr('View Errors') + f':  {self.total_error_count}')
            self.all_errors_window.addError(pr.errors[-1][0], pr.errors[-1][1], pr.current_file, pr.current_file_size)

        # Buttons
        @staticmethod
        def on_restart_all_processes_clicked():
            """Restarts all processes."""
            process_manager.restart_all_processes() if dialogs.question(main_window, tr('Restart All Processes?'),
                                                                        tr('This will restart any processes that are not currently running.\nAre you sure you want to continue?')) == dialogs.response.Yes else None

        @staticmethod
        def on_stop_all_processes_clicked():
            """Stops all currently running processes."""
            process_manager.stop_all_processes() if dialogs.question(main_window, tr('Stop all Processes?'),
                                                                     tr('This will stop all currently running processes!\nAre you sure you want to continue?')) == dialogs.response.Yes else None


class MainWindow(windows.FluentWindow):
    def __init__(self):
        """Initializes the main window of the application."""
        super().__init__(menu_expand_width=150, remember_window_pos=True)
        self.setWindowTitle(tr('Copy Process Manager'))
        self.navigationInterface.setCollapsible(False)
        self.navigationInterface.setReturnButtonVisible(False)

        # -------------------------------- Tabs --------------------------------
        # Processes & Monitoring
        process_tab = tabs.ProcessesTab()
        for i, p in enumerate(process_manager.processes):
            process_tab.add_widget(components.ProcessCard(i, p))
        process_tab.setObjectName('processes')
        self.addSubInterface(process_tab, FluentIcon.APPLICATION, tr('Processes'))

        # Sources
        src_tab = tabs.GenericTab(tr('Sources'))
        src_tab.setObjectName('src')
        self.addSubInterface(src_tab, FluentIcon.FOLDER, tr('Sources'))
        for src_path in process_manager.source_sorted_processes:
            src_tab.add_widget(
                cards.SettingWPushButtons(FluentIcon.FOLDER, f'{os_utils.getPathTarget(src_path)}', src_path,
                                          (tr('Open in Explorer'),), (Binder(os_utils.showDirInExplorer, src_path),)))

        # Destination
        dst_tab = tabs.GenericTab(tr('Destinations'))
        dst_tab.setObjectName('dst')
        self.addSubInterface(dst_tab, FluentIcon.FLAG, tr('Destinations'))
        for dst_path in process_manager.destination_sorted_processes:
            dst_tab.add_widget(
                cards.SettingWPushButtons(FluentIcon.FOLDER, f'{os_utils.getPathTarget(dst_path)}', dst_path,
                                          (tr('Open in Explorer'),), (Binder(os_utils.showDirInExplorer, dst_path),)))

        # Information
        info = tabs.GenericTab(tr('Information'))
        info.setObjectName('info')
        info.add_widget(InfoPageWidget())
        self.addSubInterface(info, FluentIcon.INFO, tr('Info'), position=NavigationItemPosition.BOTTOM)

    def closeEvent(self, event):
        """Handles the window close event."""
        if dialogs.question(self, tr('Close Process Manager?'),
                            tr('Exiting the Process Manager will terminate all the currently running processes!\nAre you sure you want to continue?')) != dialogs.response.Yes:
            event.ignore()
            return
        super().closeEvent(event)  # must call here so that window pos and size is saved to preferences
        app.exit()  # call this so that all open windows will close.
        process_manager.stop_all_processes()  # call this so that we avoid creating zombie processes.


class ErrorsWindow(windows.SubFluentWindow):
    class ErrorCard(SimpleCardWidget):
        def __init__(self, details: str, message: str):
            """Initializes the ErrorsWindow."""
            SimpleCardWidget.__init__(self)
            error_color: QColor = QColor(219, 63, 61)
            v_lay = QVBoxLayout()
            self.setLayout(v_lay)
            details_label = BodyLabel()
            details_label.setText(tr('Details') + f':  {details}')
            details_label.setTextColor(light=error_color, dark=error_color)
            details_label.setWordWrap(True)
            v_lay.addWidget(details_label)
            message_label = BodyLabel()
            message_label.setText(tr('Message') + f':  {message}')
            message_label.setTextColor(light=error_color, dark=error_color)
            message_label.setWordWrap(True)
            v_lay.addWidget(message_label)
            clipboard_button = PushButton()
            clipboard_button.setIcon(FluentIcon.PASTE)
            clipboard_button.setText(tr('Copy to Clipboard'))
            clipboard_button.setSizePolicy(SizePolicy.Fixed, SizePolicy.Fixed)
            clipboard_button.clicked.connect(
                lambda: os_utils.copyToClipboard(f'{details_label.text()}\n{message_label.text()}', app))
            v_lay.addWidget(clipboard_button)

    def __init__(self, title: str):
        super().__init__(menu_expand_width=150)
        self.setWindowTitle(title)
        self.navigationInterface.setCollapsible(False)
        self.navigationInterface.setReturnButtonVisible(False)

        # State Vars
        self.affected_files: set = set()

        # -------------------------------- Tabs --------------------------------
        # Errors
        self.errors_tab = tabs.GenericTab(tr('Errors'))
        self.errors_tab.setObjectName('errors')
        self.addSubInterface(self.errors_tab, FluentIcon.TAG, tr('Errors'))

        # Affected Files
        self.affected_files_tab = tabs.GenericTab(tr('Affected Files'))
        self.affected_files_tab.setObjectName('affected_files')
        self.addSubInterface(self.affected_files_tab, FluentIcon.DOCUMENT, tr('Affected Files'))

        # No Errors Label
        self.no_errors_label = TitleLabel(self.stackedWidget)
        self.no_errors_label.setText(tr('No Errors have Occurred'))
        setFont(self.no_errors_label, 20)
        self.no_errors_label.setTextColor('grey', 'grey')
        self.no_errors_label.adjustSize()
        self.center_no_errors_label = lambda: QTimer.singleShot(50, lambda: self.resizeEvent(None))
        self.navigationInterface.panel.displayModeChanged.connect(lambda _: self.center_no_errors_label())

    def resizeEvent(self, event):  # center the empty_container_label() whenever resize happens
        """Handles the window resize event."""
        self.no_errors_label.move((self.stackedWidget.size().width() // 2) - (self.no_errors_label.size().width() // 2),
                                  (self.stackedWidget.size().height() // 2) - (
                                              self.no_errors_label.size().height() // 2))
        super().resizeEvent(event)

    def show(self):
        """Shows the ErrorsWindow."""
        self.center_no_errors_label()
        super().show()

    def addError(self, details: str, message: str, affected_file: str, affected_file_size: int):
        """Adds an error to the ErrorsWindow."""
        self.no_errors_label.hide()
        self.errors_tab.add_widget(ErrorsWindow.ErrorCard(details, message))
        if affected_file in self.affected_files:
            return
        self.affected_files_tab.add_widget(cards.SettingWPushButtons(FluentIcon.DOCUMENT,
                                                                     f'{os_utils.getPathTarget(affected_file)}  •  {format_bytes(affected_file_size)}',
                                                                     affected_file, (tr('Open in Explorer'),), (
                                                                     lambda: os_utils.selectFileInExplorer(
                                                                         affected_file),)))
        self.affected_files.add(affected_file)

    def clearAllErrors(self):
        """Clears all errors from the window."""
        self.errors_tab.card_container.clear_widgets()
        self.affected_files_tab.card_container.clear_widgets()
        self.no_errors_label.show()


main_window: MainWindow
update_timer: QTimer
app: QApplication


def start(app_context: QApplication):
    """Starts the application."""
    global main_window, update_timer, app
    app = app_context
    update_timer = QTimer(app_context)
    update_timer.setInterval(100)
    main_window = MainWindow()
    main_window.show()
    update_timer.start()
    QTimer.singleShot(1000, process_manager.start_all_processes)
    if config_file.data['auto_copy_flags']:
        from core.settings import settings_file
        from core import settings_parser
        copyToClipboard(' '.join(settings_parser.parse(settings_file.data)), app)
