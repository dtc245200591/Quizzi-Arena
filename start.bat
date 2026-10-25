@echo off
setlocal
cd /d "%~dp0"

where docker >nul 2>&1
if errorlevel 1 (
    echo Khong tim thay Docker. Hay cai Docker Desktop va mo ung dung truoc.
    pause
    exit /b 1
)

docker info >nul 2>&1
if errorlevel 1 (
    echo Docker Desktop chua san sang. Hay mo Docker Desktop, doi den khi Docker Engine chay roi thu lai.
    pause
    exit /b 1
)

if not exist ".env" copy ".env.example" ".env" >nul

echo Dang khoi dong Quizzi Arena...
docker compose up -d --build
if errorlevel 1 (
    echo Khong the khoi dong. Thu xem log bang lenh: docker compose logs
    pause
    exit /b 1
)

echo Quizzi Arena dang khoi dong tai https://localhost:8444
start "" "https://localhost:8444"
echo Dong cua so nay khong dung may chu. Bam stop.bat de tat Quizzi Arena.
pause
