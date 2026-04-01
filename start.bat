@echo off
chcp 65001 > nul
echo ==============================================
echo K-Music Hub 서버 시작 스크립트
echo ==============================================
echo.
echo 1. Flask 라이브러리를 설치 확인 중입니다...
python -m pip install flask > nul 2>&1
if %errorlevel% neq 0 (
    py -m pip install flask > nul 2>&1
)

echo.
echo 2. 로컬 서버(app.py)를 구동합니다...
echo 잠시 후 브라우저가 열리면 서버 화면을 보실 수 있습니다.
echo (이 검은 창을 끄면 서버도 같이 꺼집니다!)
echo.

:: 브라우저 자동 띄우기 (조금 기다렸다가 열기 위해 비동기로 호출)
start http://localhost:5000

:: 서버 실행
python app.py
if %errorlevel% neq 0 (
    py app.py
)

pause
