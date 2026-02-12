from PyInstaller.utils.hooks import collect_submodules

# Rich dynamically imports unicode data modules with non-standard names
# (e.g. unicode17-0-0). Explicitly include them so PyInstaller bundles them.
hiddenimports = collect_submodules("rich._unicode_data")
