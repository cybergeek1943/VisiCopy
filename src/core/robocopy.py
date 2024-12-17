from subprocess import Popen, PIPE, CREATE_NEW_CONSOLE, CREATE_NO_WINDOW
from threading import Thread
import core.os_utils as os_utils
from core.hooks import Hook, HookType
"""Contains the robocopy wrapper code needed to interact with, monitor, and initialize processes."""


class CopyProcess_NoPiping:  # not to be used directly within Qt GUI applications
    def __init__(self, src_path: str, dst_path: str, selector_pattern: list | tuple = os_utils.DEFAULT_PATTERN, flags: list = None, _selected_files: list = None, _include_src_base_dir: bool = False, _flags_info: dict = None, _current_working_dir: str = None, __running_in_qt_app__: bool = False) -> None:  # `_` before an arg means that the arg is a custom arg not part of the original process being executed
        r"""
        This is the base class for running a robocopy process. The more refined CopyProcess object inherits from this class to add more functionality for GUI.

        NOTE: All paths must use `\` as their file delimiters.
        """
        src_path = os_utils.abspath(src_path)
        dst_path = os_utils.abspath(dst_path)

        # Object Representation
        self.__arg_repr__: dict = (lambda **kwargs: kwargs)(src_path=src_path, dst_path=dst_path, selector_pattern=selector_pattern, flags=flags, _selected_files=_selected_files, _include_src_base_dir=_include_src_base_dir, _options_info=_flags_info, _current_working_dir=_current_working_dir)

        # ---------------- Fully Program Flow Controlled Stats (not resettable) ----------------
        self.pending: bool = True  # set this too True to mark this instance as pending. By default, when an instance is created it is set as pending so that calling startPending() is not necessary
        self.process_running: bool = False
        self.process_deleted: bool = False  # if the process is deleted then this must be set to True so that the process manager code can ignore this process instance

        # ---------------- Resettable Stats ----------------
        self.unnatural_termination_occurred: bool = False

        # ---------------- Process Args ----------------
        self.cwd: str = _current_working_dir  # not currently in use
        self.src_drive_letter: str = src_path.partition('\\')[0]
        self.dst_drive_letter: str = dst_path.partition('\\')[0]
        self.src_path: str = src_path
        self.dst_path: str = dst_path
        if _include_src_base_dir:
            if os_utils.isfile(src_path):
                self.dst_path: str = f"{self.dst_path}\\{src_path.rpartition('\\')[0].rpartition('\\')[2]}"
            else:
                self.dst_path: str = f"{self.dst_path}\\{src_path.rpartition('\\')[2]}"
        self.selector_pattern: list = list(selector_pattern)
        self.flags: list = flags if flags else []
        if os_utils.isfile(src_path):  # if only copying one file
            parts: tuple = src_path.rpartition('\\')
            self.src_path: str = parts[0]
            self.selector_pattern: list = [parts[2],]
            self.disableRecursion()
        elif _selected_files:  # if only copying a specified selection of files
            self.selector_pattern: list = _selected_files
            self.disableRecursion()
        self.src_path_char_count: int = len(self.src_path)
        self.dst_path_char_count: int = len(self.dst_path)

        # Option Info - information about the robocopy arguments passed to `options`
        _flags_info = {} if _flags_info is None else _flags_info
        self.recursion_enabled: bool = _flags_info.get('recursive', False)
        self.retry_limit: int = _flags_info.get('retry_limit', 0)  # retry limit per file
        self.retry_wait: int = _flags_info.get('retry_wait', 0)  # retry wait in seconds
        self.sync_every_n_min: int = _flags_info.get('sync_every_n_min', 1)
        self.sync_every_n_change: int = _flags_info.get('sync_every_n_change', 1)

        # ---------------- Current Process Object ----------------
        self.__process_obj__: Popen | None = None

        # ---------------- Hooks ----------------
        self.deletedHook: HookType = Hook(running_in_qt_app=__running_in_qt_app__)  # emitted when copy process is marked as deleted
        self.startedHook: HookType = Hook(running_in_qt_app=__running_in_qt_app__)  # emitted when copy process is started
        self.stoppedHook: HookType = Hook(running_in_qt_app=__running_in_qt_app__)  # emitted when copy process is stopped
        self.pendingStartedHook: HookType = Hook(running_in_qt_app=__running_in_qt_app__)  # emitted when copy process pending is started

        # ---------------- Hooks (used by piping enabled subclass) ----------------
        self.totalStatsUpdateHook: HookType = Hook(running_in_qt_app=__running_in_qt_app__)  # function to call when new file is copied (Best used for updating the total files copied title and Current File Size Label)
        self.currentFileStatsUpdateHook: HookType = Hook(running_in_qt_app=__running_in_qt_app__)  # function to call when progress updates (Best used for updating both Total Progress and Current File Progress)
        self.errorOccurredHook: HookType = Hook(running_in_qt_app=__running_in_qt_app__)  # function to call when an error happens
        self.changeDetectedHook: HookType = Hook(running_in_qt_app=__running_in_qt_app__)  # function when change is detected in source by continuous monitoring
        self.syncCompleteHook: HookType = Hook(running_in_qt_app=__running_in_qt_app__)  # function to call when copy is finished... even if continuous monitoring is still running


    def disableRecursion(self) -> None:
        """useful if recursion flags must be overridden because of single or selected files being copied"""
        for i, o in enumerate(self.flags):
            if o == '/s' or o == '/e':
                self.flags.pop(i)
        self.recursion_enabled = False

    def __create_process_obj__(self) -> Popen:
        """Creates and returns a new `Popen` object to run the `robocopy` process with the given source, destination,
        selector pattern, and flags. The `robocopy` command is executed with the specified arguments."""
        return Popen(f'robocopy "{self.src_path}" "{self.dst_path}" {os_utils.joinArgs(self.selector_pattern)}{' ' if self.flags else ''}{' '.join(self.flags)}',
                     creationflags=CREATE_NEW_CONSOLE,
                     cwd=self.cwd)

    def start(self, blocked: bool = False) -> None:
        """Starts the `robocopy` process by calling `__create_process_obj__` to create the process and then
        either blocks execution or runs the process in a separate thread depending on the `blocked` parameter."""
        if self.process_deleted:
            return
        self.__reset_stats__()
        self.__process_obj__: Popen = self.__create_process_obj__()
        self.process_running = True
        self.pending = False
        if blocked:
            self.__process_analyzer__(self.__process_obj__)
        else:
            Thread(target=self.__process_analyzer__, args=(self.__process_obj__,)).start()

    def startPending(self) -> None:
        """Marks the current copy process as pending and triggers the `pendingStartedHook`.
        This is used to indicate that the process is awaiting execution."""
        self.pending = True
        self.pendingStartedHook()

    def __reset_stats__(self) -> None:
        """This gets called by start()"""
        self.unnatural_termination_occurred = False

    def terminate(self) -> None:
        """Terminates the running `robocopy` process if it is active, otherwise marks the process as stopped.
        Sets the `unnatural_termination_occurred` flag to True."""
        self.pending = False
        self.unnatural_termination_occurred = True
        if self.process_running:
            self.__process_obj__.kill()
        else:  # in case of pending (because process isn't actually running when pending)
            self.stoppedHook()

    def delete(self) -> None:
        """Use this function to terminate and mark a process instance as deleted."""
        if self.process_deleted:
            return
        self.terminate()
        self.process_deleted = True
        self.deletedHook()

    def __process_analyzer__(self, p: Popen) -> None:
        """Analyzes the output of the `robocopy` process to track the progress, detect errors, and handle file copying events. It also updates internal statistics for the copy process and manages hooks for progress tracking and error reporting."""
        self.startedHook()
        p.wait()
        self.stoppedHook()
        self.process_running = False

    def __repr__(self) -> str:
        """Returns a string representation of the current instance, including the source path, destination path,
        selector pattern, flags, and other relevant arguments for debugging purposes."""
        return self.__arg_repr__.__str__()


class CopyProcess(CopyProcess_NoPiping):  # TODO document these classes better
    def __set_source_files_count(self, blocking: bool = False, __running_threaded__: bool = False) -> None:
        """Calculates and sets the total number of files to be copied based on the source directory and the selector pattern."""
        # must be calculated at the beginning of copy if the total progress is going to be calculated
        if not __running_threaded__:
            if os_utils.isfile(self.src_path):  # if only copying one file
                self.source_files_count: int = 1
                return
            elif self.__arg_repr__['_selected_files']:  # if only copying a specified selection of files... in which case the number is known.
                self.source_files_count: int = len(self.__arg_repr__['_selected_files'])
                return
        if not __running_threaded__ and not blocking:
            Thread(target=self.__set_source_files_count, args=(True, True)).start()
            return
        self.source_files_count: int = os_utils.fileCounter(path=self.src_path, pattern=self.selector_pattern, recursive=self.recursion_enabled)

    def __init__(self, src_path: str, dst_path: str, selector_pattern: tuple | list = os_utils.DEFAULT_PATTERN, flags: list = None, _selected_files: list = None, _include_src_base_dir: bool = False, _flags_info: dict = None, _current_working_dir: str = None, __running_in_qt_app__: bool = False) -> None:  # todo: keep these args in sync with parent args
        r"""This class wraps the robocopy program, pipes & parses its output, and calculates copy progress. Progress is calculated by looking at the current number of files copied compared to the total in source.

        The fallowing key-values must be added to `_option_info` if `options` contains:
        - "recursive": True  # if /s or /e is used
        - "retry_limit": n, "retry_wait": n  # if /r:n or /w:n is used
        - "sync_every_n_min": n, "sync_every_n_change": n  # if /mot:n or /mon:n is used

        NOTE: All paths must use `\` as their file delimiters.
        NOTE: Because this class is only used in the context of GUI process manager, none of the hooks that directly interact with the main QT thread can run in their own generic threads. Otherwise, QT application may crash because its objects are not thread safe (illegal access errors).
        """
        CopyProcess_NoPiping.__init__(self, src_path=src_path, dst_path=dst_path, selector_pattern=selector_pattern, flags=flags, _selected_files=_selected_files, _include_src_base_dir=_include_src_base_dir, _flags_info=_flags_info, _current_working_dir=_current_working_dir, __running_in_qt_app__=__running_in_qt_app__)
        # ---------------- Internal Args for Methods (settable from outside) ----------------
        self.rescan_source_files_count_on_start: bool = False  # a user dialog could change this for example

        # ---------------- Fully Program Flow Controlled Stats (not resettable) ----------------
        self.continuous_sync_running: bool = False
        self.current_file: str = ''  # path of current file
        self.current_file_size: int = 0  # current file size in bytes
        self.current_file_progress: float = 0.0  # current file copy progress

        # ---------------- Resettable Stats ----------------
        # Total Stats
        self.sync_complete: bool = False
        self.source_files_count: int = 0  # used to calculate total progress percentage (it can also be the number of changes detected when continuous monitoring is enabled).
        self.__set_source_files_count(blocking=False)  # run this function as non-blocking so that copying can start immediately.
        self.total_files_read: int = 0  # this is a step ahead because its includes the current file in progress. Use total_files_copied() property to get accurate number of total files copied.
        self.total_bytes_read: int = 0  # this is a step ahead because its includes the full bytes of current file in progress. Use total_bytes_copied() property to get accurate number of total bytes copied.

        # Error Stats
        self.error_count: int = 0
        self.errors: list[tuple] = []  # (details, error_message, current_file), ...

        # ---------------- Required Robocopy Process Piping Variables ----------------
        self.__required_flags_for_piping__: list = [  # These are the Required RoboCopy args for the stdout piping parser to work
            "/ndl",  # don't show dir names,
            "/nc",  # don't show file classes
            "/njh",  # no job header
            "/njs",  # no job summery
            "/tee",  # show the status both in the console and log file (if log file specified)
            "/bytes",  # show all file sizes in bytes
            # "/v",  # originally was going to be used to show skipped files (this would be done because our custom file_counter() func does not take exclusion-filters into account). We will not use this because it messes up the progress counter with files that are skipped (such as files that already exist in DST).
            # "/unicode",  # todo: maybe use this in future if unicode file names need to be listed for other languages... causes error currently and is not included for other speed & memory reasons
        ]

    @property
    def total_progress(self) -> float:
        """Returns total progress of this copy process"""
        if not self.source_files_count:
            return 0.0
        if self.sync_complete:
            return 1.0
        if not self.total_files_read:
            return 0.0
        return (self.total_files_read + self.current_file_progress - 1) / self.source_files_count

    @property
    def total_bytes_copied(self) -> int:
        """Returns total bytes copied of this copy process"""
        if not self.total_bytes_read:
            return 0
        if self.sync_complete:
            return self.total_bytes_read
        return self.total_bytes_read-int(self.current_file_size * (1 - self.current_file_progress))

    @property
    def total_files_copied(self) -> int:
        """Returns total bytes copied of this copy process"""
        if self.total_files_read <= 0:  # use this because sometimes total files copied may be negative because of errors... specifically when invalid dst path error occurs.
            return 0
        if self.sync_complete:
            return self.total_files_read
        return self.total_files_read - 1

    def current_file_name(self, show_parent_dirs: bool = False) -> str:
        """Returns the name of the current file being copied, optionally including its parent directory."""
        return self.current_file[self.src_path_char_count+1:] if show_parent_dirs else os_utils.getPathTarget(self.current_file)

    def __reset_stats__(self) -> None:
        """This gets called by start()"""
        self.sync_complete = False
        self.total_files_read = 0
        self.total_bytes_read = 0
        self.__set_source_files_count(blocking=False) if self.rescan_source_files_count_on_start else None  # run this function in a separate thread so that copying can start immediately.
        self.error_count = 0
        self.errors.clear()
        self.unnatural_termination_occurred = False

    def __create_process_obj__(self) -> Popen:
        """Creates and returns a new `Popen` object to run the `robocopy` process with the required flags for piping."""
        return Popen(f'robocopy "{self.src_path}" "{self.dst_path}" {os_utils.joinArgs(self.selector_pattern)}{' ' if self.flags else ''}{' '.join(self.flags)} {' '.join(self.__required_flags_for_piping__)}',
                     stdout=PIPE,  # this tells us to pipe the output into buffer
                     creationflags=CREATE_NO_WINDOW,
                     text=True,  # this tells use to use text encoding
                     cwd=self.cwd)

    def __process_analyzer__(self, p: Popen) -> None:
        """Analyzes the robocopy process (using piping) and updates class attributes pertaining to the copy jobs status"""
        self.startedHook()
        error_details: str = ''
        error_occurred: bool = False
        # stdout seems to be line buffered.
        while p.poll() is None:  # this code is based upon an extensive analysis of the stdout of robocopy when using self.__required_args_for_piping__ as the flags
            l: str = p.stdout.readline(-1)[:-1]  # [:-1] is used to remove the newline char at end of each line
            if not l:
                continue

            # Changes Detector
            if l[:11] == '  Monitor :':
                self.continuous_sync_running = True
                self.sync_complete = True
                self.syncCompleteHook()
                continue
            if l[-9:] == ' changes.':
                changes: int = int(l.split(' ')[-2])
                if changes != 0:
                    self.sync_complete = False
                    self.source_files_count = changes
                    self.total_files_read = 0
                    self.total_bytes_read = 0
                    self.changeDetectedHook()
                continue

            # Error Catcher
            if error_occurred:  # after an error is caught, the next line contains the message... the message is what this code catches.
                error_occurred = False
                self.error_count += 1
                self.errors.append((error_details, l, self.current_file))
                self.errorOccurredHook()
                continue
            if l[20:25] == 'ERROR':  # first catches an error
                error_occurred = True
                error_details = l
                self.total_bytes_read -= self.current_file_size
                self.total_files_read -= 1
                self.current_file_progress = 1.0  # to keep the overall percentage value in place otherwise overall progress jumps back because the self.current_file_progress gets set to 0 on pass of file before error gets raised
                self.totalStatsUpdateHook()
                continue
            if l[0:5] == 'ERROR':  # error at [0:5] occurs when retry limit is exceeded. Nothing comes after it
                continue
            if l[0:7] == 'Waiting':  # after errors occur waits and retries may be attempted... ignore analyzing them here.
                continue

            # Analyze the pipe results
            l: str = l.strip(' ')
            if l[-1] == '%':  # if `l` is a percentage
                self.current_file_progress = float(l[:-1]) / 100  # for some file types percentages are displayed with a floating part in addition to the integer part... for this reason we need to parse l[:-1] as a float type.
                self.currentFileStatsUpdateHook()
                continue
            if l[0] == '\t':  # if `l` is a new file & bytes listing
                parts: tuple = l[6:].partition('\t')
                self.current_file = parts[2]
                self.current_file_size = int(parts[0])
                self.current_file_progress = 0.0  # must reset this so that the self.total_bytes_copied property doesn't jump ahead temporarily.
                self.total_bytes_read += self.current_file_size
                self.total_files_read += 1
                self.totalStatsUpdateHook()

        self.process_running = False
        self.continuous_sync_running = False
        if not self.unnatural_termination_occurred:
            self.sync_complete = True
            self.syncCompleteHook()
        self.stoppedHook()


if __name__ == "__main__":
    source_dir: str = r"../misc/src1/mon.log"
    destination_dir: str = r"../misc/dst1"
    pr = CopyProcess(src_path=source_dir, dst_path=destination_dir, flags=['/r:3', '/w:1', '/s'], _include_src_base_dir=False)  # '/iorate:1'
    # pr.totalStatsUpdateHook.connect(lambda: print(pr.current_file, pr.current_file_size))
    pr.start()
