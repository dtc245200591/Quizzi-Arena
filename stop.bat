@echo off
setlocal
cd /d "%~dp0"

where docker >nul 2>&1
if errorlevel 1 (
    echo Khong tim thay Docker Desktop.
    pause
    exit /b 1
)

docker compose down
if errorlevel 1 (
    echo Khong the dung dich vu. Hay kiem tra Docker Desktop.
    pause
    exit /b 1
)

echo Da dung Quizzi Arena. Quiz va diem so van duoc luu lai.
pause
