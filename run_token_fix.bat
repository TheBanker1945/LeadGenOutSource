@echo off
REM Force fix all authentication tokens
REM Run this locally to test the fix before deploying to Render

echo ========================================
echo    EMERGENCY TOKEN FIX (LOCAL TEST)
echo ========================================
echo.

python force_fix_tokens.py

echo.
echo Press any key to exit...
pause >nul
