"""
prompt.py — Modul Pembuatan Prompt dan Pembacaan Input
=======================================================
Modul ini menangani dua hal utama terkait interaksi pengguna:

1. Pembuatan String Prompt:
   Prompt adalah teks yang ditampilkan di sebelah kiri kursor saat shell
   menunggu input pengguna. PySh menampilkan prompt dalam format:
       [path/saat/ini] pysh>
   
   Untuk path yang terlalu panjang, modul ini secara otomatis mempersingkat
   tampilan menjadi format "[root/.../folder_terakhir] pysh>" agar prompt
   tetap ringkas dan tidak memenuhi layar.

2. Pembacaan Input yang Aman:
   Modul ini membungkus fungsi input() Python dengan penanganan error
   untuk dua kasus edge yang umum:
   - EOFError  : Terjadi ketika stdin ditutup (misalnya Ctrl+D di Linux).
   - UnicodeDecodeError : Terjadi jika pengguna mengirim karakter encoding
                          yang tidak valid ke shell.
"""

import os
from .colors import green, blue, cyan

# Template prompt shell
PROMPT = "pysh> "


def get_prompt() -> str:
    """
    Membuat string prompt yang informatif dan berwarna.

    Format prompt: [path_direktori] pysh>
    - Path ditampilkan dengan warna biru.
    - Teks 'pysh>' ditampilkan dengan warna cyan.
    - Jika path memiliki lebih dari 3 level kedalaman, path akan
      disingkat menjadi "root/.../folder_terakhir".

    Returns:
        String prompt yang siap ditampilkan ke pengguna.
    """
    try:
        cwd = os.getcwd()
    except OSError:
        cwd = "(unreachable)"

    parts = cwd.split(os.sep)
    if len(parts) > 3:
        # Singkat path panjang: "D:\a\b\c\d" → "D:\...\d"
        path_str = f"{parts[0]}{os.sep}...{os.sep}{parts[-1]}"
    else:
        path_str = cwd

    return f"[{blue(path_str)}] {cyan(PROMPT)}"


def read_input(prompt: str) -> str:
    """
    Membaca input dari pengguna dengan penanganan error yang aman.

    Args:
        prompt: String prompt yang akan ditampilkan sebelum kursor input.

    Returns:
        String input dari pengguna, atau:
        - "exit" jika stdin ditutup (EOFError / Ctrl+D).
        - String kosong jika terjadi error encoding.
    """
    try:
        return input(prompt)
    except EOFError:
        # Ctrl+D (Linux) atau stdin ditutup → keluar dari shell
        return "exit"
    except UnicodeDecodeError:
        print("\npysh: input mengandung karakter invalid")
        return ""
