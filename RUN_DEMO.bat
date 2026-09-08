@echo off
cd /d %~dp0
if not exist web\dist\index.html (
  echo web\dist is missing. Run: cd web ^&^& npm run build
  pause
  exit /b 1
)
REM Fail fast and say why, instead of starting a server that cannot come up and then
REM waiting out the 30-second poll before admitting it.
python --version >nul 2>&1
if errorlevel 1 (
  echo Python was not found on PATH. This script serves web\dist with Python's http.server.
  echo Install Python 3, or serve web\dist with any other static file server.
  pause
  exit /b 1
)
REM -b 127.0.0.1 binds to loopback only. Without it http.server listens on every interface,
REM which puts the demo on the venue wifi for anyone on the same network.
start "AGRIM demo server - close this window or press Ctrl+C to stop" python -m http.server 8080 -b 127.0.0.1 -d web\dist
echo Waiting for the server to start...
set tries=0
:wait
timeout /t 1 /nobreak >nul
set /a tries+=1
python -c "import socket,sys;sys.exit(0 if socket.socket().connect_ex(('127.0.0.1',8080))==0 else 1)"
if errorlevel 1 (
  if %tries% lss 30 goto wait
  echo Server did not start after 30 seconds. Check the server window for errors.
  pause
  exit /b 1
)
start "" http://localhost:8080/
