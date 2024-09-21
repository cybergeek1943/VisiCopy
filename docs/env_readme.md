# Updating and Installing all package requirements.
A local venv is used so that no bloat occurs in the package requirements when freezing and so that 

Note: `pip freeze > requirements.txt` was used make a requirements list from the manually installed packages. The version specification have been removed so that upgrades will work.

- Activate local env using `./venv/Scripts/activate` (`deactivate` later.) in the *cmd*. This is done so that pip will only be local.
- `pip install --upgrade -r requirements.txt` is used to update all packages.

This venv must not be hosted on GitHub. Make git ignore the venv dir by putting `venv/` in the `.gitignore` file.

The .gitignore file should look something like this:
```text
venv/
test/
output/
deployment/
*.json
*.cfg
*.set
*.udat
*.exe
```
