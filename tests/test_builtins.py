"""
test_builtins.py — Unit Test untuk Modul Built-in Commands
===========================================================
File ini berisi pengujian otomatis untuk memverifikasi bahwa fungsi
is_builtin() di modul core/builtins.py dapat mengidentifikasi
perintah built-in dan perintah eksternal secara akurat.

Pengujian ini penting karena kesalahan identifikasi akan menyebabkan:
    - Perintah built-in (seperti cd) dieksekusi di child process,
      sehingga perubahan direktori tidak berdampak pada shell utama.
    - Perintah eksternal (seperti grep) dicoba dieksekusi sebagai
      built-in, yang akan menyebabkan error atau perilaku tak terduga.

Skenario yang Diuji:
    - 7 perintah built-in resmi (cd, pwd, ls, dir, history, help, exit).
    - 3 perintah eksternal (echo, grep, cat) yang TIDAK boleh dikenali
      sebagai built-in.
"""

import pytest
from core.builtins import is_builtin

@pytest.mark.parametrize("command, expected", [
    # Perintah yang HARUS dikenali sebagai built-in
    ("cd", True),
    ("pwd", True),
    ("ls", True),
    ("dir", True),
    ("history", True),
    ("help", True),
    ("exit", True),
    # Perintah yang TIDAK BOLEH dikenali sebagai built-in
    ("echo", False),
    ("grep", False),
    ("cat", False),
])
def test_is_builtin(command, expected):
    """
    Memverifikasi bahwa is_builtin() mengembalikan nilai boolean yang benar
    untuk setiap nama perintah yang diberikan.
    """
    assert is_builtin(command) == expected
