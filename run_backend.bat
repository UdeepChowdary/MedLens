@echo off
echo ========================================================
echo Starting MedLens FastAPI Backend with PaddleOCR (Anaconda)
echo ========================================================

set PYTHON_EXE=C:\anaconda3\python.exe

if not exist "%PYTHON_EXE%" (
    echo [WARNING] C:\anaconda3\python.exe not found, falling back to python on PATH
    set PYTHON_EXE=python
)

"%PYTHON_EXE%" -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
