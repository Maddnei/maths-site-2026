@echo off
chcp 65001 > nul
title Site Maths & Sciences 2026 - M. Gimenez

echo ============================================================
echo   Lancement du site Maths & Sciences 2026 - M. Gimenez
echo ============================================================
echo.

cd /d "%~dp0"

echo [1/2] Verification des dependances Python...
python -m pip install -r requirements.txt --quiet

echo [2/2] Demarrage du serveur web local...
echo.
echo Le site est accessible sur : http://localhost:5000
echo Identifiants Professeur : dgimenez / Cadolive+2406
echo.
echo Pour arreter le serveur, fermez simplement cette fenetre.
echo ============================================================
echo.

start http://localhost:5000

python app.py
pause
