@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0RUN_ALL.ps1"
exit /b %errorlevel%
