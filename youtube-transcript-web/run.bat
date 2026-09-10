@echo off
chcp 65001 > nul
echo ========================================================
echo   YouTube Audio & Transcript Web Service 시작
echo ========================================================
echo.

set PYTHON_EXE=C:\Users\KIM DONGJUN\miniconda3\envs\myenv\python.exe

if not exist "%PYTHON_EXE%" (
    set PYTHON_EXE=python
)

echo 브라우저에서 아래 주소로 접속하세요:
echo http://localhost:8000
echo.

"%PYTHON_EXE%" app.py

pause
