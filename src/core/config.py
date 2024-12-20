from core.userdata_io import UserdataFile
"""Contains the default configuration of the basic application config."""


__default_config: dict = {
    'advanced_mode': False,  # type: bool
    'language': -1,  # type: int  # -1 means not specified yet.
    'auto_copy_flags': False,  # type: bool
    'win_pos': None,  # type: tuple[int, int] | list[int, int]
    'win_size': (1600, 900),  # type: tuple[int, int] | list[int, int]
    'win_max': False,  # type: bool
}


config_file: UserdataFile = UserdataFile(filename='config', default_data=__default_config)
config_file.load()
