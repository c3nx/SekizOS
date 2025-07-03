@echo off
setlocal enabledelayedexpansion
title Windows Agent for Claude Code - Installer v2.0
color 0A

echo.
echo ============================================================
echo    Windows Agent for Claude Code - Installer v2.0
echo ============================================================
echo.

:: Check if running as admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Administrator privileges required!
    echo.
    echo Please right-click on install.bat and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

:: Check Python installation
echo [1/7] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANT: Check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

python --version
echo [OK] Python found
echo.

:: Enable PowerShell script execution
echo [2/7] Configuring PowerShell execution policy...
powershell -Command "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force" >nul 2>&1
echo [OK] PowerShell execution policy configured
echo.

:: Install Python dependencies
echo [3/7] Installing Python dependencies...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)
echo [OK] Dependencies installed successfully
echo.

:: Configure Windows Firewall
echo [4/7] Configuring Windows Firewall...
:: Remove old rules
netsh advfirewall firewall delete rule name="Claude Windows Agent" >nul 2>&1
netsh advfirewall firewall delete rule name="Claude Agent WSL" >nul 2>&1
:: Add new rules
netsh advfirewall firewall add rule name="Claude Windows Agent" dir=in action=allow protocol=TCP localport=8765 profile=any >nul 2>&1
netsh advfirewall firewall add rule name="Claude Agent WSL" dir=in action=allow protocol=TCP localport=8765 remoteip=172.16.0.0/12,10.0.0.0/8,192.168.0.0/16 >nul 2>&1
echo [OK] Firewall rules configured for port 8765
echo.

:: Get Windows IP for WSL
echo [5/7] Detecting network configuration...
set WINDOWS_IP=Unknown
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4" ^| findstr /c:"192.168" /c:"172." /c:"10."') do (
    for /f "tokens=1" %%b in ("%%a") do (
        set WINDOWS_IP=%%b
        goto :found_ip
    )
)
:found_ip
echo Windows IP: %WINDOWS_IP%
echo.

:: Create startup script
echo [6/7] Creating startup configuration...
(
echo @echo off
echo cd /d "%CD%"
echo start /min pythonw windows_agent.py
) > start_agent.bat

:: Create visible startup script for testing
(
echo @echo off
echo cd /d "%CD%"
echo python windows_agent.py
echo pause
) > start_agent_visible.bat
echo [OK] Startup scripts created
echo.

:: Create Task Scheduler task
echo [7/7] Setting up auto-start with Task Scheduler...
:: Remove old task
schtasks /delete /tn "ClaudeWindowsAgent" /f >nul 2>&1
:: Create new task
schtasks /create /tn "ClaudeWindowsAgent" /tr "\"%CD%\start_agent.bat\"" /sc onlogon /rl highest /f >nul 2>&1
if %errorlevel% eq 0 (
    echo [OK] Auto-start configured successfully
) else (
    echo [WARNING] Could not configure auto-start
)
echo.

:: Test the agent
echo Starting Windows Agent...
start /min start_agent.bat
timeout /t 3 >nul

:: Test connection
echo Testing agent connection...
curl -s -H "Authorization: Bearer claude-agent-2024" http://localhost:8765/health >nul 2>&1
if %errorlevel% eq 0 (
    echo [OK] Agent is running and responding!
) else (
    echo [WARNING] Agent may need a moment to start
)
echo.

:: Display success message
echo ============================================================
echo    Installation Complete!
echo ============================================================
echo.
echo Agent Status: Running on port 8765
echo.
echo Access from WSL: http://%WINDOWS_IP%:8765
echo Local access: http://localhost:8765
echo.
echo The agent will start automatically when Windows starts.
echo.
echo To test manually: Run start_agent_visible.bat
echo To uninstall: Run uninstall.bat
echo.
echo Agent info saved to: %USERPROFILE%\.claude_agent_info
echo.
pause