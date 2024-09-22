files: list[str] = [
        ".\\main.py",
        ".\\settings_ui.py",
        ".\\source_selection_ui.py",
        ".\\destination_selection_ui.py",
        ".\\process_manager_ui.py",
        ".\\ui_comps\\__init__.py",
        ".\\ui_comps\\selection_ui_comps.py",
        ".\\ui_comps\\settings_ui_comps.py",
        ".\\core\\settings_data.py",
        ".\\core\\translation.py"
]

inpt: str = input('Enter name of .ts file: ')
print('pyside6-lupdate', end=' ')
for fp in files:
    print(f'"{fp}"', end=' ')
print(fr'-ts ".\i18n\{inpt}.ts" -no-obsolete -tr-function-alias tr=tr')
