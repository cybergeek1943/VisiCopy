from core import lang_rc
from warnings import warn
from core.config import preferences, save_config
from PySide6.QtCore import QObject, QCoreApplication, QTranslator, QLocale


class __TranslationDummy(QObject):
    """Used to register strings for translation using lupdate with `r` as `tr` alias."""
    @staticmethod
    def settings_strings(r: callable):
        # Subfolders
        r('Copy all subfolders')
        r('Only n levels deep')
        r('Copy empty folders')
        r('Only copy the folder-tree structure')
        r('Create zero-size files with same names as in source')

        # Performance
        r('Note that when multiprocessing is enabled, multiple copy processes are created in the following circumstances:'
          '\n• When there are multiple sources'
          '\n• When there are multiple destinations selected')
        r('Use unbuffered I/O (recommended for larger files)')
        r('Multi-Threading per-process (use 1-128 threads)')
        r('Multiprocessing - max number of processes to run simultaneously when copying from multiple sources or copying to multiple destinations (1-32)')
        r('Prioritize multiple destinations (de-prioritizes multiple sources)')
        r('Allow next pending process to run when a currently running process is finished and in Continuous Monitoring/Sync Mode')
        r('Apply the following throttle settings for files greater than')
        r('Throttle the I/O rate to n amount per second')
        r('Max I/O size per read/write cycle')
        r('Use SMB compression for copies over network (can improve speed significantly)')
        r('Optimize the sparse state of files (useful for large files with lots of empty data. e.g. large database files with lots of empty space get optimized for storage)')
        r('Specify the IPG (inter-packet gap) in milliseconds to free up bandwidth on slow lines (can effect performance; research best IPG for your network)')

        # Basic Filters
        r('Exclude files larger than')
        r('Exclude files smaller than')
        r('Maximum file age - exclude files older than')
        r('Minimum file age - exclude files newer than')
        r('Maximum last access date - exclude files unused since')
        r('Minimum last access date - exclude files used since')
        r('Only copy files matching the given names/wildcards (separated by a space)')
        r('Exclude files matching the given names/wildcards/paths (separated by a space)')
        r('Exclude folders matching the given names/wildcards/paths (separated by a space)')

        # Attribute Filters
        r('Copy only files with the Archive attribute')
        r('Remove the Archive attribute from files in source after copy')
        r("Don't copy files with the following attributes")
        r('Only copy files with the following attributes')

        # Source/Destination Relation Filters
        r('Note:'
          '\n• These settings are for the relations between files that already exists in the source and / or destination.'
          '\n• By default, a file in both the source and destination is compared using the Name, Size, and Timestamps.'
          '\n• A file from source that already exists in destination is not copied by default.'
          '\n• If a file already exists in the destination but is still copied from source anyway, it will overwrite the file in the destination.'
          '\n• The term "source pool" means the collection of files from source that will be copied to destination.')
        r('Include files that already exist in destination to source pool (disables the comparison of size and timestamps in source and destination)')
        r('Exclude files from source pool that are newer than the files already existing in destination (uses "modified" timestamp to compare)')
        r('Exclude files from source pool that are older than the files already existing in destination (uses "modified" timestamp to compare)')
        r('Exclude files from source pool that have the same timestamps but different sizes than the files already existing in destination')
        r('Exclude "lonely" files that do not exist in destination from source pool - prevents new items in destination')
        r('Include "tweaked" files to source pool - if any attribute of file in source is different, than overwrite file in destination')

        # Syncing and Continuous Monitoring
        r('Keep the destination as a mirror of source - will delete items in destination that are no longer in source')
        r('Monitor source and update destination after n changes happen')
        r('Wait in intervals of n minutes before updating destination')
        r('Revaluate security attributes on files already in destination and fix them if they have changed in source. (happens per pass)')
        r('Revaluate timestamps on files already in destination and fix them if they have changed in source. (happens per pass)')

        # Copy Options
        r('Move files from source - deletes files from source after copy is complete')
        r('Copy the symbolic link (.lnk) target instead of the (.lnk) file itself')
        r('Number of retries per failed copy of a file')
        r('Number of seconds to wait before retrying')
        r('Copy the following file properties:')
        r('Copy the following folder properties:')
        r('Add the following attributes to items copied to destination:')
        r('Remove the following attributes on items copied to destination:')
        r('Assume FAT File Times (2-second date/time granularity) - use this when copying files to a linux NAS or other non-windows file system')
        r('Copy any encrypted files using EFS RAW mode (can disable multi-threading)')
        r('Create destination files using 8.3 FAT file names only (legacy)')

        # Logging & Progress Status
        r('When using the process manager GUI:')
        r('Show full path of each file being copied')
        r('Calculate Speed and ETA every n seconds')
        r('Use n progress-checkpoint samples for calculating the ETA')
        r('Save Log file to path')
        r("Don't use the process manager GUI (spawn consoles instead)")
        r("Don't show copy status in console (only show in log file)")
        r('Show full file paths')
        r('Show file timestamps')
        r('Show file sizes')
        r('Use bytes only')
        r('Show per-file progress')
        r('Show per-file ETA')
        r('Enable verbose mode (show skipped files in output)')
        r('Show all extra files, not just the ones selected')
        r("Only list the files, don't copy anything.(useful for testing selections)")
        r('Use unicode encoding')

        # Sub Argument Options
        r('Read Only')
        r('Archive')
        r('System')
        r('Hidden')
        r('Compressed')
        r('Not Content Indexed')
        r('Encrypted')
        r('Temporary')
        r('Offline')
        r('File Data')
        r('Folder Data')
        r('Attributes')
        r('Timestamps')
        r('Owner Information')
        r('Auditing Information')
        r('NTFS access control list (ACL)')
        r('Extended Attributes')
        r('Skip alt data streams')

        # Section Titles
        r('Subfolders')
        r('Performance')
        r('Filters')
        r('Basic Filters')
        r('Attribute Filters')
        r('Source/Destination Relation Filters')
        r('Syncing & Continuous Monitoring')
        r('Copy Options')
        r('Logging & Progress Status')

        # Placeholders
        r('path\\to\\folder\\file_name.log')
        r('e.g.,   *.txt   "file name.*"')
        r('e.g.,   *.mp4   "file name.*"   "path"')

    @staticmethod
    def preferences_strings(r: callable):
        # Language
        r('Language')
        r('Currently, four languages are supported. More will be added in future releases.')

        # Theme
        r('Theme Mode')
        r("Change the color of this application's interface.")
        r('Dark')
        r('Light')
        r('System (Auto)')

        # Import/export
        r("Import/Export this Job's Settings")
        r('You may use import/export to move the settings for the currently selected job between computers.')
        r('Import/Export All Userdata')
        r('You may use import/export to move the Settings, Preferences, and Jobs between computers.')

        # Copy Parsed to Clipboard
        r('Copy Parsed Settings Flags to Clipboard (Super Users)')
        r('Copy the command-line flags that are used to spawn robocopy processes to the clipboard.')
        r('Copy to Clipboard')

        # Auto Copy Parsed to Clipboard
        r('Automatically Copy Parsed Settings Flags to Clipboard (Super Users)')
        r('Automatically copy the command-line flags that are used to spawn robocopy processes to the clipboard when copy starts.')

        # Reset User Data
        r('Reset Settings and Userdata')
        r('You may reset either the settings for the current job or reset all user data and delete all jobs.')
        r("Reset this Job's Settings")
        r('Reset all Userdata')

    @staticmethod
    def words_strings(r: callable):
        r('Preferences')
        r('Settings')
        r('Cancel')
        r('Ok')
        r('Yes')
        r('No')
        r('change')
        r('changes')
        r('Import')
        r('Export')
        r('Error')
        r('Bytes')
        r('Kilobytes')
        r('Megabytes')
        r('Gigabytes')
        r('Date')
        r('Days')
        r('day')
        r('month')
        r('year')
        r('On')
        r('Off')
        r('January')
        r('February')
        r('March')
        r('April')
        r('May')
        r('June')
        r('July')
        r('August')
        r('September')
        r('October')
        r('November')
        r('December')

    @staticmethod
    def notices_strings(r: callable):
        r('Please Confirm Carefully!')
        r('You are about to reset all settings, delete all Jobs, and restore these preferences back to their defaults.\nAre you sure you want to continue?')
        r('You are about to reset the settings for this job to their defaults.\nAre you sure you want to continue?')
        r('Confirm Change')
        r('You have made 1 change.\nDo you want to save this change?')
        r('You have made {} changes.\nDo you want to save these changes?')
        r("Import Settings File  -  Warning: this will override the current job's settings!")
        r('Save Settings as a File')
        r('Settings (*.set)')
        r('Import Userdata File  -  Warning: this will override all current userdata!')
        r('Save All Userdata as a File')
        r('Userdata (*.udat)')
        r('This file could not be imported because it is corrupt!')


class Language:
    # must follow order of 'english', 'spanish', 'chinese', 'hindi'
    ENGLISH: int = 0
    SPANISH: int = 1
    CHINESE: int = 2
    HINDI: int = 3


def lang_enum_to_code(lang: int) -> str:
    return ('en', 'es', 'zh', 'hi')[lang]


def lang_code_to_enum(code: str) -> int:
    try:
        return ('en', 'es', 'zh', 'hi').index(code)
    except ValueError:
        return -1


def init_translator(app: QCoreApplication):
    """Used to load the translation files. Only call once"""
    if get_lang() == Language.ENGLISH:
        return
    translator: QTranslator = QTranslator(app)
    translator.load(f':\\i18n\\{lang_enum_to_code(get_lang())}.qm')
    app.installTranslator(translator)


# Functions
def set_lang(lang: int) -> None:
    if lang == -1:
        lang = 0
    preferences['language']: int = lang
    save_config()


def get_lang() -> int:
    return preferences['language']


def get_system_lang_code() -> str:
    return QLocale.system().name().split('_')[0]


if get_lang() == -1:
    set_lang(lang_code_to_enum(get_system_lang_code()))
if get_lang() == Language.ENGLISH:
    def tr(src_str: str):
        return src_str
else:
    def tr(src_str: str):
        o: str = QCoreApplication.translate('app', src_str)
        if o == src_str:
            warn(f'The below string was not found in the translation file!\n"{src_str}"\n', stacklevel=2)
        return o


# todo NOTE: .ts files must manually have their "<name></name>" set to "<name>app</name>" for `tr()` to work
# pyside6-lupdate ".\core\translation.py" -ts ".\i18n\zh.ts" -tr-function-alias tr=r
# pyside6-lrelease ".\i18n\zh.ts" -qm ".\i18n\zh.qm"
