@echo off
cd /d C:\Users\Lenovo\Downloads\elt-pipeline
docker start pg >nul 2>&1
timeout /t 5 >nul
echo ===== %date% %time% ===== >> pipeline.log
C:\Users\Lenovo\venv\Scripts\python.exe pipeline.py >> pipeline.log 2>&1
echo exit code: %errorlevel% >> pipeline.log