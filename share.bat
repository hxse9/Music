@echo off
chcp 65001 > nul
echo ==============================================
echo K-Music Hub 임시 인터넷 공유 (터널링) 스크립트
echo ==============================================
echo.
echo [주의] 이 스크립트를 실행하기 전에 반드시 start.bat으로
echo        로컬 서버가 켜져 있어야 합니다!
echo.
echo.
echo 서버 연결을 시도 중입니다...
echo 아래에서 "https://..." 로 시작하는 임시 주소가 생성되면
echo 그 주소를 복사해서 친구들에게 공유해주세요!
echo.
echo (참고: 이 검은 창을 닫으면 공유 연결도 함께 끊어집니다.)
echo --------------------------------------------------------
ssh -o StrictHostKeyChecking=no -R 80:localhost:5000 nokey@localhost.run
pause
