#!/bin/bash 
pyinstaller --noconfirm --log-level=WARN \
--name "easicmd_gui" \
--add-data="easy_irods_commands.wiki:." \
--distpath="./executable/linux" \
--onefile \
--hidden-import=irods.auth.native \
--windowed \
api_gui_easicmd.py
