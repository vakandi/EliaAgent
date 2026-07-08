@echo off
echo ========================================
echo YouTube Transcription Skill - Installation
echo ========================================
echo.

REM Vérifier si Python est installé
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Erreur: Python n'est pas installé ou non trouvé dans le PATH
    pause
    exit /b 1
)

echo Installation des dépendances Python...
pip install yt-dlp openai-whisper youtube-transcript-api requests

echo.
echo Création du fichier de configuration...
if not exist "config.json" (
    copy config.example.json config.json
    echo Fichier config.json créé. Veuillez l'éditer avec vos clés API.
) else (
    echo Fichier config.json existe déjà.
)

echo.
echo Installation terminée !
echo.
echo Prochaines étapes:
echo 1. Éditez config.json avec vos clés API
echo 2. Utilisez: python main.py --url "URL_YOUTUBE" --create-skill
echo.
pause