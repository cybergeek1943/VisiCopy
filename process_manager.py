from core import settings_parser
from core import settings_data
from core.settings_data import CustomSettings, exposed_settings
from core.robocopy import CopyProcess, CopyProcess_NoPiping
from core.hooks import Hook, HookType, Binder
"""Takes care of initializing and running the copy processes"""
processes: list[CopyProcess | CopyProcess_NoPiping] = []
processes_count: int
source_sorted_processes: dict = {}
destination_sorted_processes: dict = {}
# noinspection DuplicatedCode
def init_processes(src_paths: list[tuple[str, dict]], dst_paths: list[str], settings: list[dict] | None = None, use_gui: bool | None = None):
    """This function initiates all the processes so that copying can actually begin. This MUST be called before any other functions in the module are called. If `process_flags` is NONE then the process flags will automatically be parsed from the current settings configuration."""
    if settings:
        settings_data.load_job_file_settings(settings)

    # ---- Exposed Settings ----
    flags_info: dict = {}  # this is used to tell the CopyProcess what flags to expect as `options`.
    for e in exposed_settings:  # this code is specifically designed for the CopyClass.init() _option_stats argument and is also only deigned for the current configuration of settings_data.exposed_settings
        if exposed_settings[e]['toggled'] and exposed_settings[e]['type'].endswith('entry'):
            flags_info[e] = exposed_settings[e]['entry']
        elif exposed_settings[e]['toggled']:
            flags_info[e] = True

    # ---- Custom Settings ----
    dst_prioritized: bool = CustomSettings.dst_prioritized
    use_gui: bool = CustomSettings.use_gui if use_gui is None else use_gui
    selector_pattern: list | tuple = CustomSettings.selector_pattern
    allow_new_multi_processes_in_sync_mode: bool = CustomSettings.allow_new_multi_processes_in_sync_mode

    # ---- Create the processes and add them to `processes` ----
    process_flags: list[str] = settings_parser.parse(settings_data.settings)
    if dst_prioritized and len(dst_paths) > 1:  # when prioritizing the dst
        for src in src_paths:
            for dst in dst_paths:
                if use_gui:
                    processes.append(CopyProcess(src_path=src[0], dst_path=dst, selector_pattern=selector_pattern, flags=process_flags, _selected_files=src[1]['selected_files'], _include_src_base_dir=src[1]['include_base_dir'], _flags_info=flags_info, __running_in_qt_app__=True))
                else:
                    processes.append(CopyProcess_NoPiping(src_path=src[0], dst_path=dst, selector_pattern=selector_pattern, flags=process_flags, _selected_files=src[1]['selected_files'], _include_src_base_dir=src[1]['include_base_dir'], _flags_info=flags_info))
    else:  # when prioritizing the src
        for dst in dst_paths:
            for src in src_paths:
                if use_gui:
                    processes.append(CopyProcess(src_path=src[0], dst_path=dst, selector_pattern=selector_pattern, flags=process_flags, _selected_files=src[1]['selected_files'], _include_src_base_dir=src[1]['include_base_dir'], _flags_info=flags_info, __running_in_qt_app__=True))
                else:
                    processes.append(CopyProcess_NoPiping(src_path=src[0], dst_path=dst, selector_pattern=selector_pattern, flags=process_flags, _selected_files=src[1]['selected_files'], _include_src_base_dir=src[1]['include_base_dir'], _flags_info=flags_info))
    global processes_count
    processes_count = len(processes)

    # ---- Connect up the necessary hooks for the processes to run in the stack ----
    for p in processes:
        if allow_new_multi_processes_in_sync_mode:
            p.syncCompleteHook.connect_(__start_next_pending_process)
        else:
            p.stoppedHook.connect_(__start_next_pending_process)
        p.pendingStartedHook.connect_(Binder(__start_single_process, p))  # the processPendingStarted hook is only emitted when a process is restarted. This is needed in the event of all processes completing but the user restarting one of them.

    # ---- Sorts the paths so that they can be read later by the process manager UI ----
    processes_paths: list[(str, str)] = [(p.src_path, p.dst_path.rpartition('\\')[0] if p.__arg_repr__['_include_src_base_dir'] else p.dst_path) for p in processes]  # in the format (src_path, dst_path), ...
    for sp, dp in processes_paths:
        source_sorted_processes[sp] = []
        destination_sorted_processes[dp] = []
    for path, proc in zip(processes_paths, processes):
        source_sorted_processes[path[0]].append(proc)
        destination_sorted_processes[path[1]].append(proc)


# noinspection PyDefaultArgument
def getProcessesStats() -> tuple[float, int]:
    overall_progress: float = 0
    total_copied_bytes: int = 0
    for pr in processes:
        overall_progress += 1 if pr.process_deleted else pr.total_progress
        total_copied_bytes += pr.total_bytes_copied
    return overall_progress / processes_count, total_copied_bytes


# These Hooks can work as callbacks because they aren't running in separate threads.
processesStartedHook: HookType = Hook()  # used to start using timers to update UI.
allProcessesStoppedHook: HookType = Hook()  # used to stop using timers to update UI.
runningProcessCountChangedHook: HookType = Hook()  # used to change the running process count labels.


running_process_count: int = 0
def __increment_running_process_count(negative: bool = False, reset: bool = False) -> None:
    global running_process_count
    if reset:
        running_process_count = 0
        runningProcessCountChangedHook.emit_()
        allProcessesStoppedHook.emit_()
        return
    running_process_count += -1 if negative else 1
    if running_process_count < 0:
        running_process_count = 0
        return
    runningProcessCountChangedHook.emit_()
    if running_process_count == 1 and not negative:
        processesStartedHook.emit_()
    if running_process_count == 0 and negative:
        allProcessesStoppedHook.emit_()


def start_all_processes() -> None:
    """This function starts running processes until `concurrent_process_limit` is reached"""
    concurrent_process_limit: int = CustomSettings.concurrent_process_limit
    for pr in processes:
        if running_process_count == concurrent_process_limit:
            break
        if pr.pending:
            pr.start()
            __increment_running_process_count()


# noinspection PyDefaultArgument
def stop_all_processes() -> None:
    allow_new_multi_processes_in_sync_mode: bool = CustomSettings.allow_new_multi_processes_in_sync_mode
    for pr in processes:
        if pr.pending or pr.process_running:
            pr.stoppedHook.disconnect_(__start_next_pending_process)
            pr.syncCompleteHook.disconnect_(__start_next_pending_process) if allow_new_multi_processes_in_sync_mode else None
            pr.terminate()
            while pr.process_running:  # we must wait for the process thread to actually exit here before reconnecting the hooks below
                pass
            pr.stoppedHook.connect_(__start_next_pending_process)
            pr.syncCompleteHook.connect_(__start_next_pending_process) if allow_new_multi_processes_in_sync_mode else None
    __increment_running_process_count(reset=True)


# noinspection PyDefaultArgument
def restart_all_processes() -> None:
    for pr in processes:
        if not pr.process_running and not pr.process_deleted:
            pr.__reset_stats__()
            pr.startPending()


def __start_single_process(pr: CopyProcess | CopyProcess_NoPiping) -> None:
    if running_process_count == CustomSettings.concurrent_process_limit:
        return
    pr.start()
    __increment_running_process_count()


def __start_next_pending_process() -> None:
    """This is called whenever a process stops. This runs the first process in the processes stack. After the first process is executed, it gets popped from the stack so that the next time this function is called the next process in the stack is executed."""
    for process in processes:
        if process.pending:
            process.start()
            __increment_running_process_count()
            break
    __increment_running_process_count(negative=True)


if __name__ == "__main__":
    pass
