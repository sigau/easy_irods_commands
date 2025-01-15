# EASy-Irods-CoMmanDs (easicmd)
<!--docker run --entrypoint doctoc --rm -it -v $(pwd):/usr/src jorgeandrada/doctoc README.md --notitle -->

## Short description
Easicmd is a user-friendly Python script that provides a graphical interface for interacting with irods. It simplifies the usage of icommands by generating intuitive commands, making it ideal for new users or individuals who prefer a graphical interface over the command line. With Easicmd, you can effortlessly perform common tasks such as uploading and downloading data from irods, creating directories, managing metadata, searching for data by name or metadata, and retrieving essential information like directory size. Additionally, it streamlines the process of sharing data access with other users or groups. Enjoy a hassle-free irods experience with Easicmd!

# Install 
## Get the script
You can clone the reposatory with the following command 
```
git clone https://github.com/sigau/easy_irods_commands.git
```
## Dependancies

- **tkinter** (Linux : sudo apt-get install python3-tk | windows : during the installation process of Python ensure that you select the option to install Tcl/Tk and Tkinter  )
- **git** (https://git-scm.com/)

All the other dependencies are listed in the requirements.txt file.

You can also create a python virtualenv with the following command line (on windows it will be create when using the .bat):
```
cd easy_irods_commands
python -m venv env_easicmd
source env_easicmd/bin/activate
pip install -r requirements.txt
```
This will create a virtualenv with all the dependencies installed and not interact with your main environement/installation

**For Windows users** : You can double click on **gui_easicmd_windows_launcher.bat** it will create the virtual environement and run the graphical version of easicmd using the api. You now have a clikable launcher for the graphical version of easicmd.(It's possible that when you double click on the bat it open notepad, you need to associate the opening of a .ps1 file with powershell or just close the notepad, which will trigger execution of the script ).

# Run the script 
## Command line or graphical user interface (GUI)
- ./api_easicmd.py --> run the command line version
- ./api_gui_easicmd.py --> launch the GUI version

## First time running api_easicmd.py or api_gui_easicmd.py
**Fill in the irods configuration info** : 
The first time you run the script it will ask you to fill in the iRODS configuration information (host, port, user, zone) and the script will save it in a \~/.easicmd_config/.easicmd.info file. It will also ask you for your password, which can be saved (and encrypted) with a local key (\~/.easicmd_config/.easicmd.psw and \~/.easicmd_config/.easicmd.key) so that you can use it later without having to retype it (as icommands do) or not remember it and have to retype it each time you run the script. 

# Requirements
## Requirements for api_easicmd.py and api_gui_easicmd.py
The api_easicmd.py and api_gui_easicmd.py scripts represent updated versions that no longer rely on icommands. They are built upon the iRODS Python API, eliminating the necessity to adjust icommand clients when the server undergoes an iRODS version update. These upgraded scripts are compatible with Linux, Mac, and Windows operating systems.


# wiki 
For more details or help on how to use the script and its various functions, you can have a look at the project's [wiki section](../../wiki). 