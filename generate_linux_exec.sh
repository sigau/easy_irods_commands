#!/bin/bash 
pyinstaller --noconfirm --log-level=WARN \
--name "easicmd_gui" \
--distpath="./executable/linux" \
--onefile \
--hidden-import=irods.auth.native \
--windowed \
api_gui_easicmd.py
