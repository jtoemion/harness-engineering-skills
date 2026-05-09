@echo off
setlocal

REM Antigravity Mode Detector
REM Returns QUICK or FULL based on .memory/ directory existence
REM Usage: call detect-mode.bat from project root

if exist ".memory\" (
    echo FULL
) else if exist ".memory" (
    echo FULL
) else if exist ".memory\activeContext.md" (
    echo FULL
) else (
    echo QUICK
)

endlocal