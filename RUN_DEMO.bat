@echo off
cd /d %~dp0
if not exist web\dist\index.html (
  echo web\dist is missing. Run: cd web ^&^& npm run build
  pause
  exit /b 1
)
start "" http://localhost:8080/
python -m http.server 8080 -d web\dist
