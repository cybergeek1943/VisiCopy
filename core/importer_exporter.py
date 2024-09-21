import core.settings_data as settings_data
import core.settings_parser as settings_parser
import core.config as preferences
import json


def export_settings(filepath: str) -> None:
    """Export the settings for the currently selected job as a (.set) file."""
    with open(filepath, 'w') as f:
        f.write(json.dumps(settings_data.settings))


def import_settings(filepath: str) -> bool:
    """Import settings (.set) to current job from external file. If successful, return True. Restart of Easy Copy is required."""
    try:
        with open(filepath, mode='r') as f:
            settings_data.settings.clear()
            settings_data.settings = json.loads(f.read())
            settings_data.save_settings()
            settings_data.__init_quick_access_settings()
        return True
    except (FileNotFoundError, json.JSONDecodeError):
        return False


def export_preferences(filepath: str) -> None:
    """Exports a (.udat) file to `filepath`"""
    settings_data.save_settings()
    userdata_file: dict = {
        'settings_data': settings_data.settings,
        'preferences_config': preferences.preferences,
    }
    with open(filepath, 'w') as f:  # save the `userdata_file` to `filepath`
        f.write(json.dumps(userdata_file))


def import_preferences(filepath: str) -> bool:
    """`filepath` expects a (.udat) file. Restart of Easy Copy required."""
    try:
        preferences.del_old_files()
        with open(filepath, 'r') as f:
            userdata_file: dict = json.loads(f.read())
            preferences.preferences.clear()
            preferences.preferences = userdata_file['preferences_config']
            settings_data.settings.clear()
            settings_data.settings = userdata_file['settings_data']
        preferences.save_config()
        settings_data.save_settings()
        return True
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return False


def export_job_file(filepath: str, sources: list[tuple[str, dict]], destinations: list[str]) -> None:
    """Export the settings along with the selected sources and destinations as a (.job) file."""
    userdata_file: dict = {
        'settings_data': settings_data.settings,
        'sources': sources,
        'destinations': destinations,
    }
    with open(filepath, 'w') as f:
        f.write(json.dumps(userdata_file))


def import_job_file(filepath: str) -> tuple[list[list[str, dict]], list[str], list[dict]] | None:
    """Imports the compiled flags from settings along with the selected sources and destinations from a (.job) file. Return the sources and destinations in a tuple (sources, destinations, process_flags: list[str], use_gui: bool)."""
    try:
        with open(filepath, mode='r') as f:
            job_file: dict = json.loads(f.read())
            return job_file['sources'], job_file['destinations'], job_file['settings_data']
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def clear_job_file():
    settings_data.__load_settings()
