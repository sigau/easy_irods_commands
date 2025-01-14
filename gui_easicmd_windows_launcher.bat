@echo off

:: Author: Gautier Debaecker
:: Date: October 2024
:: Copyright (c) 2024 by Gautier Debaecker
:: Special thanks to Beyoncé for the inspiration
:: GitHub: https://github.com/sigau
:: License: MIT License

REM Chemin vers l'environnement virtuel
set ENV_PATH=env_easicmd

REM Vérifie si l'environnement virtuel existe
if not exist "%ENV_PATH%" (
    echo Environnement virtuel non trouvé. Création en cours...
    
    REM Crée un nouvel environnement virtuel
    python -m venv "%ENV_PATH%"

    REM Activez l'environnement virtuel
    call "%ENV_PATH%\Scripts\activate.ps1"

    REM Installez les dépendances à partir du fichier requirements.txt
    pip install -r requirements.txt
)

REM Activez l'environnement virtuel
call "%ENV_PATH%\Scripts\activate.ps1"

REM Exécutez le script Python
python api_gui_easicmd.py

PAUSE

REM Désactivez l'environnement virtuel (optionnel)
call "%ENV_PATH%\Scripts\deactivate"
