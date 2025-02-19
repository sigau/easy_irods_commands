#!/bin/bash 
pyinstaller --noconfirm --log-level=WARN \
--name "easicmd_gui" \
--add-data="easy_irods_commands.wiki:." \
--distpath="./executable/macOS" \
--onefile \
--hidden-import=irods.auth.native \
--nowindow \
--icon="screenshot/eic.ico" \
api_gui_easicmd.py
