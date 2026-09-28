# -*- coding: utf-8 -*-
"""Setup script for the Call Center AI prediction project.

This script uses ``setuptools`` to package the Django project so it can be
installed with ``pip`` (e.g., ``pip install -e .``).  The ``install_requires``
list is populated from ``requirements.txt`` to keep the runtime dependencies
in sync with the development environment.
"""

import pathlib
from setuptools import find_packages, setup

# Path to the project root (the directory containing this ``setup.py``)
HERE = pathlib.Path(__file__).parent.resolve()

# Load the requirements from ``requirements.txt`` – ignore empty lines and comments
requirements_path = HERE / "requirements.txt"
if requirements_path.is_file():
    with requirements_path.open(encoding="utf-8") as f:
        install_requires = [
            line.strip()
            for line in f
            if line.strip() and not line.strip().startswith("#")
        ]
else:
    install_requires = []

setup(
    name="call_center_ai",
    version="0.1.0",
    description="Prediction of customer behaviour in call‑center systems",
    long_description=(HERE / "README.md").read_text(encoding="utf-8") if (HERE / "README.md").is_file() else "",
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="you@example.com",
    url="https://example.com/call_center_ai",
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Django",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
