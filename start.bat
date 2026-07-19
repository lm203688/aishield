@echo off
echo Starting AIShield API Server...
set PYTHONPATH=%~dp0
set AISHIELD_PORT=8450
set PYTHONUNBUFFERED=1
python -m api.server
pause