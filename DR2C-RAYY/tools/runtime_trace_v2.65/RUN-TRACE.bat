@echo off
setlocal
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Collect-DR2CTrace.ps1"
set TRACE_EXIT=%ERRORLEVEL%
echo.
if not "%TRACE_EXIT%"=="0" echo Trace failed. Read the error above and correct the stated issue.
if "%TRACE_EXIT%"=="0" echo Trace collector finished. Inspect the ZIP before sharing it.
pause
exit /b %TRACE_EXIT%
