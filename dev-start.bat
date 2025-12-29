@echo off
echo Starting Lift Backend Development Server...
call .venv\Scripts\activate
uvicorn app.main:app --reload
pause
