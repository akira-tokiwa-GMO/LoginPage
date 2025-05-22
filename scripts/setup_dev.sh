#!/usr/bin/env bash
# Install development dependencies including flake8 and pytest
python -m pip install --upgrade pip
pip install -e .[dev]
