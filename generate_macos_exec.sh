#!/bin/bash 
pyinstaller --noconfirm --log-level=WARN \
--name "easicmd_gui" \
--distpath="./executable/macOS" \
--onefile \
--hidden-import=irods.auth.native \
--windowed \
--icon="screenshot/eic.ico" \
api_gui_easicmd.py
