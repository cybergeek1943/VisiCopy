from core import lang_rc
from warnings import warn
from core.config import config_file
from PySide6.QtCore import QObject, QCoreApplication, QTranslator, QLocale

tr: callable = lambda _: None  # dummy callable used to register additional strings for translation
tr('day')
tr('month')
tr('year')
tr('January')
tr('February')
tr('March')
tr('April')
tr('May')
tr('June')
tr('July')
tr('August')
tr('September')
tr('October')
tr('November')
tr('December')


class Language:
    # must follow order of 'english', 'spanish', 'chinese', 'hindi'
    ENGLISH: int = 0
    SPANISH: int = 1
    CHINESE: int = 2
    HINDI: int = 3


def lang_enum_to_code(lang: int) -> str:
    """Converts a language enum value to its corresponding language code.
    >>> lang_enum_to_code(2)
    'zh'
    >>> lang_enum_to_code(0)
    'en'
    """
    return ('en', 'es', 'zh', 'hi')[lang]


def lang_code_to_enum(code: str) -> int:
    """Converts a language code (e.g., 'en', 'es') to its corresponding enum value.
    >>> lang_code_to_enum('es')
    1
    >>> lang_code_to_enum('hi')
    3
    """
    try:
        return ('en', 'es', 'zh', 'hi').index(code)
    except ValueError:
        return -1


def init_translator(app: QCoreApplication):
    """Used to load the translation files and install them into `app`. Only call this once."""
    if get_lang() == Language.ENGLISH:
        return
    translator: QTranslator = QTranslator(app)
    translator.load(f':\\i18n\\{lang_enum_to_code(get_lang())}.qm')
    app.installTranslator(translator)


# Functions
def set_lang(lang: int) -> None:
    """Sets the application's language to the specified enum value and saves the setting to the configuration file."""
    if lang == -1:
        lang = Language.ENGLISH
    config_file.data['language']: int = lang
    config_file.save()


def get_lang() -> int:
    """Retrieves the current language setting from the configuration file."""
    return config_file.data['language']


def get_system_lang_code() -> str:
    """Returns the system's default language code (e.g., 'en', 'es') based on the system's locale."""
    return QLocale.system().name().split('_')[0]


if get_lang() == -1:
    set_lang(lang_code_to_enum(get_system_lang_code()))
if get_lang() == Language.ENGLISH:
    def tr(src_str: str):
        return src_str
else:
    def tr(src_str: str):
        o: str = QCoreApplication.translate('', src_str)
        if __debug__ and o == src_str:  # debug is false when program is frozen
            warn(f'The below string was not found in the translation file or may be the same word in "{get_lang()}" as "en"!\n"{src_str}"\n', stacklevel=2)
        return o


# todo NOTE: .ts files must not contain anything in their "<name></name>"  for `tr()` to work because "<name>" holds the context
# use translation_command_gen.py to generate lupdate command and run it for each language
# pyside6-lrelease ".\i18n\zh.ts" -qm ".\i18n\zh.qm"
# pyside6-rcc lang.qrc -o ./core/lang_rc.py
# use translation_command_gen.py to make a lupdate command for all ui files.
