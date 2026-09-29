@echo off
title SMART ENTRY Launcher
color 0B

:menu
cls
echo ===================================================
echo               SMART ENTRY LAUNCHER
echo ===================================================
echo.
echo Please select an option:
echo.
echo   1. Start Server (Run this first!)
echo   2. Open Admin Dashboard
echo   3. Open Entry Camera Kiosk
echo   4. Open Exit Camera Kiosk
echo   5. Exit
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto server
if "%choice%"=="2" goto admin
if "%choice%"=="3" goto entry
if "%choice%"=="4" goto exitcam
if "%choice%"=="5" exit

echo.
echo Invalid choice! Please press 1, 2, 3, 4, or 5.
pause
goto menu

:server
echo Starting Server in a new window...
start cmd /k "title SMART ENTRY Server && python app.py"
goto menu

:admin
start http://localhost:5000/admin
goto menu

:entry
start http://localhost:5000/kiosk
goto menu

:exitcam
start http://localhost:5000/kiosk/exit
goto menu
