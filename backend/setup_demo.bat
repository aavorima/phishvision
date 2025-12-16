@echo off
echo ====================================
echo PhishVision Demo Data Setup
echo ====================================
echo.
echo This script will populate your database with demo data.
echo.
pause
echo.
echo Running demo data seeder...
python seed_demo_data.py
echo.
echo ====================================
echo Setup Complete!
echo ====================================
echo.
echo You can now start the backend with:
echo   python app.py
echo.
echo Demo Login:
echo   Username: demo
echo   Password: demo123
echo.
pause
