"""This file contains all icon resources"""
from ui_lib import assets_rc
from qfluentwidgets import FluentIcon  # we can call the FluentIcon to get fluent widget icons
logoIcon: str = ':/assets/icon.ico'


class MainIcon:
    """Contains the icons used in the main window."""
    selectSource: str = ':/assets/main/source.png'
    selectDestination: str = ':/assets/main/destination.png'
    startCopy: str = ':/assets/main/start.png'
    dragDrop: str = ':/assets/main/drag_drop.png'
    logoWName: str = ':/assets/main/logo_name.png'
    jobsIcon: str = ':/assets/main/jobs.png'
    driveIcon: str = ':/assets/main/drive.png'
    dropdownIcon: str = ':/assets/main/dropdown.png'


class ProcessManagerIcon:
    """Contains the icons used in the process manager window."""
    pending: str = ':/assets/process_manager/pending.png'
    complete: str = ':/assets/process_manager/complete.png'
    monitoring: str = ':/assets/process_manager/monitoring.png'
    stoppedMidway: str = ':/assets/process_manager/stopped_midway.png'
    completeWithError: str = ':/assets/process_manager/complete_with_error.png'


# Use this to compile the resource files into python code:
# pyside6-rcc assets.qrc -o ./ui_lib/assets_rc.py
