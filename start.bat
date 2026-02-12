@echo off
echo.
echo  🦞 OpenClaw GUI starten...
echo  ==========================
echo.
echo  Die Web-Oberflaeche oeffnet sich unter:
echo  http://127.0.0.1:5000
echo.
echo  Zum Beenden: Strg+C druecken
echo.

cd /d "%~dp0"
call venv\Scripts\activate.bat
python app.py
