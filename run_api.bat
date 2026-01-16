@echo off
title GitHub Auto-Follow API
cls
echo.
echo    _____ _ _   _           _         _       _ 
echo   ^|  __ (_) ^| ^| ^|         ^| ^|       ^| ^|     ^| ^|
echo   ^| ^|  \/_^| ^|_^| ^|__  _   _^| ^|__     ^| ^| __ _^| ^|__   ___ 
echo   ^| ^| __^| ^| __^| '_ \^| ^| ^| ^| '_ \    ^| ^|/ _` ^| '_ \ / __^|
echo   ^| ^|_\ \ ^| ^|_^| ^| ^| ^| ^|_^| ^| ^|_) ^|   ^| ^| (_^| ^| ^|_) ^|\__ \
echo    \____/_^|\__^|_^| ^|_^|\__,_^|_.__/    ^|_^|\__,_^|_.__/ ^|___/
echo.
echo       Created by: dewhush
echo.
echo.

echo Installing requirements...
pip install -r requirements.txt > nul 2>&1

echo.
echo [INFO] Starting API Server...
echo [INFO] Access Docs at: http://127.0.0.1:8000/docs
echo.

uvicorn api:app --reload --host 0.0.0.0 --port 8000
pause
