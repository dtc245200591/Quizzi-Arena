@echo off
setlocal
cd /d "%~dp0"

echo Tao tai khoan quan tri Quizzi Arena. Hay nhap ten dang nhap, email va mat khau theo huong dan.
docker compose exec app python manage.py createsuperuser
if errorlevel 1 (
    echo Dam bao Quizzi Arena dang chay bang start.bat truoc.
    pause
    exit /b 1
)

echo Da tao tai khoan. Dang nhap tai https://localhost:8444/staff/login/
pause
