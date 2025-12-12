@echo off
call venv\Scripts\activate.bat
uvicorn app.api.routes:app --host 127.0.0.1 --port 8000 --reload
