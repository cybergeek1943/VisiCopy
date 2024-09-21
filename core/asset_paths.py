"""This file contains the paths to all assets and resources used by the code."""
from core import assets_rc
logoIconPath: str = ':/assets/icon.ico'


class MainIconPaths:
    selectSource: str = ':/assets/main/source.png'
    selectDestination: str = ':/assets/main/destination.png'
    startCopy: str = ':/assets/main/start.png'
    dragDrop: str = ':/assets/main/drag_drop.png'
    logoWName: str = ':/assets/main/logo_name.png'
    jobsIcon: str = ':/assets/main/jobs.png'
    driveIcon: str = ':/assets/main/drive.png'
    dropdownIcon: str = ':/assets/main/dropdown.png'


class ProcessStatusIconPaths:
    pending: str = ':/assets/process_manager/pending.png'
    complete: str = ':/assets/process_manager/complete.png'
    monitoring: str = ':/assets/process_manager/monitoring.png'
    stoppedMidway: str = ':/assets/process_manager/stopped_midway.png'
    completeWithError: str = ':/assets/process_manager/complete_with_error.png'


# pyside6-rcc assets.qrc -o assets_rc.py
# pyside6-rcc lang.qrc -o lang_rc.py
