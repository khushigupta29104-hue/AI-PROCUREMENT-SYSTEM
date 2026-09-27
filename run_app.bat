@echo off
REM run_app.bat -- convenience launcher for Windows
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)
streamlit run frontend\app.py
