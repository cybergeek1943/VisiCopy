# Import Application Data
import core.os_utils
from core.settings import cdict, settings_file
import core.settings as settings
from core.config import config_file
from core.translation import set_lang, get_lang
import core.settings_parser as settings_parser
from core.importer_exporter import export_settings, import_settings
from core.os_utils import copyToClipboard

# Import Components and Visual Tools
from qfluentwidgets import (NavigationItemPosition,
                            SimpleCardWidget,
                            setFont, TitleLabel,
                            HorizontalSeparator)
from settings_window.settings_widgets import *
from ui_lib.icons import FluentIcon
from ui_lib.policy import *
from ui_lib import windows, dialogs, cards
from ui_lib import Label
from ui_components import InfoPageWidget, ListView
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import QVBoxLayout, QFileDialog, QApplication
from qfluentwidgets import setTheme, Theme as QtTheme


# put all icons code in ui_lib
tab_icons: dict = {  # based on `tab_id` from the settings dict. todo keep these tab IDs up to date with the settings data
    'subfolders': FluentIcon.FOLDER_ADD,
    'performance': FluentIcon.SPEED_HIGH,
    'filters': FluentIcon.FILTER,
    'syncing': FluentIcon.SYNC,
    'copy_options': FluentIcon.COPY,
    'logging': FluentIcon.VIEW,
}


class SettingsCard(SimpleCardWidget):
    def __init__(self, title: str, note: str | None, elements: list[dict], show_card_title: bool = False):
        SimpleCardWidget.__init__(self)
        self.setBorderRadius(16)

        layout = QVBoxLayout()
        layout.setSpacing(0)
        self.setLayout(layout)

        # Card Title
        if show_card_title:
            self.title = TitleLabel(tr(title), self)
            layout.addWidget(self.title, alignment=AlignFlag.AlignHCenter)
            setFont(self.title, 18, QFont.Weight.Bold)
            self.title.darkColor = 'lightgray'

        # Card Note
        if note:
            layout.addWidget(Label(text=tr(note), dark_color=QColor(255, 255, 255, 160), light_color=QColor(0, 0, 0, 160)))
            layout.addSpacing(20)

        # Card Elements
        self.__hierarchy__: dict = {}
        for elem in elements:
            if 'advanced' in elem and not config_file.data['advanced_mode']:
                continue
            elem_type = elem['type']

            if elem_type == 'spacer':
                layout.addSpacing(20 * elem['units'])
                if elem['divider']:
                    layout.addWidget(HorizontalSeparator())
                    layout.addSpacing(20 * elem['units'])
                continue

            sub_pos: int = elem.get('sub_pos', 0)  # used to build element hierarchy
            if elem_type == 'switch':
                e = Switch(toggled=elem['toggled'], label=tr(elem['label']), sub_pos=sub_pos, __variable__=cdict(elem))
            elif elem_type == 'checkbox':
                e = CheckBox(toggled=elem['toggled'], label=tr(elem['label']), sub_pos=sub_pos, __variable__=cdict(elem))
            elif elem_type == 'switch-str-entry':
                e = SwitchStrEntry(toggled=elem['toggled'], label=tr(elem['label']), entry=elem['entry'], placeholder=tr(elem['placeholder']), width_factor=elem['width_factor'], sub_pos=sub_pos, __variable__=cdict(elem))
            elif elem_type == 'switch-num-entry':
                e = SwitchNumEntry(toggled=elem['toggled'], label=tr(elem['label']), entry=elem['entry'], min_entry=elem['min_entry'], max_entry=elem['max_entry'], width_factor=elem['width_factor'], sub_pos=sub_pos, __variable__=cdict(elem))
            elif elem_type == 'switch-size-entry':
                e = SwitchSizeEntry(toggled=elem['toggled'], label=tr(elem['label']), entry=elem['entry'], min_entry=elem['min_entry'], max_entry=elem['max_entry'], size_options=elem['size_options'], selected_option=elem['selected_option'], width_factor=elem['width_factor'], sub_pos=sub_pos, __variable__=cdict(elem))
            elif elem_type == 'switch-date-entry':
                e = SwitchDateEntry(toggled=elem['toggled'], label=tr(elem['label']), day=elem['day'], month=elem['month'], year=elem['year'], use_days=elem['use_days'], days=elem['days'], min_days=elem['min_days'], max_days=elem['max_days'], sub_pos=sub_pos, __variable__=cdict(elem))
            elif elem_type == 'switch-dropdown':
                e = SwitchDropdown(toggled=elem['toggled'], options=tuple(tr(s) for s in elem['options']), selected_option=elem['selected_option'], sub_pos=sub_pos, __variable__=cdict(elem))
            elif elem_type == 'constant':
                e = Constant(label=tr(elem['label']), sub_pos=sub_pos, __variable__=cdict(elem))

            # noinspection PyUnboundLocalVariable
            layout.addWidget(e)
            e.setSizePolicy(SizePolicy.Fixed, SizePolicy.Fixed)

            # Structure the hierarchy - do note that the hierarchy is already calculated the moment settings in the settings_data module is initiated... the reason that it is important to recalculate here is so that when the user changes a setting the hierarchy of that element will reflect it both visually and in the settings data.
            self.__hierarchy__[sub_pos] = e
            if sub_pos != 0:
                parent = self.__hierarchy__[sub_pos - 1]
                e.set_disabled(elem["disabled"] or not parent.toggled or parent.disabled, __disable_children__=False, __update_variable__=False)
                parent.__children__.append(e)
            else:
                e.set_disabled(elem["disabled"], __disable_children__=False, __update_variable__=False)


class MainWindow(windows.SubFluentWindow):
    def __init__(self):
        windows.SubFluentWindow.__init__(self, menu_expand_width=280, remember_window_pos=True)
        # Set Window Configuration
        self.navigationInterface.setReturnButtonVisible(False)
        self.setWindowTitle(tr("Settings"))
        settings.changesDetectedHook.connect_(lambda: self.setWindowTitle(tr("Settings")) if settings.detected_changes == 0 else self.setWindowTitle(tr("Settings") + f'  •  {settings.detected_changes} ' + (tr('change') if settings.detected_changes == 1 else tr('changes'))))

        # Add to tabs the main settings from settings data
        self.navigationInterface.addSeparator()
        self.tabs: dict[str, ListView] = {}  # used to store the tab object and its route key (object name).
        for card in settings_file.data:
            if 'advanced' in card and not config_file.data['advanced_mode']:
                continue
            tab_title: str | None = card.get('tab_title', None)
            tab_id: str = card['tab_id']
            card_title: str = card['title']
            card_note: str | None = card['note']
            card_elements: list[dict] = card['elements']
            if not self.tabs.__contains__(tab_id):
                tab_object: ListView = ListView(tab_title=tr(tab_title) if tab_title else tr(card_title))
                tab_object.setObjectName(tab_id)
                tab_object.__setattr__('show_card_title', True if tab_title else False)
                self.tabs[tab_id] = tab_object
                self.addSubInterface(interface=tab_object, icon=tab_icons.get(tab_id, FluentIcon.REMOVE), text=tr(tab_title) if tab_title else tr(card_title))
            self.tabs[tab_id].add_widget(SettingsCard(title=card_title, note=card_note, elements=card_elements, show_card_title=self.tabs[tab_id].__getattribute__('show_card_title')))

        # Additional VisiCopy Config
        # TODO abstract lambdas
        configuration: ListView = ListView(tr('Configuration'))
        configuration.setObjectName('configuration')
        self.tabs['configuration'] = configuration
        configuration.add_widget(cards.SettingWSwitch(FluentIcon.APPLICATION, tr("Advanced Users"), tr('Enable more advanced features and controls for settings such as performance and logging. (requires restart)'), config_file.data['advanced_mode'], self.set_advanced_mode))
        configuration.add_widget(cards.SettingWComboBox(FluentIcon.LANGUAGE, tr('Language'), tr("Change the language from your locale's default setting. (requires restart)"), ('English', 'Español (Spanish)', '简体中文 (Chinese)', 'हिंदी (Hindi)'), get_lang(), self.set_language))
        configuration.add_widget(cards.SettingWComboBox(FluentIcon.BRUSH, tr('Theme Mode'), tr("Change the color of this application's interface."), (tr('Dark'), tr('Light'), tr('System (Auto)')), config_file.data['theme'], self.set_theme))
        if config_file.data['advanced_mode']:
            configuration.add_widget(cards.SettingWSwitch(FluentIcon.CODE, tr('Automatically Copy Parsed Settings Flags to Clipboard (Super Users)'), tr('Automatically copy the command-line flags that are used to spawn robocopy processes to the clipboard when copy starts.'), config_file.data['auto_copy_flags'], lambda b: config_file.data.__setitem__('auto_copy_flags', b)))
            configuration.add_widget(cards.SettingWPushButtons(FluentIcon.CODE, tr('Copy Parsed Settings Flags to Clipboard (Super Users)'), tr('Copy the command-line flags that are used to spawn robocopy processes to the clipboard.'), (tr('Copy to Clipboard'),), (lambda: copyToClipboard(' '.join(settings_parser.parse(settings_file.data)), app),)))
            configuration.add_widget(cards.SettingWPushButtons(FluentIcon.SAVE_COPY, tr("Import/Export Settings"), tr('You may use import/export to move VisiCopy settings between computers. (requires restart)'), (tr("Import"), tr("Export")), (self.import_settings, self.export_settings)))
        _ = cards.SettingWPushButtons(FluentIcon.HISTORY, tr('Reset Settings'), tr("Reset VisiCoy's settings back to their original defaults. (requires restart)"), (tr("Reset Settings"),), (self.reset_settings,))
        _.setButtonBorderColor(0, '#d04933')  # TODO put all styles into custom objects in UI lib!
        configuration.add_widget(_)
        self.addSubInterface(configuration, FluentIcon.DEVELOPER_TOOLS, tr('Configuration'), NavigationItemPosition.BOTTOM)

        # Info tab
        info: ListView = ListView(tr('Info'))
        info.setObjectName('info')
        info.add_widget(InfoPageWidget())
        self.addSubInterface(info, FluentIcon.INFO, tr('Info'), NavigationItemPosition.BOTTOM)

    def set_advanced_mode(self , b: bool) -> None:
        config_file.data['advanced_mode'] = b
        dialogs.info(self, tr('Restart Required'), tr('VisiCopy will close automatically. Please reopen VisiCopy for changes to take effect.'))
        config_file.save()
        # noinspection PyArgumentList
        app.exit(force_exit=True)

    def set_language(self, index: int):
        set_lang(index)
        self.restart()

    @staticmethod
    def set_theme(index: int):
        config_file.data['theme']: int = index
        setTheme(theme=QtTheme.DARK if index == 0 else QtTheme.LIGHT if index == 1 else QtTheme.AUTO)
        config_file.save()

    def reset_settings(self):
        r = dialogs.question(self, tr('Please Confirm Carefully!'),
                             tr("You are about to reset VisiCoy's settings back to their defaults.\nAre you sure you want to continue?"))
        if r != dialogs.response.Yes:
            return
        settings_file.reset()
        config_file.reset()
        settings_file.save()
        config_file.save()
        self.restart()

    def export_settings(self):
        if p := QFileDialog.getSaveFileName(self, caption=tr('Save settings to a file'), dir=f'{core.os_utils.user_docs_path}/visicopy', filter=tr('Settings (*.set)'))[0]:
            export_settings(filepath=p)

    def import_settings(self):
        if p := QFileDialog.getOpenFileName(self, caption=tr("Import settings from file"), dir=core.os_utils.user_docs_path, filter=tr('Settings (*.set)'))[0]:
            if import_settings(filepath=p):
                self.restart()
            else:
                dialogs.info(self, tr('Error'), tr('This file could not be imported because it is corrupt!'), critical=True)

    def restart(self):
        dialogs.info(self, tr('Restart Required'), tr('VisiCopy will close automatically. Please reopen VisiCopy for changes to take effect.'))
        # noinspection PyArgumentList
        app.exit(force_exit=True)


app: QApplication
settings_window: MainWindow | None = None
def start():
    global settings_window
    if not settings_window:
        settings_window = MainWindow()
    settings_window.show()
