@echo off
echo Installing python-docx in virtual environment...
call venv\Scripts\activate.bat
pip install python-docx
echo.
echo Installation complete!
echo Please restart your Flask server.
pause
