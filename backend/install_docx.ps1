Write-Host "Installing python-docx in virtual environment..." -ForegroundColor Cyan
& ".\venv\Scripts\python.exe" -m pip install python-docx
Write-Host ""
Write-Host "Installation complete!" -ForegroundColor Green
Write-Host "Please restart your Flask server." -ForegroundColor Yellow
