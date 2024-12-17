from core.settings import settings_file
from core.config import config_file
import json


def export_settings(filepath: str) -> None:
    """Exports a (.udat) file to `filepath`"""
    userdata_file: dict = {
        'config_data': config_file.data,
        'settings_data': settings_file.data
    }
    with open(filepath, 'w') as f:  # save the `userdata_file` to `filepath`
        f.write(json.dumps(userdata_file))


def import_settings(filepath: str) -> bool:
    """`filepath` expects a (.udat) file. Restart of VisiCopy required."""
    try:
        with open(filepath, 'r') as f:
            userdata_file: dict = json.loads(f.read())
            config_file.data = userdata_file['config_data']
            settings_file.data = userdata_file['settings_data']
        config_file.save()
        settings_file.save()
        return True
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return False


# TODO reimplement the Job export functions after the Job manager is further improved.
# def export_job_file(filepath: str, sources: list[tuple[str, dict]], destinations: list[str]) -> None:
#     """Export the settings along with the selected sources and destinations as a (.job) file."""
#     userdata_file: dict = {
#         'settings_data': settings_file.data,
#         'sources': sources,
#         'destinations': destinations,
#     }
#     with open(filepath, 'w') as f:
#         f.write(json.dumps(userdata_file))
#
#
# def import_job_file(filepath: str) -> tuple[list[list[str, dict]], list[str], list[dict]] | None:
#     """Imports the compiled flags from settings along with the selected sources and destinations from a (.job) file. Return the sources and destinations in a tuple (sources, destinations, process_flags: list[str], use_gui: bool)."""
#     try:
#         with open(filepath, mode='r') as f:
#             job_file: dict = json.loads(f.read())
#             return job_file['sources'], job_file['destinations'], job_file['settings_data']
#     except (FileNotFoundError, json.JSONDecodeError):
#         return None
