import os
core_path: str = '../core'
home_ui_path: str = '../ui_components'
main_path: str = '..'
line_count: int = 0
for f in os.listdir(core_path):
    if f.endswith('.py'):
        with open(os.path.join(core_path, f), 'r', encoding='UTF-8') as file:
            line_count += file.read().count('\n')
for f in os.listdir(home_ui_path):
    if f.endswith('.py'):
        with open(os.path.join(home_ui_path, f), 'r', encoding='UTF-8') as file:
            line_count += file.read().count('\n')
for f in os.listdir(main_path):
    if f.endswith('.py'):
        with open(os.path.join(main_path, f), 'r', encoding='UTF-8') as file:
            line_count += file.read().count('\n')
print(line_count)
