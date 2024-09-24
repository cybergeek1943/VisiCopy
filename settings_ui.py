# Import Application Data
from core.settings_data import cdict, save_settings, reset_settings
import core.settings_data as settings_data
from core import config
from core.translation import tr, set_lang, get_lang
import core.settings_parser as settings_parser
from core.importer_exporter import export_settings, import_settings, export_preferences, import_preferences
from core.os_utils import copyToClipboard

# Import Components and Visual Tools
from qfluentwidgets import (NavigationItemPosition,
                            SimpleCardWidget,
                            setFont, TitleLabel,
                            HorizontalSeparator)
from ui_comps.settings_ui_comps import Switch, CheckBox, SwitchStrEntry, SwitchNumEntry, SwitchSizeEntry, SwitchDateEntry, SwitchDropdown, Constant
from ui_comps import Icons, AlignFlag, SizePolicy, primitives, cards, windows, dialogs, InfoPageWidget
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import QVBoxLayout, QFileDialog, QApplication
from qfluentwidgets import setTheme, Theme as QtTheme


tab_icons: dict = {  # based on `tab_id` from the settings dict. todo keep these tab IDs up to date with the settings data
    'subfolders': Icons.FOLDER_ADD,
    'performance': Icons.SPEED_HIGH,
    'filters': Icons.FILTER,
    'syncing': Icons.SYNC,
    'copy_options': Icons.COPY,
    'logging': Icons.VIEW,
}


class Card(SimpleCardWidget):
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
            layout.addWidget(primitives.Label(text=tr(note), dark_color=QColor(255, 255, 255, 160), light_color=QColor(0, 0, 0, 160)))
            layout.addSpacing(20)

        # Card Elements
        self.__hierarchy__: dict = {}
        for elem in elements:
            elem_type = elem['type']

            if elem_type == 'spacer':
                layout.addSpacing(20*elem['units'])
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


class MainWindow(windows.SubWindow):
    def __init__(self):
        windows.SubWindow.__init__(self, menu_expand_width=280, remember_window_pos=True)
        # Set Window Configuration
        self.navigationInterface.setReturnButtonVisible(False)
        self.setWindowTitle(tr("Settings"))
        settings_data.changesDetectedHook.connect_(lambda: self.setWindowTitle(tr("Settings")) if settings_data.changes_detected == 0 else self.setWindowTitle(tr("Settings") + f'  •  {settings_data.changes_detected} ' + (tr('change') if settings_data.changes_detected == 1 else tr('changes'))))

        # Add to tabs the main settings from settings data
        self.navigationInterface.addSeparator()
        self.tabs: dict[str, windows.TabComponent] = {}  # used to store the tab object and its route key (object name).
        for card in settings_data.settings:
            tab_title: str | None = card.get('tab_title', None)
            tab_id: str = card['tab_id']
            card_title: str = card['title']
            card_note: str | None = card['note']
            card_elements: list[dict] = card['elements']
            if not self.tabs.__contains__(tab_id):
                tab_object: windows.TabComponent = windows.TabComponent(tab_title=tr(tab_title) if tab_title else tr(card_title))
                tab_object.setObjectName(tab_id)
                tab_object.__setattr__('show_card_title', True if tab_title else False)
                self.tabs[tab_id] = tab_object
                self.addSubInterface(interface=tab_object, icon=tab_icons.get(tab_id, Icons.REMOVE), text=tr(tab_title) if tab_title else tr(card_title))
            self.tabs[tab_id].add_widget(Card(title=card_title, note=card_note, elements=card_elements, show_card_title=self.tabs[tab_id].__getattribute__('show_card_title')))

        # Add the additional user preferences from userdata
        preferences: windows.TabComponent = windows.TabComponent(tr('Preferences'))
        preferences.setObjectName('preferences')
        self.tabs['preferences'] = preferences
        preferences.add_widget(cards.SettingWComboBox(Icons.LANGUAGE, tr('Language'), tr('Currently, four languages are supported. More will be added in future releases.'), ('English', 'Español (Spanish)', '简体中文 (Chinese)', 'हिंदी (Hindi)'), get_lang(), self.set_language))
        preferences.add_widget(cards.SettingWComboBox(Icons.BRUSH, tr('Theme Mode'), tr("Change the color of this application's interface."), (tr('Dark'), tr('Light'), tr('System (Auto)')), config.preferences['theme'], self.set_theme))
        preferences.add_widget(cards.SettingWPushButtons(Icons.SAVE_COPY, tr("Import/Export Settings"), tr('You may use import/export to move VisiCopy settings between computers.'), (tr("Import"), tr("Export")), (self.import_settings, self.export_settings)))
        preferences.add_widget(cards.SettingWPushButtons(Icons.SAVE_COPY, tr('Import/Export All Userdata'), tr('You may use import/export to move the settings and preferences between computers.'), (tr("Import"), tr("Export")), (self.import_preferences, self.export_preferences)))
        preferences.add_widget(cards.SettingWPushButtons(Icons.CODE, tr('Copy Parsed Settings Flags to Clipboard (Super Users)'), tr('Copy the command-line flags that are used to spawn robocopy processes to the clipboard.'), (tr('Copy to Clipboard'),), (lambda: copyToClipboard(' '.join(settings_parser.parse(settings_data.settings)), app),)))
        preferences.add_widget(cards.SettingWSwitch(Icons.CODE, tr('Automatically Copy Parsed Settings Flags to Clipboard (Super Users)'), tr('Automatically copy the command-line flags that are used to spawn robocopy processes to the clipboard when copy starts.'), config.preferences['auto_copy_flags'], lambda b: config.preferences.__setitem__('auto_copy_flags', b)))
        _ = cards.SettingWPushButtons(Icons.HISTORY, tr('Reset Settings and/or Preferences'), tr('You may reset either the Settings (which manages how copy processes behave) or the User Preferences (such as language, theme, & window position.).'), (tr("Reset Settings"), tr("Reset Preferences")), (self.reset_settings, self.reset_preferences))
        _.setButtonBorderColor(0, '#d04933')
        _.setButtonBorderColor(1, '#d04933')
        preferences.add_widget(_)
        self.addSubInterface(preferences, Icons.DEVELOPER_TOOLS, tr('Preferences'), NavigationItemPosition.BOTTOM)

        # Add Info tab
        info: windows.TabComponent = windows.TabComponent(tr('Info'))
        info.setObjectName('info')
        info.add_widget(InfoPageWidget())
        self.addSubInterface(info, Icons.INFO, tr('Info'), NavigationItemPosition.BOTTOM)

    def set_language(self, index: int):
        set_lang(index)
        self.restart()

    @staticmethod
    def set_theme(index: int):
        config.preferences['theme']: int = index
        setTheme(theme=QtTheme.DARK if index == 0 else QtTheme.LIGHT if index == 1 else QtTheme.AUTO)
        config.save_config()

    def reset_settings(self):
        r = dialogs.question(self, tr('Please Confirm Carefully!'),
                             tr('You are about to reset the settings that control how copy processes behave.\nAre you sure you want to continue?'))
        if r != dialogs.response.Yes:
            return
        reset_settings()
        save_settings()
        self.restart()

    def reset_preferences(self):
        r = dialogs.question(self, tr('Please Confirm!'),
                             tr('You are about to reset preferences such as language, theme, and window position.\nAre you sure you want to continue?'))
        if r != dialogs.response.Yes:
            return
        config.reset_config()
        config.save_config()
        self.restart()

    def export_settings(self):
        if p := QFileDialog.getSaveFileName(self, caption=tr('Save settings as a file'), dir=f'{config.user_docs_path}/settings', filter=tr('Settings (*.set)'))[0]:
            export_settings(filepath=p)

    def import_settings(self):
        if p := QFileDialog.getOpenFileName(self, caption=tr("Import settings file"), dir=config.user_docs_path, filter=tr('Settings (*.set)'))[0]:
            self.restart() if import_settings(filepath=p) else dialogs.info(self, tr('Error'), tr('This file could not be imported because it is corrupt!'), critical=True)

    def export_preferences(self):
        if p := QFileDialog.getSaveFileName(self, caption=tr('Save user preferences as a file'), dir=f'{config.user_docs_path}/visicopy', filter=tr('Userdata (*.udat)'))[0]:
            export_preferences(filepath=p)

    def import_preferences(self):
        if p := QFileDialog.getOpenFileName(self, caption=tr("Import user preferences file!"), dir=config.user_docs_path, filter=tr('Userdata (*.udat)'))[0]:
            if import_preferences(filepath=p):
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
