import os
import platform
import json
from copy import deepcopy
from core.hooks import Hook, HookType
__debug_mode__: bool = False  # enable to only load from default data rather than from actual userdata file
__store_in_cd__: bool = False  # enable to store the userdata in current directory for debugging purposes
__app_name__: str = "VisiCopy"
__version__: str = "1.0.0"


def get_appdata_directory() -> str:
    if __store_in_cd__:
        return '.'
    match platform.system():
        case 'Windows':
            return os.path.join(os.getenv('APPDATA'), __app_name__)
        case 'Darwin':  # Mac OS
            return os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', __app_name__)
        case _:  # Linux and other Unix-like systems
            return os.path.join(os.path.expanduser('~'), f'.{__app_name__}')


class UserdataFile:
    """Interface for loading and saving user data."""
    def __init__(self, filename: str, default_data: dict | list):
        os.makedirs(directory := get_appdata_directory(), exist_ok=True)
        self.file_path: str = os.path.join(directory, f'{filename}_{__version__}.json')
        self.default_data: dict | list = default_data
        self.data: dict | list = {}

        # Hooks
        self.onLoad: HookType = Hook()
        self.onSave: HookType = Hook()
        self.onReset: HookType = Hook()

    def save(self) -> None:
        with open(self.file_path, mode='w') as f:
            f.write(json.dumps(self.data))
        self.onSave()

    def reset(self) -> None:
        self.data = deepcopy(self.default_data)
        self.save()
        self.onReset()

    def load(self) -> None:
        if __debug_mode__:
            self.data = deepcopy(self.default_data)
            self.onLoad()
            return
        try:
            with open(self.file_path, mode='r') as f:
                self.data = json.loads(f.read())
            self.onLoad()
        except (FileNotFoundError, json.JSONDecodeError):  # if error occurs then reload default settings.
            with open(self.file_path, mode='w') as f:
                f.write(json.dumps(self.default_data))
            self.load()  # recursively call to reload settings
