from core.userdata_io import UserdataFile
"""Contains the default configurations of the settings and basic application config. It also contains the interfaces """
class ThemeMode:
    DARK: int = 0
    LIGHT: int = 1
    AUTO: int = 2


class SettingsMode:
    Normal: int = 0
    Advanced: int = 1


__default_config: dict = {
    'mode': SettingsMode.Normal,  # type: int  # -1 means not specified yet.
    'language': -1,  # type: int  # -1 means not specified yet.
    'theme': ThemeMode.DARK,  # type: int
    'auto_copy_flags': False,  # type: bool
    'win_pos': None,  # type: tuple[int, int] | list[int, int]
    'win_size': (1600, 900),  # type: tuple[int, int] | list[int, int]
    'win_max': False,  # type: bool
}


config_file: UserdataFile = UserdataFile(filename='config', default_data=__default_config)
config_file.load()
