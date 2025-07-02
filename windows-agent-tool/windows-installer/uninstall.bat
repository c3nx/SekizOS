@echo off
setlocal enabledelayedexpansion
title Windows Agent for Claude Code - Uninstaller
color 0C

echo.
echo ============================================================
echo    Windows Agent for Claude Code - Uninstaller
echo ============================================================
echo.
echo This will remove Windows Agent and all its configurations.
echo.
echo Press Ctrl+C to cancel or any key to continue...
pause >nul

:: Check if running as admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Administrator privileges required!
    echo.
    echo Please right-click on uninstall.bat and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

:: Stop the agent
echo [1/5] Stopping Windows Agent...
taskkill /f /im python.exe /fi "WINDOWTITLE eq *Windows Agent*" >nul 2>&1
taskkill /f /im pythonw.exe >nul 2>&1
timeout /t 2 >nul
echo [OK] Agent processes stopped
echo.

:: Remove Task Scheduler task
echo [2/5] Removing auto-start configuration...
schtasks /delete /tn "ClaudeWindowsAgent" /f >nul 2>&1
echo [OK] Task Scheduler entry removed
echo.

:: Remove firewall rules
echo [3/5] Removing firewall rules...
netsh advfirewall firewall delete rule name="Claude Windows Agent" >nul 2>&1
netsh advfirewall firewall delete rule name="Claude Agent WSL" >nul 2>&1
echo [OK] Firewall rules removed
echo.

:: Remove agent info file
echo [4/5] Cleaning up configuration files...
if exist "%USERPROFILE%\.claude_agent_info" (
    del /f /q "%USERPROFILE%\.claude_agent_info" >nul 2>&1
    echo [OK] Agent info file removed
) else (
    echo [OK] No agent info file found
)
echo.

:: Uninstall Python packages (optional)
echo [5/5] Python packages...
echo.
echo Do you want to uninstall Python packages? (Y/N)
echo Note: Only choose Y if no other programs use these packages
choice /c YN /n
if %errorlevel% equ 1 (
    echo Uninstalling Python packages...
    python -m pip uninstall -y -r requirements.txt >nul 2>&1
    echo [OK] Python packages uninstalled
) else (
    echo [SKIP] Python packages kept
)
echo.

:: Final message
echo ============================================================
echo    Uninstallation Complete!
echo ============================================================
echo.
echo Windows Agent has been removed from your system.
echo.
echo You can safely delete this folder:
echo %CD%
echo.
pause