@echo off
REM ============================================================
REM  run_tests.bat — Script Eksekusi Test Suite PySh (1-Klik)
REM ============================================================
REM  Script ini menjalankan seluruh unit test yang ada di folder
REM  tests/ menggunakan framework pytest dalam mode verbose (-v),
REM  sehingga setiap test case ditampilkan secara individual
REM  beserta status PASSED/FAILED-nya.
REM
REM  Cara Penggunaan:
REM    1. Klik dua kali file ini di Windows Explorer, ATAU
REM    2. Jalankan dari terminal: .\run_tests.bat
REM
REM  Catatan Teknis:
REM    - PYTHONPATH=. diperlukan agar pytest dapat menemukan
REM      modul 'core' yang berada di direktori root proyek.
REM ============================================================
echo ==========================================================
echo           PySh Automated QA Test Suite (Fase 8)
echo ==========================================================
set PYTHONPATH=.
pytest tests/ -v
echo.
echo Test Run Complete! Tekan tombol apapun untuk keluar...
pause >nul
