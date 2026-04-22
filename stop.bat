@echo off
chcp 65001 >nul

title SIGS - Stop

echo.
echo  ========================================
echo    SIGS - Stop All Services
echo  ========================================
echo.

call :kill_port 8888 "Backend"
call :kill_port 3111 "Frontend"

echo.
echo  All services stopped.
echo.
pause
goto :eof

:kill_port
set port=%~1
set label=%~2
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":%port% " ^| findstr "LISTENING"') do (
    echo     [KILL] %label% port %port% - PID %%a
    taskkill /PID %%a /F >nul 2>&1
)
echo     [OK] Port %port%
goto :eof
