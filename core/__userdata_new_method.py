import os
import platform
import json
APP_NAME = "Easy Copy"

class UserdataFile:  # TODO modify this for VisiCopy
    """Singleton interface for loading and saving user data."""
    __debug_mode__: bool = False

    def __init__(self):
        self.data: list[str] = []  # actual data to be stored.
        os.makedirs(directory:=self.get_appdata_directory(), exist_ok=True)
        self.file_path: str = os.path.join(directory, 'userdata.json') if not self.__debug_mode__ else '.\\userdata.json'
        self.__load()

    @staticmethod
    def get_appdata_directory() -> str:
        match platform.system():
            case 'Windows':
                return os.path.join(os.getenv('APPDATA'), APP_NAME)
            case 'Darwin':  # Mac OS
                return os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', APP_NAME)
            case _:  # Linux and other Unix-like systems
                return os.path.join(os.path.expanduser('~'), f'.{APP_NAME}')

    def set_data(self, data: list[str]) -> None:
        self.data = data

    def get_data(self) -> list[str]:
        return self.data

    def save_changes(self) -> None:
        with open(self.file_path, mode='w') as f:
            f.write(json.dumps(self.data))

    def __load(self) -> None:
        try:
            with open(self.file_path, mode='r') as f:
                self.data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):  # if error occurs then reload default settings.
            self.save_changes()
            self.__load()
userdata_file: UserdataFile = UserdataFile()