"""
PyInstaller hook for loghtml package.
This file is automatically detected and used by PyInstaller when building executables.
"""

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect all data files from loghtml package
datas = collect_data_files('loghtml')

# Ensure all submodules are included
hiddenimports = collect_submodules('loghtml')

# Specifically include the template.html file
datas += [
    ('template.html', 'loghtml'),
]

# Add the package itself to hidden imports
hiddenimports.extend([
    'loghtml',
    'loghtml.core',
    'loghtml.writer',
    'loghtml.config',
])