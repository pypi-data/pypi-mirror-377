#!/usr/bin/env python

from setuptools import setup, find_packages
from pathlib import Path
import os
import traceback

NAME = "gitignore"

def get_version():
    """
    Get the version.
    Version is taken from the __version__.py file if it exists.
    The content of __version__.py should be:
    version = "0.33"
    """
    try:
        version_file = Path(__file__).parent / "__version__.py"
        if not version_file.is_file():
            version_file = Path(__file__).parent / NAME / "__version__.py"
        if version_file.is_file():
            with open(version_file, "r") as f:
                for line in f:
                    if line.strip().startswith("version"):
                        parts = line.split("=")
                        if len(parts) == 2:
                            return parts[1].strip().strip('"').strip("'")
    except Exception as e:
        if os.getenv('TRACEBACK') and os.getenv('TRACEBACK') in ['1', 'true', 'True']:
            print(traceback.format_exc())
        else:
            print(f"ERROR: {e}")

    return "0.0.0"

def get_long_description():
    """
    Get the long description from the README.md file.
    """
    readme_file = Path(__file__).parent / "README.md"
    if readme_file.is_file():
        with open(readme_file, "r", encoding="utf-8") as f:
            return f.read()
    return ""

setup(
    name="gitign",
    version=get_version(),
    description="A powerful and user-friendly Python script to generate `.gitignore` files with default entries, custom patterns, or templates from gitignore.io",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    keywords="gitignore gitignore.io rich terminal",
    project_urls={
        "Bug Tracker": "https://github.com/cumulus13/gitignore/issues",
    },
    author="Hadi Cahyadi",
    author_email="cumulus13@gmail.com",
    url="https://github.com/cumulus13/gitignore",
    packages=[NAME],
    package_dir={NAME: NAME},
    include_package_data=True,
    install_requires=[
        "rich>=10.0.0",
        "licface",
        "rich_argparse"
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            f"gitign={NAME}.{NAME}:main",
            f"gitig={NAME}.{NAME}:main",
            f"{NAME}={NAME}.{NAME}:main",
        ]
    },
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)