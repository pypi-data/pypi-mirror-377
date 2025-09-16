"""
Setup script for loghtml package.
This file ensures compatibility with PyInstaller and other build tools.
"""

from setuptools import setup, find_packages
import os

# Read the current directory
here = os.path.abspath(os.path.dirname(__file__))

# Ensure package data is included
package_data = {
    'loghtml': ['template.html', 'py.typed', '_pyinstaller_hook.py']
}

setup(
    packages=find_packages(),
    package_data=package_data,
    include_package_data=True,
    zip_safe=False,  # Important for PyInstaller compatibility
)