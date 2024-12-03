"""Contains the code for loading and saving the userdata data.
The userdata is what stores the location of the current settings, jobs, language, theme, etc.

The preferences.cfg is what stores user preferences such as theme and language.
The job.cfg is a single file that store all the jobs and the currently selected job."""
from copy import deepcopy
import json
import os


user_docs_path: str = os.path.expanduser('~\\Documents')  # TODO use separate module for OS interaction


class ThemeMode:
    DARK: int = 0
    LIGHT: int = 1
    AUTO: int = 3


__default_preferences: dict = {
    'language': -1,  # type: int  # -1 means not specified yet.
    'theme': ThemeMode.DARK,  # type: int
    'auto_copy_flags': False,  # type: bool
    'win_pos': None,  # type: tuple[int, int] | list[int, int]
    'win_size': (1600, 900),  # type: tuple[int, int] | list[int, int]
    'win_max': False,  # type: bool
}


# ---------------- Config Management ----------------
preferences: dict = {}


class __Path:  # SINGLETON CLASS!
    """Singleton class that stores all paths for user data in file system."""
    def __init__(self):
        self.userdataDirPath: str = '.'  # this is the directory where all user data such as settings and preferences are stored
        self.preferencesConfigPath: str = f'{self.userdataDirPath}/preferences.cfg'

    @property
    def settingsPath(self) -> str:
        return f'{self.userdataDirPath}/settings.set'
paths: __Path = __Path()


def __load_config(load_default: bool = False) -> None:
    global preferences
    if load_default:
        preferences = deepcopy(__default_preferences)
        return
    try:
        with open(paths.preferencesConfigPath, mode='r') as f:
            preferences = json.loads(f.read())
    except (FileNotFoundError, json.JSONDecodeError):  # if error occurs then reload default config.
        with open(paths.preferencesConfigPath, mode='w') as f:
            f.write(json.dumps(__default_preferences))
        __load_config()  # recursively call to reload config
__load_config()


def save_config() -> None:
    with open(paths.preferencesConfigPath, mode='w') as f:
        f.write(json.dumps(preferences))


def reset_config() -> None:
    global preferences
    preferences = deepcopy(__default_preferences)
    del_old_files()


def del_old_files() -> None:
    for f in os.listdir(paths.userdataDirPath):  # remove any old settings or config files
        if f.endswith('.set') or f.endswith('.cgf'):
            os.remove(f'{paths.userdataDirPath}\\{f}')
