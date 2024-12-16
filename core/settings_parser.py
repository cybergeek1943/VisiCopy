from copy import deepcopy  # must deep copy raw data so the element alterations don't affect actual mutable settings data
"""Takes the settings file and extracts the settings to parse them into the relevant commands. This code is only specifically relevant to Robocopy and does not encompass all the features of the settings ui framework that could be implemented. This code could be adapted to support some other backend such as rsync."""

options_map: dict = {
    # attributes
    "read_only": "R",
    "archive": "A",
    "system": "S",
    "hidden": "H",
    "compressed": "C",
    "not_content_indexed": "N",
    "encrypted": "E",
    "temporary": "T",
    "offline": "O",

    # copy options
    "data": "D",  # both files & dirs
    "attributes": "A",  # both files & dirs
    "timestamps": "T",  # both files & dirs
    "skip_alt_data_streams": "X",  # both files & dirs
    "ntfs_acl": "S",  # files only
    "owner_info": "O",  # files only
    "audit_info": "U",  # files only
    "extended_attributes": "E",  # dirs only
}  # contains the args for flags used in robocopy


# These parser flags tell the paser what the args should expect from settings widgets. These flags or specifically designed for the settings widgets currently being used
# `opt--` tells the parser to expect options as input
# `str--` tells the parser to expect strings as input
# `qstr--` tells the parser to expect a string as input. Similar to -str but wraps the string in quotation marks "".
# `num--` tells the parser to expect values such as integers or floats as input
# `size--` tells the parser to expect a size as input
# `date--` tells the parser to expect a file size as input
# `combo--` tells the parser to expect a selected item from a dropdown as input
arg_map: dict = {
    # Sub-folders
    "recursive": "/s",
    "n_levels": "/lev num--",
    "copy_empty_folders": "/e",
    "only_structure": "/e /xf *",
    "create_zero_length": "/create",

    # Performance
    "use_unbuffered": "/j",
    "multi-thread": "/mt num--",
    "throttle_threshold": "/threshold size--",  # don't need -s here because robocopy already implements conversion
    "throttle_rate": "/iorate size--",  # don't need -s here because robocopy already implements conversion
    "throttle_cycle": "iomaxsize size--",  # don't need -s here because robocopy already implements conversion
    "network_compression": "/compress",
    "retain_sparse_state": "/sparce",
    "inter_packet_gap": "/ipg num--",

    # Basic Filters
    "max_size": "/max size--",
    "min_size": "/min size--",
    "exclude_files": "/xf str--",
    "exclude_folders": "/xd str--",
    "max_age": "/maxage date--",
    "min_age": "/minage date--",
    "max_last_access": "/maxlad date--",
    "min_last_access": "/minlad date--",

    # Attribute Filters
    "only_archived": "/a",
    "remove_archive_attrib": "/m",
    "exclude_files_with_attrib": "/xa opt--",
    "include_files_with_attrib": "/ia opt--",

    # Source/Destination Relation Filters
    "include_existing": "/is",
    "exclude_newer": "/xn",
    "exclude_older": "/xo",
    "exclude_changed": "/xc",
    "exclude_lonely": "/xl",
    "include_tweaked": "/it",

    # Syncing & Continuous Monitoring
    "mirror_src_to_dst": "/purge",  # use /purge instead of /mir because user needs control over recursive copy using /s or /e
    "sync_every_n_change": "/mon num--",
    "sync_every_n_min": "/mot num--",
    "revaluate_security_attributes": "/secfix",
    "revaluate_timestamps": "/timfix",

    # Copy Options
    "move_files": "/mov",  # uses /mov because it does not delete the entire src dir when /e is used like /move does
    "copy_symbolic_link": "/sl",
    "retry_limit": "/r num--",
    "retry_wait": "/w num--",
    "copy_file_properties": "/copy opt--",
    "copy_folder_properties": "/dcopy opt--",
    "add_attr": "/a+ opt--",
    "remove_attr": "/a- opt--",
    "assume_fat_file_times": "/fft",
    "efs_raw_mode": "/efsraw",
    "legacy_name_mode": "/fat",

    # Logging
    "log_path": "/log qstr--",
    "console_and_log": "/tee",
    "show_paths": "/fp",
    "show_timestamps": "/ts",
    "show_file_size": "/ns",
    "use_bytes_for_file_size": "/bytes",
    "show_file_progress": "/np",
    "show_file_eta": "/eta",
    "verbose": "/v",
    "show_extras": "/x",
    "list_only": "/l",
    "use_unicode": "/unicode",
}


def size_value_to_bytes(size_value: int, option: int) -> int:
    """Takes a value specified by `size_value` and then converts it to bytes int using `option` where 0 is bytes, 1 is kilobytes, 2 is megabytes, 3 is gigabytes, and 4 is terabytes.
    >>> size_value_to_bytes(1, 4)
    1000000000000
    >>> size_value_to_bytes(1, 3)
    1000000000
    >>> size_value_to_bytes(1, 2)
    1000000
    """
    return size_value*(10**(0, 3, 6, 9, 12)[option])

    # return size_value*(10**(0 if option == 0 else 3 if option == 1 else 6 if option == 2 else 9 if option == 3 else 0))


def date_str(year: int, month: int, day: int) -> str:
    """Returns the date as a string."""
    return f'{year}{'0' if 10 > month else ''}{month}{'0' if 10 > day else ''}{day}'


def _flatten_settings_to_elem_list(raw_data: list) -> list:
    """Takes the settings data and puts all the elements from each section into a list that's ready to parsed"""
    out: list = []
    for section in raw_data:
        out.extend(section['elements'])
    return out


def _parse_settings(data: list) -> list:
    """This function is only designed to parse for robocopy... but can be easily tweaked for other purposes."""
    # output vars
    args: list[str,] = []  # parsed args

    args_to_override: list = []
    elem_is_option: bool = False  # used for adding sub-elements as option to args
    for elem in data:
        if elem['type'] == 'spacer':
            continue

        # ---------------- Element Processing ----------------
        # Disabled Element Handling
        if elem.get('disabled_default'):
            elem: dict = deepcopy(elem)
            for k, v in elem.get('disabled_default').items():
                elem[k] = v
            elem['disabled'] = False  # fake element as enabled even if elem is disabled
        if elem['disabled']:  # if element is disabled then do not continue analysis
            continue

        # Element Alterations
        if elem.get('override') and elem['toggled']:
            elem: dict = deepcopy(elem)
            for o in elem.get('override'):
                if elem['toggled'] == o[0]:
                    args_to_override.append(arg_map[o[1]])
        if elem.get('inverse'):
            elem: dict = deepcopy(elem)
            elem['toggled'] = not elem['toggled']

        # skip custom elements here
        if elem.get('custom'):
            continue

        # ---------------- Parser ----------------
        # Get the element ID
        elem_id: str | tuple = elem.get('id')
        if elem['type'] == 'switch-dropdown':  # set the correct element ID depending on dropdown selection
            elem_id: str = elem_id[elem['selected_option']]

        # Add element as option to parent arg if applicable
        if elem_is_option and elem.get('sub_pos', 0) == 0:  # if current element is not a sub-element
            if args[-1][-1] == ':':  # if no sub elements were added as options to the parent element
                del args[-1]
            elem_is_option = False
        if elem_is_option and elem['toggled']:  # only works if current element is a sub-element
            args[-1] = f'{args[-1]}{options_map[elem_id]}'
            continue

        # If the element is not activated even after processing than it gets thrown out.
        if not elem['toggled']:  # must be after the option adder above, otherwise a bug occurs because if next elements is not an option and is toggled off `elem_is_option` will remain true.
            continue

        arg: str = arg_map[elem_id]
        if arg[-2:] == '--':  # if arg expects its own args/flags
            # Check args expected input values and act accordingly
            arg, _, input_type = arg.partition(' ')
            if input_type == 'opt--':  # if arg expects options
                args.append(f'{arg}:')
                elem_is_option = True  # do this so that future elements will be considered as options if their sub_pos is > 0
                continue
            elif input_type == 'qstr--':
                args.append(f'{arg}:"{elem['entry']}"')
            elif input_type == 'num--' or input_type == 'str--':
                args.append(f'{arg}:{elem['entry']}')
            elif input_type == 'size--':
                args.append(f'{arg}:{size_value_to_bytes(size_value=elem['entry'], option=elem['selected_option'])}')
            elif input_type == 'date--':
                if elem['use_days']:
                    args.append(f'{arg}:{elem['days']}')
                else:
                    args.append(f'{arg}:{date_str(year=elem['year'], month=elem['year'], day=elem['day'])}')
            elif input_type == 'combo--':
                args.append(f'{arg}:{elem['options'][elem['selected_option']]}')
        else:  # if no input to args is needed
            args.append(arg)

    # Remove the overridden args
    for oa in args_to_override:
        for i, a in enumerate(args):
            if a.startswith(oa):
                del args[i]

    return args


def parse(data: list) -> list:
    """Parse the settings to robocopy commands"""
    return _parse_settings(_flatten_settings_to_elem_list(data))
