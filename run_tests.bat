@echo off
echo ==========================================================
echo           PySh Automated QA Test Suite (Fase 8)
echo ==========================================================
set PYTHONPATH=.
pytest tests/ -v
echo.
echo Test Run Complete! Tekan tombol apapun untuk keluar...
pause >nul
