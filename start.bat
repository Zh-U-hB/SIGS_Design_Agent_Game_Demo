@echo off
chcp 65001 >nul

title SIGS - Start

set BACKEND_PORT=8888
set FRONTEND_PORT=3111
set PROJECT_DIR=%~dp0
set BACKEND_DIR=%PROJECT_DIR%backend
set FRONTEND_DIR=%PROJECT_DIR%frontend

echo.
echo  ========================================
echo    SIGS - Start Script
echo  ========================================
echo.

echo  [1/6] Checking ports...
call :kill_port %BACKEND_PORT%
call :kill_port %FRONTEND_PORT%
echo.

echo  [2/6] Checking environment...
where uv >nul 2>&1
if errorlevel 1 (
    echo     [ERROR] uv not found. Install: pip install uv
    pause
    exit /b 1
)
echo     [OK] uv

where node >nul 2>&1
if errorlevel 1 (
    echo     [ERROR] node not found. Install: https://nodejs.org/
    pause
    exit /b 1
)
echo     [OK] node
echo.

echo  [3/6] Installing dependencies...
if not exist "%BACKEND_DIR%\.venv" (
    echo     Installing backend deps...
    pushd "%BACKEND_DIR%"
    uv sync
    if errorlevel 1 (
        popd
        echo     [ERROR] Backend install failed
        pause
        exit /b 1
    )
    popd
    echo     [OK] Backend deps installed
) else (
    echo     [OK] Backend deps ready
)

if not exist "%FRONTEND_DIR%\node_modules" (
    echo     Installing frontend deps...
    pushd "%FRONTEND_DIR%"
    npm install
    if errorlevel 1 (
        popd
        echo     [ERROR] Frontend install failed
        pause
        exit /b 1
    )
    popd
    echo     [OK] Frontend deps installed
) else (
    echo     [OK] Frontend deps ready
)
echo.

echo  [4/6] Starting services...
start "SIGS Backend" cmd /k "cd /d %PROJECT_DIR% && set PYTHONPATH=%PROJECT_DIR% && cd backend && uv run uvicorn main:app --host 0.0.0.0 --port %BACKEND_PORT% --reload"
echo     [START] Backend  - http://localhost:%BACKEND_PORT%
echo.

echo  [5/5] Waiting for server to start...
timeout /t 3 /nobreak >nul

echo  [6/6] Opening browser...
start http://localhost:%BACKEND_PORT%/pages/landing.html
echo.

echo  ========================================
echo    Started!
echo  ----------------------------------------
echo    Frontend : http://localhost:%BACKEND_PORT%/pages/landing.html
echo    Explore  : http://localhost:%BACKEND_PORT%/pages/explore.html
echo    Backend  : http://localhost:%BACKEND_PORT%
echo    API Docs : http://localhost:%BACKEND_PORT%/docs
echo  ----------------------------------------
echo    Close this window will NOT stop the service.
echo    Close the terminal window to stop.
echo  ========================================
echo.
pause
goto :eof

:kill_port
set port=%~1
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":%port% " ^| findstr "LISTENING"') do (
    echo     [KILL] Port %port% occupied by PID %%a, killing...
    taskkill /PID %%a /F >nul 2>&1
    timeout /t 1 /nobreak >nul
)
echo     [OK] Port %port% free
goto :eof
