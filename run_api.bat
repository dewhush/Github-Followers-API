@echo off
title GitHub Followers API
cls
echo.
echo    _____ _ _   _           _       ______    _ _                            
echo   / ____(_) ^| ^| ^|         ^| ^|     ^|  ____^|  ^| ^| ^|                           
echo  ^| ^|  __ _^| ^|_^| ^|__  _   _^| ^|__   ^| ^|__ ___^| ^| ^| _____      _____ _ __ ___ 
echo  ^| ^| ^|_ ^| ^| __^| '_ \\^| ^| ^| ^| '_ \\  ^|  __/ _ \\^| ^| ^|/ _ \\ \\ /\\ / / _ \\ '__/ __^|
echo  ^| ^|__^| ^| ^| ^|_^| ^| ^| ^| ^|_^| ^| ^|_) ^| ^| ^| ^| (_) ^| ^| ^| (_) \\ V  V /  __/ ^|  \\__ \\
echo   \\_____|_^|\\__^|_^| ^|_^|\\__,_^|_.__/  ^|_^|  \\___/^|_^|_^|\\___/ \\_/\\_/ \\___^|_^|  ^|___/
echo.
echo                     Created by: dewhush
echo.
echo ============================================================
echo.

echo [INFO] Installing requirements...
pip install -r requirements.txt > nul 2>&1

echo [INFO] Starting API Server...
echo [INFO] Access Docs: http://127.0.0.1:8000/docs
echo.

uvicorn api:app --reload --host 0.0.0.0 --port 8000
pause
