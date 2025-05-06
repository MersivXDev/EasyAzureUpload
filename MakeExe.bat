@echo off
REM Activate the virtual environment
call venv\Scripts\activate.bat

pyinstaller --onefile --name EzAzureUploader --distpath EasyAzureUpload EasyAzureUpload\main.py

REM Pause so the window doesn't close immediately (optional)
pause