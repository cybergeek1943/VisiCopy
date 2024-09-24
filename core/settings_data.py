"""Contains the code for loading and saving settings data."""
from copy import deepcopy
import json
import core.config as preferences
from core.hooks import Hook, HookType

MAX_INT: int = 2147483647  # this is the maximum integer possible because of C++ restraint


# Element Builders
# NOTE: if these components are changed then the program will crash (because of key errors) if we do not re-initiate the json file
# NOTE: __default_settings should only define layout and information... not styling
# NOTE: currently the `disabled` key is only used to store/initiate information about the disabled state of an element... it can automatically be flipped on/off depending on its `sub_pos` relationship with a parent element.


def spacer(units: int = 1, divider: bool = False) -> dict:
    return {'type': 'spacer', 'units': units, 'divider': divider}


def constant(label: str,
             disabled: bool = False,  # used of sub-elements
             **kwargs):
    """This element should entail a constant setting with sub-settings... sort of like a switch that's always on."""
    return {'type': 'constant', 'label': label, 'disabled': disabled, 'toggled': True, 'id': '', **kwargs}


def switch(label: str,
           toggled: bool,
           disabled: bool = False,
           **kwargs) -> dict:
    return {'type': 'switch', 'label': label, 'toggled': toggled, 'disabled': disabled, **kwargs}


def checkBox(label: str,
             toggled: bool,
             disabled: bool = False,
             **kwargs) -> dict:
    return {'type': 'checkbox', 'label': label, 'toggled': toggled, 'disabled': disabled, **kwargs}


def switchStrEntry(label: str,
                   toggled: bool,
                   entry: str = '',
                   placeholder: str = '',
                   width_factor: int = 0,  # if 0, the default is used.
                   disabled: bool = False,
                   **kwargs) -> dict:
    # generally use `placeholder` only when displaying info about what to enter; conversely, put default values in `entry` instead of `placeholder`
    return {'type': 'switch-str-entry', 'label': label, 'toggled': toggled, 'entry': entry, 'placeholder': placeholder, 'width_factor': width_factor, 'disabled': disabled, **kwargs}


def switchNumEntry(label: str,
                   toggled: bool,
                   entry: int | float = 0,  # explicitly pass a float here if the number entry should support floats
                   min_entry: int | float = 0,
                   max_entry: int | float = MAX_INT,
                   width_factor: int = 0,
                   disabled: bool = False,
                   **kwargs) -> dict:
    return {'type': 'switch-num-entry', 'label': label, 'toggled': toggled, 'entry': entry, 'min_entry': min_entry, 'max_entry': max_entry, 'width_factor': width_factor, 'disabled': disabled, **kwargs}


def switchSizeEntry(label: str,
                    toggled: bool,
                    entry: int = 1,
                    min_entry: int = 1,
                    max_entry: int = MAX_INT,
                    size_options: tuple = ('Bytes', 'Kilobytes', 'Megabytes', 'Gigabytes'),
                    selected_option: int = 2,
                    width_factor: int = 0,
                    disabled: bool = False,
                    **kwargs) -> dict:
    return {'type': 'switch-size-entry', 'label': label, 'toggled': toggled, 'entry': entry, 'min_entry': min_entry, 'max_entry': max_entry, 'size_options': size_options, 'selected_option': selected_option, 'width_factor': width_factor, 'disabled': disabled, **kwargs}


def switchDateEntry(label: str,
                    toggled: bool,
                    day: int = 0,
                    month: int = 0,
                    year: int = 0,
                    use_days: bool = False,
                    days: int = 7,
                    min_days: int = 1,
                    max_days: int = 1899,
                    disabled: bool = False,
                    **kwargs) -> dict:
    return {'type': 'switch-date-entry', 'label': label, 'toggled': toggled, 'day': day, 'month': month, 'year': year, 'use_days': use_days, 'days': days, 'min_days': min_days, 'max_days': max_days, 'disabled': disabled, **kwargs}


def switchDropdown(toggled: bool,
                   options: tuple,
                   selected_option: int = 0,
                   disabled: bool = False,
                   **kwargs) -> dict:
    # default option is options[0]
    # id must also be a tuple
    return {'type': 'switch-dropdown', 'toggled': toggled, 'options': options, 'selected_option': selected_option, 'disabled': disabled, **kwargs}


tr: callable = lambda _: _  # dummy callable used to register strings for translation
""" Parser args for these elements (added using **kwargs). The parser assumes that all elements (elements that own settings to their name) have a "toggle" value key.
`disabled_default`={toggled: True|False, entry: Any, <{kwargs}...>}  use this to tell the parser what the element should evaluated as when it is disabled
`override`=[(True|False, <id>), ...]  use this to override other elements in parser... `True|False` specifies the value of self element when the `<id>` should disabled/removed. This is put into effect when toggled is true. (this does not effect `custom` elements) (only works for switches and checkboxes with no entry or sub-options due to the way the parser is written)
`inverse`=True  use this to tell the parser that the elements boolean value should be inverted when considering its arg status
`custom`=True  use this to tell the parser that the element is custom and cannot be mapped to an argument.
`expose`=True  use this to make elements accessible in `exposed_setting` variable.
`id`=<name>  use this to give shortened name to element to be accessed by parser. For `switchDropdown()`, pass a tuple of IDs for each item in dropdown.
"""
""" Each entry in the settings below is a card. Each card is placed into a tab using 'tab_id'
'tab_title': this is optional and is used only if more than one card will be placed in the same tab. It tells the GUI parser to mark the tab as containing more than one card and to display card title on each card.
'tab_id': this places the card into the tab differentiated by this id. The IDs now being used are mapped to specific icons.
'title': this is the title of the card and will be displayed on the card only if there is more than one card in the tab. Otherwise, this title will be used for the tab title instead.
'note': this places a note at the beginning of the card.
'elements': contains the UI elements to placed in the card.
"""
""" Extra Args for elements
'sub_pos': This is an `int` that set the elements sub position giving us the ability to nest elements and make a "tree". This should only be used of the element has a 'disabled' arg.
"""
__default_settings: list = [
    {
        'tab_id': 'subfolders',
        'title': tr('Subfolders'),
        'note': None,
        'elements': [
            # related
            switch(tr('Copy all subfolders'), toggled=True, expose=True, id='recursive'),
            switchNumEntry(tr('Only n levels deep'), toggled=False, entry=10, sub_pos=1, id='n_levels'),
            switch(tr('Copy empty folders'), toggled=True, sub_pos=1, id='copy_empty_folders'),

            # related
            switch(tr('Only copy the folder-tree structure'), toggled=False, id='only_structure'),
            switch(tr('Create zero-size files with same names as in source'), toggled=False, sub_pos=1, id='create_zero_length', override=[(True, 'only_structure')]),
        ]
    },
    {
        'tab_id': 'performance',
        'title': tr('Performance'),
        'note': tr('Note that when multiprocessing is enabled, multiple copy processes are created in the following circumstances:'
                   '\n• When there are multiple sources'
                   '\n• When there are multiple destinations selected'),
        'elements': [
            switch(tr('Use unbuffered I/O (recommended for larger files)'), toggled=True, id='use_unbuffered'),
            switchNumEntry(tr('Multi-Threading per-process (use 1-128 threads)'), toggled=True, entry=8, min_entry=1, max_entry=128, id='multi-thread'),
            switchNumEntry(tr('Multiprocessing - max number of processes to run simultaneously when copying from multiple sources or copying to multiple destinations (1-32)'), toggled=True, entry=8, min_entry=1, max_entry=32, id='multiprocess', custom=True),
            checkBox(tr('Prioritize multiple destinations (de-prioritizes multiple sources)'), toggled=True, sub_pos=1, id='prioritize_dst', custom=True),
            checkBox(tr('Allow next pending process to run when a currently running process is finished and in Continuous Monitoring/Sync Mode'), toggled=True, sub_pos=1, id='allow_new_multi_processes_in_sync_mode', custom=True),
            spacer(divider=True),

            switchSizeEntry(tr('Apply the following throttle settings for files greater than'), toggled=False, entry=1, id='throttle_threshold'),
            switchSizeEntry(tr('Throttle the I/O rate to n amount per second'), toggled=False, selected_option=2, sub_pos=1, id='throttle_rate'),
            switchSizeEntry(tr('Max I/O size per read/write cycle'), toggled=False, selected_option=2, sub_pos=1, id='throttle_cycle'),
            spacer(divider=True),

            switch(tr('Use SMB compression for copies over network (can improve speed significantly)'), toggled=False, id='network_compression'),
            switch(tr('Optimize the sparse state of files (useful for large files with lots of empty data. e.g. large database files with lots of empty space get optimized for storage)'), toggled=True, id='retain_sparse_state', inverse=True),
            switchNumEntry(tr('Specify the IPG (inter-packet gap) in milliseconds to free up bandwidth on slow lines (can effect performance; research best IPG for your network)'), toggled=False, entry=0.096, id='inter_packet_gap'),
        ]
    },
    {
        'tab_title': tr('Filters'),
        'tab_id': 'filters',
        'title': tr('Basic Filters'),
        'note': None,
        'elements': [
            switchSizeEntry(tr('Exclude files larger than'), toggled=False, id='max_size'),
            switchSizeEntry(tr('Exclude files smaller than'), toggled=False, id='min_size'),
            spacer(divider=True),

            switchDateEntry(tr('Maximum file age - exclude files older than'), toggled=False, id='max_age'),
            switchDateEntry(tr('Minimum file age - exclude files newer than'), toggled=False, id='min_age'),
            switchDateEntry(tr('Maximum last access date - exclude files unused since'), toggled=False, id='max_last_access'),
            switchDateEntry(tr('Minimum last access date - exclude files used since'), toggled=False, id='min_last_access'),
            spacer(divider=True),

            switchStrEntry(tr('Only copy files matching the given names/wildcards (separated by a space)'), toggled=False, placeholder=tr('e.g.,   *.txt   "file name.*"'), width_factor=3, id='only_specified_files', custom=True),  # could use non-custom /if:files here... but then specified file selection may be grouped with extra unexpected files from that src directory
            switchStrEntry(tr("Exclude files matching the given names/wildcards/paths (separated by a space)"), toggled=False, placeholder=tr('e.g.,   *.mp4   "file name.*"   "path"'), width_factor=3, id='exclude_files'),
            switchStrEntry(tr("Exclude folders matching the given names/wildcards/paths (separated by a space)"), toggled=False, placeholder=tr('e.g.,   *.mp4   "file name.*"   "path"'), width_factor=3, id='exclude_folders'),
        ]
    },
    {
        'tab_id': 'filters',
        'title': tr('Attribute Filters'),
        'note': None,
        'elements': [
            # related
            switch(tr('Copy only files with the Archive attribute'), toggled=False, id='only_archived'),
            switch(tr('Remove the Archive attribute from files in source after copy'), toggled=False, sub_pos=1, id='remove_archive_attrib'),
            spacer(),

            switchDropdown(toggled=False, options=(tr("Don't copy files with the following attributes"), tr('Only copy files with the following attributes')), id=('exclude_files_with_attrib', 'include_files_with_attrib')),
            checkBox(tr('Read Only'), toggled=False, sub_pos=1, id='read_only'),
            checkBox(tr('Archive'), toggled=False, sub_pos=1, id='archive'),
            checkBox(tr('System'), toggled=False, sub_pos=1, id='system'),
            checkBox(tr('Hidden'), toggled=False, sub_pos=1, id='hidden'),
            checkBox(tr('Compressed'), toggled=False, sub_pos=1, id='compressed'),
            checkBox(tr('Not Content Indexed'), toggled=False, sub_pos=1, id='not_content_indexed'),
            checkBox(tr('Encrypted'), toggled=False, sub_pos=1, id='encrypted'),
            checkBox(tr('Temporary'), toggled=False, sub_pos=1, id='temporary'),
            checkBox(tr('Offline'), toggled=False, sub_pos=1, id='offline')
        ]
    },
    {
        'tab_id': 'filters',
        'title': tr('Source/Destination Relation Filters'),
        'note': tr('Note:'
                   '\n• These settings are for the relations between files that already exists in the source and/or destination.'
                   '\n• By default, a file in both the source and destination is compared using the Name, Size, and Timestamps.'
                   '\n• A file from source that already exists in destination is not copied by default.'
                   '\n• If a file already exists in the destination but is still copied from source anyway, it will overwrite the file in the destination.'
                   '\n• The term "source pool" means the collection of files from source that will be copied to destination.'),
        'elements': [
            # Related - because the sub settings deal with still excluding files
            switch(tr('Include files that already exist in destination to source pool (disables the comparison of size and timestamps in source and destination)'), toggled=False, id='include_existing'),
            switch(tr('Exclude files from source pool that are newer than the files already existing in destination (uses "modified" timestamp to compare)'), toggled=False, sub_pos=1, id='exclude_newer'),
            switch(tr('Exclude files from source pool that are older than the files already existing in destination (uses "modified" timestamp to compare)'), toggled=False, sub_pos=1, id='exclude_older'),
            switch(tr('Exclude files from source pool that have the same timestamps but different sizes than the files already existing in destination'), toggled=False, sub_pos=1, id='exclude_changed'),
            spacer(divider=True),

            switch(tr('Exclude "lonely" files that do not exist in destination from source pool - prevents new items in destination'), toggled=False, id='exclude_lonely'),
            switch(tr('Include "tweaked" files to source pool - if any attribute of file in source is different, than overwrite file in destination'), toggled=False, id='include_tweaked'),
        ]
    },
    {
        'tab_id': 'syncing',
        'title': tr('Syncing & Continuous Monitoring'),
        'note': None,
        'elements': [
            switch(tr('Keep the destination as a mirror of source - will delete items in destination that are no longer in source'), toggled=False, id='mirror_src_to_dst'),

            switchNumEntry(tr('Monitor source and update destination after n changes happen'), toggled=False, entry=1, expose=True, id='sync_every_n_change'),
            switchNumEntry(tr('Wait in intervals of n minutes before updating destination'), toggled=False, entry=1, expose=True, id='sync_every_n_min', sub_pos=1),

            switch(tr('Revaluate security attributes on files already in destination and fix them if they have changed in source. (happens per pass)'), toggled=False, id='revaluate_security_attributes'),
            switch(tr('Revaluate timestamps on files already in destination and fix them if they have changed in source. (happens per pass)'), toggled=False, id='revaluate_timestamps'),
        ]
    },
    {
        'tab_id': 'copy_options',
        'title': tr('Copy Options'),
        'note': None,
        'elements': [
            switch(tr('Move files from source - deletes files from source after copy is complete'), toggled=False, id='move_files'),
            switch(tr('Copy the symbolic link (.lnk) target instead of the (.lnk) file itself'), toggled=False, id='copy_symbolic_link', inverse=True),
            switchNumEntry(tr('Number of retries per failed copy of a file'), toggled=True, entry=10, expose=True, id='retry_limit'),
            switchNumEntry(tr('Number of seconds to wait before retrying'), toggled=True, entry=5, sub_pos=1, expose=True, id='retry_wait'),
            spacer(divider=True),

            # related
            constant(tr("Copy the following file properties:"), id='copy_file_properties'),
            checkBox(tr('File Data'), toggled=True, sub_pos=1, id='data'),
            checkBox(tr('Attributes'), toggled=True, sub_pos=1, id='attributes'),
            checkBox(tr('Timestamps'), toggled=True, sub_pos=1, id='timestamps'),
            checkBox(tr('Owner Information'), toggled=False, sub_pos=1, id='owner_info'),
            checkBox(tr('Auditing Information'), toggled=False, sub_pos=1, id='audit_info'),
            checkBox(tr('NTFS access control list (ACL)'), toggled=False, sub_pos=1, id='ntfs_acl'),
            checkBox(tr('Skip alt data streams'), toggled=False, sub_pos=1, id='skip_alt_data_streams'),
            spacer(),

            # related
            constant(tr("Copy the following folder properties:"), id='copy_folder_properties'),
            checkBox(tr('Folder Data'), toggled=True, sub_pos=1, id='data'),
            checkBox(tr('Attributes'), toggled=True, sub_pos=1, id='attributes'),
            checkBox(tr('Timestamps'), toggled=True, sub_pos=1, id='timestamps'),
            checkBox(tr('Extended Attributes'), toggled=False, sub_pos=1, id='owner_info'),
            checkBox(tr('Skip alt data streams'), toggled=False, sub_pos=1, id='skip_alt_data_streams'),
            spacer(divider=True),

            # related
            switch(tr('Add the following attributes to items copied to destination:'), toggled=False, id='add_attr'),
            checkBox(tr('Read Only'), toggled=False, sub_pos=1, id='read_only'),
            checkBox(tr('Archive'), toggled=False, sub_pos=1, id='archive'),
            checkBox(tr('System'), toggled=False, sub_pos=1, id='system'),
            checkBox(tr('Hidden'), toggled=False, sub_pos=1, id='hidden'),
            checkBox(tr('Compressed'), toggled=False, sub_pos=1, id='compressed'),
            checkBox(tr('Not Content Indexed'), toggled=False, sub_pos=1, id='not_content_indexed'),
            checkBox(tr('Encrypted'), toggled=False, sub_pos=1, id='encrypted'),
            checkBox(tr('Temporary'), toggled=False, sub_pos=1, id='temporary'),
            spacer(),

            # related
            switch(tr('Remove the following attributes on items copied to destination:'), toggled=False, id='remove_attr'),
            checkBox(tr('Read Only'), toggled=False, sub_pos=1, id='read_only'),
            checkBox(tr('Archive'), toggled=False, sub_pos=1, id='archive'),
            checkBox(tr('System'), toggled=False, sub_pos=1, id='system'),
            checkBox(tr('Hidden'), toggled=False, sub_pos=1, id='hidden'),
            checkBox(tr('Compressed'), toggled=False, sub_pos=1, id='compressed'),
            checkBox(tr('Not Content Indexed'), toggled=False, sub_pos=1, id='not_content_indexed'),
            checkBox(tr('Encrypted'), toggled=False, sub_pos=1, id='encrypted'),
            checkBox(tr('Temporary'), toggled=False, sub_pos=1, id='temporary'),
            spacer(divider=True),

            switch(tr('Assume FAT File Times (2-second date/time granularity) - use this when copying files to a linux NAS or other non-windows file system'), toggled=False, id='assume_fat_file_times'),
            switch(tr('Copy any encrypted files using EFS RAW mode (can disable multi-threading)'), toggled=False, id='efs_raw_mode'),
            switch(tr('Create destination files using 8.3 FAT file names only (legacy)'), toggled=False, id='legacy_name_mode'),
        ]
    },
    {
        'tab_id': 'logging',
        'title': tr('Logging & Progress Status'),
        'note': None,
        'elements': [
            # related
            constant(tr('When using the process manager GUI:'), custom=True),
            switch(tr('Show full path of each file being copied'), toggled=False, id='gui_show_full_file_path', custom=True, sub_pos=1),
            switchNumEntry(tr('Calculate Speed and ETA every n seconds'), toggled=True, entry=8, id='speed_eta_seconds_interval', custom=True, sub_pos=1),
            switchNumEntry(tr('Use n progress-checkpoint samples for calculating the ETA'), toggled=True, entry=32, id='eta_progress_checkpoints', custom=True, sub_pos=1),
            spacer(),

            switchStrEntry(tr('Save Log file to path'), toggled=False, placeholder=tr(r'path\to\folder\file_name.log'), width_factor=3, id='log_path'),
            spacer(),

            # related
            switch(tr("Don't use the process manager GUI (spawn consoles instead)"), toggled=False, id='show_console', custom=True),
            checkBox(tr("Don't show copy status in console (only show in log file)"), toggled=False, sub_pos=1, id='console_and_log', inverse=True),
            checkBox(tr('Show full file paths'), toggled=False, sub_pos=1, id='show_paths'),
            checkBox(tr('Show file timestamps'), toggled=False, sub_pos=1, id='show_timestamps'),
            checkBox(tr('Show file sizes'), toggled=True, sub_pos=1, id='show_file_size', inverse=True),
            checkBox(tr('Use bytes only'), toggled=False, sub_pos=2, id='use_bytes_for_file_size'),
            checkBox(tr('Show per-file progress'), toggled=False, sub_pos=1, id='show_file_progress', inverse=True),
            checkBox(tr('Show per-file ETA'), toggled=False, sub_pos=1, id='show_file_eta'),
            checkBox(tr('Enable verbose mode (show skipped files in output)'), toggled=False, sub_pos=1, id='verbose'),
            checkBox(tr('Show all extra files, not just the ones selected'), toggled=False, sub_pos=1, id='show_extras'),
            checkBox(tr("Only list the files, don't copy anything. (useful for testing selections)"), toggled=False, sub_pos=1, id='list_only'),
            checkBox(tr('Use unicode encoding'), toggled=False, sub_pos=1, id='use_unicode'),
        ]
    }
]


def __set_element_hierarchy():
    """This function runs only when the __default_settings is used to start a new setting.json file. It takes care of assigning disabled status to elements based on their hierarchy so that the parser will accurately parse settings that should be disabled."""
    __hierarchy__: dict = {}
    for card in __default_settings:
        for elem in card['elements']:
            if not elem.__contains__('disabled'):  # stop here if element type is unsupported in the hierarchy (does not have an explicit `disabled` arg)
                continue
            sub_pos: int = elem.get('sub_pos', 0)
            __hierarchy__[sub_pos] = elem
            if sub_pos != 0:
                parent = __hierarchy__[sub_pos - 1]
                elem['disabled'] = not parent['toggled'] or parent['disabled']


# ---------------- Settings Management ----------------
settings: list = []  # this is the settings that is accessible


def __load_settings(load_defaults: bool = False) -> None:
    global settings
    if load_defaults:
        __set_element_hierarchy()
        settings = deepcopy(__default_settings)
        __init_quick_access_settings()
        return
    settings_path: str = preferences.paths.settingsPath
    try:
        with open(settings_path, mode='r') as f:
            settings = json.loads(f.read())
        __init_quick_access_settings()
    except (FileNotFoundError, json.JSONDecodeError):  # if error occurs then reload default settings.
        __set_element_hierarchy()
        with open(settings_path, mode='w') as f:
            f.write(json.dumps(__default_settings))
        __load_settings()  # recursively call to reload settings


pre_job_load_settings: list[dir] | None = None
def load_job_file_settings(settings_data: list[dir]) -> None:
    global settings, pre_job_load_settings
    pre_job_load_settings = settings
    settings = settings_data
    __init_quick_access_settings()
def exit_job_file_settings() -> None:
    global settings, pre_job_load_settings
    if pre_job_load_settings is None:
        return
    settings = pre_job_load_settings
    __init_quick_access_settings()
    pre_job_load_settings = None


def save_settings() -> None:
    with open(preferences.paths.settingsPath, mode='w') as f:
        f.write(json.dumps(settings))
    set_detected_changes(0)


def reset_settings() -> None:
    global settings
    __set_element_hierarchy()
    settings = deepcopy(__default_settings)  # we must deepcopy so that the default settings to get overwritten when they are changed by user.
    __init_quick_access_settings()
    set_detected_changes(0)


changes_detected: int = 0
class cdict(dict):
    """Use this to as the object to pass to __variable__ in the settings ui manager. This way we know when the settings are changed by user."""
    def __init__(self, elem: dict):
        super().__init__(elem)  # this creates a copy of the `elem` initial state when `elem is created` because dict({}) creates a copy of its arg data.
        self.elem: dict = elem  # this is the fluid copy of `elem` which gets updated by the user interactions with the user interface.

    def __setitem__(self, key, value):
        if self.elem[key] != value and key != 'disabled':  # if the key's value is not already the same AND also the key is not a "disable" type of key.
            if self[key] == value:  # if the original `elem`'s value is equal to the new value
                set_detected_changes(n=-1, add_n=True)
            elif self[key] == self.elem[key]:  # if the current value of key is equal to the original value of key... makes it so that only one change adds to counter and not many changes.
                set_detected_changes(n=1, add_n=True)
        self.elem.__setitem__(key, value)
def set_detected_changes(n: int, add_n: bool = False) -> None:
    global changes_detected
    if add_n:
        changes_detected += n
    else:
        changes_detected = n
    changesDetectedHook()
changesDetectedHook: HookType = Hook()


# ---------------- Quick Settings Retrieval (used for process manager to easily retrieve settings.) ----------------
exposed_settings: dict = {}  # Exposed settings of non-custom elements containing the expose keyword... this is used by CopyProcess to anticipate flags such as those causing recursion.
""" Current Settings in `exposed_settings`:
"recursive",
"retry_limit",
"retry_wait",
"sync_every_n_change",
"sync_every_n_min"
"""

from core import os_utils
custom_settings: dict = {}  # Non-robocopy settings that are used for extra features of VisiCopy
class __CustomSettings__:  # TODO must keep this up to date with the id names of custom settings that need quick access.
    """Custom Settings Singleton"""
    @property
    def use_gui(self) -> bool:
        return not custom_settings['show_console']['toggled']

    @property
    def concurrent_process_limit(self) -> int:
        return custom_settings['multiprocess']['entry'] if custom_settings['multiprocess']['toggled'] and custom_settings['multiprocess']['entry'] else 1

    @property
    def dst_prioritized(self) -> bool:
        return custom_settings['prioritize_dst']['toggled']

    @property
    def allow_new_multi_processes_in_sync_mode(self) -> bool:
        return custom_settings['allow_new_multi_processes_in_sync_mode']['toggled']

    @property
    def selector_pattern(self) -> list | tuple:
        return os_utils.arg_split(custom_settings['only_specified_files']['entry']) if custom_settings['only_specified_files']['toggled'] and custom_settings['only_specified_files']['entry'] else os_utils.DEFAULT_PATTERN

    @property
    def gui_show_full_file_path(self) -> bool:
        return custom_settings['gui_show_full_file_path']['toggled']

    @property
    def speed_eta_seconds_interval(self) -> int:
        return custom_settings['speed_eta_seconds_interval']['entry'] if custom_settings['speed_eta_seconds_interval']['toggled'] else 0

    @property
    def eta_progress_checkpoints(self) -> int:
        return custom_settings['eta_progress_checkpoints']['entry'] if custom_settings['eta_progress_checkpoints']['toggled'] else 1
CustomSettings: __CustomSettings__ = __CustomSettings__()


def __init_quick_access_settings():  # only call locally in this module when settings are loaded from files or reset.
    """this must be called whenever settings are loaded from file or reset."""
    exposed_settings.clear()
    custom_settings.clear()
    for c in settings:  # todo must keep this up to date with the layout of settings
        for e in c['elements']:
            if e.get('custom') and e['id'] != '':
                custom_settings[e['id']] = e
            if e.get('expose'):
                exposed_settings[e['id']] = e


# ---------------- load settings when module is run ----------------
__load_settings()