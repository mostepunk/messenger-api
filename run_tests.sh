#!/bin/bash
python3 -m virtualenv venv
source venv/bin/activate
pip install -r /requirements-dev.txt
pytest -vv
deactivate
rm -rf venv
