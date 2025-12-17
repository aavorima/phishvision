@echo off
REM Start PhishVision with ngrok for QR code testing (Windows)

echo ============================================================
echo PhishVision - QR Code Testing with ngrok
echo ============================================================
echo.

REM Check if ngrok is installed
where ngrok >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: ngrok is not installed!
    echo Install it from: https://ngrok.com/download
    echo.
    pause
    exit /b 1
)

echo Starting ngrok tunnel on port 5000...
start "ngrok" cmd /k "ngrok http 5000"

echo.
echo Waiting for ngrok to start...
timeout /t 3 /nobreak >nul

echo.
echo Please check the ngrok window for your public URL
echo It will look like: https://abc123.ngrok.io
echo.
echo Copy that URL and set it as BASE_URL:
echo   set BASE_URL=https://abc123.ngrok.io
echo.
echo Or add it to your .env file:
echo   BASE_URL=https://abc123.ngrok.io
echo.
echo Press any key to start Flask app...
pause >nul

echo.
echo Starting Flask app...
python app.py

